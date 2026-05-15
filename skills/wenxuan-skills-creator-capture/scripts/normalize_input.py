from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

for candidate in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
    if (candidate / "env_utils.py").exists():
        BOOTSTRAP_ROOT = candidate
        break
else:
    BOOTSTRAP_ROOT = Path(__file__).resolve().parents[3]

if str(BOOTSTRAP_ROOT) not in sys.path:
    sys.path.insert(0, str(BOOTSTRAP_ROOT))

from env_utils import get_wenxuan_output_dir
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from schemas import (  # noqa: E402
    AccountProfile,
    AuthorRef,
    CaptureBundle,
    CaptureMeta,
    CommentSignal,
    Completeness,
    ContactMethod,
    FailedProvider,
    MetricSet,
    MonetizationClue,
    PostItem,
    TrafficHook,
    VisualAsset,
)


CTA_RULES: list[tuple[str, str]] = [
    ("follow_prompt", r"关注|点个关注|主页看看"),
    ("save_prompt", r"收藏|建议存下|先码住|记得保存"),
    ("comment_prompt", r"评论区|留言|扣1|打在公屏|告诉我"),
    ("private_domain_prompt", r"私信|主页|微信|v信|vx|群|领取|进群|加我"),
]

MONETIZATION_RULES: list[tuple[str, str]] = [
    ("course", r"课程|训练营|陪跑|社群"),
    ("consulting", r"咨询|答疑|1v1|一对一"),
    ("product", r"链接|商品|店铺|下单|购买"),
    ("private_domain", r"私信|微信|vx|v信|公众号|主页"),
]

CONTACT_PATTERNS: list[tuple[str, str]] = [
    ("wechat", r"(?:vx|v信|微信)[:：]?\s*([A-Za-z0-9_-]{4,})"),
    ("xiaohongshu", r"小红书号[:：]?\s*([A-Za-z0-9_-]{4,})"),
    ("email", r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"),
]


def text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = text(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def first_non_empty(*values: Any) -> str:
    for value in values:
        normalized = text(value)
        if normalized:
            return normalized
    return ""


def extract_first_line(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def unix_to_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=UTC)
    except (TypeError, ValueError, OSError):
        return None


def safe_url(value: Any) -> str | None:
    candidate = text(value)
    if not candidate:
        return None
    parsed = urlparse(candidate)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return candidate
    return None


def parse_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def detect_format(payload: dict[str, Any]) -> str:
    meta = payload.get("meta") or {}
    endpoint = text(meta.get("list_endpoint"))
    if "xiaohongshu" in endpoint and "get_user_posted_notes" in endpoint:
        return "xhs_account_posts_export"
    if isinstance(payload.get("items"), list) and payload.get("meta"):
        return "generic_capture_bundle_like"
    return "unknown"


def get_xhs_detail_note(item: dict[str, Any]) -> dict[str, Any]:
    detail = item.get("detail") or {}
    data = detail.get("data") or {}
    nested = data.get("data") or []
    if not nested:
        return {}
    first = nested[0] or {}
    note_list = first.get("note_list") or []
    if not note_list:
        return {}
    return note_list[0] or {}


def get_xhs_root_user(payload: dict[str, Any]) -> dict[str, Any]:
    for item in payload.get("items") or []:
        note = get_xhs_detail_note(item)
        user = note.get("user") or {}
        if user:
            return user
        list_user = (item.get("list_item") or {}).get("user") or {}
        if list_user:
            return list_user
    return {}


def build_contact_methods(*texts: str) -> list[ContactMethod]:
    found: list[ContactMethod] = []
    joined = "\n".join(texts)
    for contact_type, pattern in CONTACT_PATTERNS:
        for match in re.finditer(pattern, joined, flags=re.IGNORECASE):
            value = text(match.group(1))
            if value:
                found.append(ContactMethod(type=contact_type, value=value))
    deduped: dict[tuple[str, str], ContactMethod] = {}
    for item in found:
        deduped[(item.type, item.value)] = item
    return list(deduped.values())


def collect_hashtags(note: dict[str, Any], fallback_desc: str) -> list[str]:
    tags: list[str] = []
    for tag in note.get("hash_tag") or []:
        name = text(tag.get("name"))
        if name:
            tags.append(name)
    for topic in note.get("topics") or []:
        name = text(topic.get("name"))
        if name:
            tags.append(name)
    for match in re.findall(r"#([^#\[\]\n]+)", fallback_desc):
        tags.append(match.replace("[话题]", "").strip())
    return unique(tags)


def build_media_urls(note: dict[str, Any], list_item: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    for source in (note.get("images_list") or []) + (list_item.get("images_list") or []):
        if not isinstance(source, dict):
            continue
        for key in ("url_size_large", "url", "original"):
            candidate = safe_url(source.get(key))
            if candidate:
                urls.append(candidate)
    return unique(urls)


def guess_layout(media_count: int, body: str) -> str:
    if media_count >= 7:
        return "dense_multi_page_carousel"
    if media_count >= 3:
        return "multi_page_carousel"
    if "图1" in body or "图 1" in body:
        return "annotated_slide_series"
    if media_count == 1:
        return "single_cover_card"
    return "unknown"


def guess_visual_notes(note: dict[str, Any], body: str) -> str:
    parts: list[str] = []
    if "图1" in body or "图 1" in body:
        parts.append("body references page-by-page explanation")
    if note.get("has_music"):
        parts.append("contains music")
    return "; ".join(parts)


def detect_signals(posts: list[PostItem], rules: list[tuple[str, str]], clue_class: type[TrafficHook] | type[MonetizationClue]) -> list[Any]:
    counter: Counter[tuple[str, str]] = Counter()
    examples: dict[tuple[str, str], str] = {}

    for post in posts:
        combined = "\n".join([post.title, post.body, post.cover_text])
        for clue_type, pattern in rules:
            if re.search(pattern, combined, flags=re.IGNORECASE):
                matched = re.search(pattern, combined, flags=re.IGNORECASE)
                clue_text = matched.group(0) if matched else clue_type
                key = (clue_type, clue_text)
                counter[key] += 1
                examples.setdefault(key, post.post_id)

    results: list[Any] = []
    for (clue_type, clue_text), count in counter.most_common():
        frequency = f"{count}/{len(posts)} posts"
        if clue_class is TrafficHook:
            destination = "private_domain" if clue_type == "private_domain_prompt" else "in_post_engagement"
            confidence = "observed" if count >= 2 else "inferred"
            results.append(TrafficHook(hook_type=clue_type, hook_text=clue_text, destination=destination, confidence=confidence))
        else:
            destination = "private_domain" if clue_type == "private_domain" else "on_platform"
            confidence = "observed" if count >= 2 else "inferred"
            results.append(MonetizationClue(clue_type=clue_type, clue_text=f"{clue_text} ({frequency})", destination=destination, confidence=confidence))
    return results


def build_comment_signals(posts: list[PostItem]) -> list[CommentSignal]:
    comment_counts = [post.metrics.comments or 0 for post in posts]
    if not comment_counts:
        return []
    active = sum(1 for count in comment_counts if count > 0)
    peak = max(comment_counts)
    average = round(sum(comment_counts) / len(comment_counts), 2)
    return [
        CommentSignal(
            signal_type="comment_activity",
            signal_text=f"{active}/{len(posts)} posts have visible comment counts; average={average}, peak={peak}",
            frequency_hint="derived_from_visible_metrics_only",
            representative_examples=[post.post_id for post in sorted(posts, key=lambda item: item.metrics.comments or 0, reverse=True)[:3]],
        )
    ]


def derive_completeness(payload: dict[str, Any], posts: list[PostItem], profile: AccountProfile | None) -> Completeness:
    has_profile = profile is not None
    has_posts = bool(posts)
    has_rich_details = any(post.body and post.media_urls for post in posts)
    has_profile_depth = bool(profile and (profile.bio or profile.follower_count or profile.contact_methods))

    if has_profile and has_posts and has_rich_details and has_profile_depth:
        return "high"
    if has_profile and has_posts:
        return "partial"
    return "low"


def normalize_xhs_account_export(payload: dict[str, Any], *, source_path: Path) -> CaptureBundle:
    meta = payload.get("meta") or {}
    root_user = get_xhs_root_user(payload)
    profile_url = safe_url(meta.get("profile_url"))
    user_id = first_non_empty(root_user.get("userid"), root_user.get("id"), meta.get("user_id"))
    red_id = first_non_empty(root_user.get("red_id"))
    display_name = first_non_empty(root_user.get("nickname"), root_user.get("name"), user_id)

    profile = AccountProfile(
        platform="xhs",
        display_name=display_name,
        handle=first_non_empty(red_id, user_id),
        bio="",
        profile_url=profile_url,
        avatar_url=safe_url(root_user.get("image") or root_user.get("images")),
        verified=bool(root_user.get("red_official_verified") or root_user.get("show_red_official_verify_icon") or (root_user.get("red_official_verify_type") or 0) > 0),
        aliases=unique([user_id, red_id]),
        external_links=[],
        contact_methods=build_contact_methods(""),
        discovered_from=unique(
            [
                text(meta.get("list_endpoint")),
                text(meta.get("detail_endpoint")),
                profile_url or "",
            ]
        ),
    )

    posts: list[PostItem] = []
    visual_assets: list[VisualAsset] = []

    for item in payload.get("items") or []:
        list_item = item.get("list_item") or {}
        note = get_xhs_detail_note(item)
        body = first_non_empty(note.get("desc"), list_item.get("desc"))
        source_url = safe_url((note.get("share_info") or {}).get("link"))
        media_urls = build_media_urls(note, list_item)
        hashtags = collect_hashtags(note, body)
        list_user = list_item.get("user") or {}
        note_user = note.get("user") or {}

        post = PostItem(
            platform="xhs",
            post_id=first_non_empty(item.get("note_id"), note.get("id"), list_item.get("id")),
            post_type=first_non_empty(note.get("type"), list_item.get("type"), "image_note"),
            title=first_non_empty(note.get("title"), item.get("title"), list_item.get("title")),
            subtitle="",
            cover_text=first_non_empty(list_item.get("display_title")),
            first_sentence=extract_first_line(body),
            body=body,
            transcript="",
            published_at=unix_to_datetime(first_non_empty(item.get("publish_time"), note.get("time"), list_item.get("create_time"))),
            source_url=source_url,
            media_urls=media_urls,
            hashtags=hashtags,
            metrics=MetricSet(
                views=note.get("view_count") or list_item.get("view_count"),
                likes=note.get("liked_count") or list_item.get("likes"),
                comments=note.get("comments_count") or list_item.get("comments_count"),
                shares=note.get("shared_count") or list_item.get("share_count"),
                saves=note.get("collected_count") or list_item.get("collected_count"),
                favorites=list_item.get("collected_count"),
            ),
            author=AuthorRef(
                platform="xhs",
                display_name=first_non_empty(note_user.get("nickname"), note_user.get("name"), list_user.get("nickname"), display_name),
                handle=first_non_empty(note_user.get("red_id"), note_user.get("userid"), list_user.get("userid"), profile.handle),
                profile_url=profile_url,
                verified=profile.verified,
            ),
            metadata={
                "capture_index": item.get("capture_index"),
                "status": item.get("status"),
                "sticky": bool(note.get("sticky") or list_item.get("sticky")),
                "ip_location": text(note.get("ip_location")),
                "topics": hashtags,
                "language": text(note.get("text_language_code")),
                "raw_user_id": first_non_empty(note_user.get("id"), list_user.get("userid"), user_id),
                "source_path": str(source_path),
            },
        )
        posts.append(post)

        visual_assets.append(
            VisualAsset(
                asset_type="image_post_gallery",
                source_url=media_urls[0] if media_urls else source_url,
                dominant_colors=[],
                layout_guess=guess_layout(len(media_urls), body),
                typography_guess="text-heavy educational card",
                decorative_elements=unique(
                    [
                        "emoji_prefix" if re.search(r"[^\w\s]", post.title) else "",
                        "multi_page_sequence" if len(media_urls) >= 3 else "",
                        "topic_hashtags" if hashtags else "",
                    ]
                ),
                visual_notes=guess_visual_notes(note, body),
                related_post_id=post.post_id,
            )
        )

    traffic_hooks = detect_signals(posts, CTA_RULES, TrafficHook)
    monetization_clues = detect_signals(posts, MONETIZATION_RULES, MonetizationClue)
    comment_signals = build_comment_signals(posts)

    attempted_providers = unique(
        [
            "tikhub_xhs_app_v2",
            text(meta.get("list_endpoint")),
            text(meta.get("detail_endpoint")),
        ]
    )
    failed_providers = [
        FailedProvider(provider="detail_errors", error=f"{len(payload.get('detail_errors') or [])} detail errors recorded")
        for _ in [0]
        if payload.get("detail_errors")
    ]

    completeness = derive_completeness(payload, posts, profile)
    notes = [
        f"detected_format=xhs_account_posts_export",
        f"requested_limit={meta.get('requested_limit')}",
        f"fetched_ok_count={meta.get('fetched_ok_count')}",
        "profile-level bio/follower stats were not present in this export",
        "comment_signals are derived from visible metrics, not raw comment content",
    ]

    return CaptureBundle(
        query=first_non_empty(display_name, user_id, profile_url),
        task_type="creator_capture",
        platform_hint="xhs",
        creator_hint=display_name,
        success=bool(posts),
        account_profile=profile,
        posts=posts,
        visual_assets=visual_assets,
        comment_signals=comment_signals,
        traffic_hooks=traffic_hooks,
        monetization_clues=monetization_clues,
        related_links=unique([profile_url or ""] + [text(post.source_url) for post in posts if post.source_url]),
        capture_meta=CaptureMeta(
            attempted_providers=attempted_providers,
            failed_providers=failed_providers,
            captured_count=len(posts),
            captured_at=datetime.now(tz=UTC),
            completeness=completeness,
            notes=" | ".join(notes),
        ),
        error=None if posts else "No posts extracted from payload.",
    )


def normalize_payload(payload: dict[str, Any], *, source_path: Path) -> CaptureBundle:
    detected = detect_format(payload)
    if detected == "xhs_account_posts_export":
        return normalize_xhs_account_export(payload, source_path=source_path)
    raise ValueError(f"Unsupported input format: {detected}")


def get_default_output_path(input_path: Path) -> Path:
    output_dir = get_wenxuan_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{input_path.stem}.capture-bundle.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize creator capture exports into CaptureBundle.")
    parser.add_argument("input_path", help="Path to raw creator JSON export.")
    parser.add_argument("-o", "--output", help="Optional path to write normalized CaptureBundle JSON. Defaults to ./wenxuan-output/<input>.capture-bundle.json")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--print-summary", action="store_true", help="Print a compact summary instead of full JSON.")
    args = parser.parse_args()

    input_path = Path(args.input_path).expanduser().resolve()
    payload = parse_json(input_path)
    bundle = normalize_payload(payload, source_path=input_path)

    if args.print_summary:
        summary = {
            "query": bundle.query,
            "creator": bundle.creator_hint,
            "platform": bundle.platform_hint,
            "posts": len(bundle.posts),
            "visual_assets": len(bundle.visual_assets),
            "traffic_hooks": [hook.model_dump() for hook in bundle.traffic_hooks],
            "monetization_clues": [clue.model_dump() for clue in bundle.monetization_clues],
            "completeness": bundle.capture_meta.completeness,
        }
        output_text = json.dumps(summary, ensure_ascii=False, indent=2 if args.pretty else None)
    else:
        output_text = bundle.model_dump_json(indent=2 if args.pretty else None, ensure_ascii=False)

    output_path = Path(args.output).expanduser().resolve() if args.output else get_default_output_path(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text, encoding="utf-8")
    print(str(output_path))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
