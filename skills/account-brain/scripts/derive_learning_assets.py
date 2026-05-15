from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CAPTURE_SCHEMA_PATH = ROOT.parent / "creator-capture" / "scripts" / "schemas.py"
ACCOUNT_BRAIN_SCHEMA_PATH = ROOT / "schemas" / "models.py"


def load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


capture_schemas = load_module("creator_capture_schemas_for_learning", CAPTURE_SCHEMA_PATH)
brain_models = load_module("account_brain_models_for_learning", ACCOUNT_BRAIN_SCHEMA_PATH)


STOPWORDS = {
    "话题",
    "新手",
    "必看",
    "入门",
    "大全",
    "核心",
    "教程",
    "保姆级",
    "超详细",
    "一篇",
    "搞懂",
    "速查",
    "手册",
    "全解",
    "揭秘",
    "整理",
    "分享",
    "合集",
    "公式",
    "技巧",
    "步骤",
    "指南",
    "图解",
    "全篇",
    "一次",
    "秒懂",
    "全套",
    "完整",
    "方法",
    "内容",
    "知识",
    "学习",
    "The",
    "the",
    "And",
    "and",
}


TEMPLATE_RULES = [
    ("新手必看型", [r"新手", r"小白", r"0基础", r"零基础", r"入门"]),
    ("保姆级步骤型", [r"保姆级", r"一步一步", r"步骤", r"流程", r"教程"]),
    ("大全速查型", [r"大全", r"速查", r"核心手册", r"对照", r"一查就懂"]),
    ("逆位/反面公式型", [r"逆位", r"公式", r"反面", r"万能", r"拆解"]),
    ("关系模式型", [r"爱情", r"感情", r"关系", r"恋爱", r"模式"]),
]


def text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def load_capture_bundle(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    return capture_schemas.CaptureBundle.model_validate(payload)


def split_terms(text_value: str) -> list[str]:
    terms = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]{2,8}", text_value)
    cleaned: list[str] = []
    for term in terms:
        term = term.strip().strip("｜|:：,，。.!！?？()（）[]【】<>《》")
        if not term or term in STOPWORDS:
            continue
        if len(term) <= 1:
            continue
        if term.isascii() and len(term) <= 4:
            continue
        cleaned.append(term)
    return cleaned


def get_all_post_texts(bundle: Any) -> list[str]:
    texts: list[str] = []
    for post in bundle.posts:
        texts.extend([text(post.title), text(post.body), text(post.cover_text), text(post.first_sentence)])
        texts.extend([text(tag) for tag in post.hashtags])
    return [value for value in texts if value]


def get_visual_reference_texts(bundle: Any) -> list[str]:
    texts: list[str] = []
    for asset in bundle.visual_assets:
        texts.extend([text(asset.layout_guess), text(asset.typography_guess), text(asset.visual_notes)])
        texts.extend([text(item) for item in asset.decorative_elements])
    return [value for value in texts if value]


def infer_templates(posts: list[Any]) -> list[str]:
    counts: Counter[str] = Counter()
    for post in posts:
        corpus = " ".join([text(post.title), text(post.body), text(post.cover_text), text(post.first_sentence)])
        for template_name, patterns in TEMPLATE_RULES:
            if any(re.search(pattern, corpus) for pattern in patterns):
                counts[template_name] += 1
    return [f"{name} ({count})" for name, count in counts.most_common()]


def infer_topic_clusters(posts: list[Any], top_terms: list[str]) -> list[str]:
    clusters: list[str] = []
    for term in top_terms[:12]:
        hits = []
        for post in posts:
            corpus = " ".join([text(post.title), text(post.body), text(post.cover_text)] + [text(tag) for tag in post.hashtags])
            if term in corpus:
                hits.append(post.title)
        if hits:
            clusters.append(f"{term} -> {len(hits)} posts")
    return clusters


def infer_question_space(top_terms: list[str]) -> list[str]:
    prompts = [f"{term} 是什么？" for term in top_terms[:8]]
    prompts.extend([f"{term} 怎么入门？" for term in top_terms[:4]])
    return unique(prompts)


def infer_reusable_explanations(posts: list[Any]) -> list[str]:
    ordered = sorted(posts, key=lambda post: (post.metrics.likes or 0, post.metrics.saves or 0), reverse=True)
    excerpts: list[str] = []
    for post in ordered[:8]:
        source = text(post.first_sentence) or text(post.body).splitlines()[0]
        if source:
            excerpts.append(source[:120])
    return unique(excerpts)


def infer_cross_domain_mappings(posts: list[Any]) -> list[str]:
    themes = {
        "情感": ["爱情", "感情", "恋爱", "关系"],
        "事业": ["事业", "工作", "职场", "职业"],
        "成长": ["新手", "入门", "学习", "成长"],
        "决策": ["选择", "判断", "决断", "路线"],
    }
    mappings: list[str] = []
    corpus = " ".join([text(post.title) + " " + text(post.body) for post in posts])
    for theme, keywords in themes.items():
        if any(keyword in corpus for keyword in keywords):
            mappings.append(theme)
    return unique(mappings)


def infer_knowledge_domains(top_terms: list[str]) -> list[str]:
    return top_terms[:12]


def infer_visual_style(bundle: Any) -> tuple[str, str, list[str], list[str], list[str], list[str], str, str, str]:
    layout_counter: Counter[str] = Counter()
    typography_counter: Counter[str] = Counter()
    decorative_counter: Counter[str] = Counter()
    reference_images: list[str] = []
    prompt_seed_parts: list[str] = []

    for asset in bundle.visual_assets:
        if asset.layout_guess:
            layout_counter[asset.layout_guess] += 1
        if asset.typography_guess:
            typography_counter[asset.typography_guess] += 1
        for item in asset.decorative_elements:
            if item:
                decorative_counter[item] += 1
        if asset.source_url:
            reference_images.append(str(asset.source_url))
        if asset.visual_notes and asset.visual_notes != "image note":
            prompt_seed_parts.append(asset.visual_notes)

    top_layout = layout_counter.most_common(1)[0][0] if layout_counter else "unknown"
    top_typography = typography_counter.most_common(1)[0][0] if typography_counter else "unknown"
    decorative = [name for name, _ in decorative_counter.most_common(10)]
    palette_tokens = [
        "warm beige",
        "dark brown",
        "soft orange",
        "dusty pink",
        "lavender accent",
    ]
    layout_grammar = unique(
        [
            "large title banner",
            "one idea per block",
            "clear grid or card structure",
            "thin frame with corner ornaments",
            "high readability over decoration",
            top_layout,
        ]
    )
    typography_tokens = unique(
        [
            "brush-style headline",
            "bold Chinese title",
            "high contrast body text",
            top_typography,
        ]
    )
    decorative_grammar = unique(
        [
            "book and scroll motifs",
            "hand-drawn icons",
            "simple annotation marks",
            *decorative,
        ]
    )
    composition_rules = unique(
        [
            "keep one dominant focus per page",
            "use 3-7 visual blocks, not dense paragraphs",
            "pair every concept with a visual marker",
            "keep white space readable",
        ]
    )
    prompt_seed = ", ".join(
        unique(
            [
                "vintage parchment knowledge poster",
                "clean editorial layout",
                "warm beige background",
                "dark brown typography",
                "orange highlight bars",
                "simple iconography",
                *prompt_seed_parts,
            ]
        )
    )
    negative_prompt = ", ".join(
        [
            "low quality",
            "cluttered layout",
            "unreadable text",
            "generic ai slop",
            "too much decoration",
            "neon cyberpunk",
        ]
    )
    style_name = "vintage handbook"
    base_style = "parchment educational poster"
    information_density = "medium-high"
    return (
        style_name,
        base_style,
        palette_tokens,
        layout_grammar,
        typography_tokens,
        decorative_grammar,
        composition_rules,
        prompt_seed,
        negative_prompt,
        reference_images,
        information_density,
    )


def build_learning_assets(bundle: Any):
    all_text = "\n".join(get_all_post_texts(bundle))
    tokens = split_terms(all_text)
    token_counter = Counter(tokens)
    top_terms = [term for term, count in token_counter.most_common() if count >= 2]
    if not top_terms:
        top_terms = [term for term, _ in token_counter.most_common(12)]

    content_knowledge_kb = brain_models.ContentKnowledgeKB(
        creator_name=bundle.creator_hint or bundle.account_profile.display_name,
        platform=bundle.platform_hint or bundle.account_profile.platform,
        source_posts_analyzed=len(bundle.posts),
        knowledge_domains=infer_knowledge_domains(top_terms),
        topic_clusters=infer_topic_clusters(bundle.posts, top_terms),
        recurring_concepts=top_terms[:20],
        reusable_explanations=infer_reusable_explanations(bundle.posts),
        cross_domain_mappings=infer_cross_domain_mappings(bundle.posts),
        content_templates=infer_templates(bundle.posts),
        question_space=infer_question_space(top_terms),
        evidence=[
            brain_models.RuleEvidence(
                description="Derived from repeated titles, body copy, hashtags, and high-performing posts in the captured set.",
                example_refs=[post.post_id for post in sorted(bundle.posts, key=lambda p: (p.metrics.likes or 0, p.metrics.saves or 0), reverse=True)[:5]],
                confidence="inferred",
            )
        ],
    )

    (
        style_name,
        base_style,
        palette_tokens,
        layout_grammar,
        typography_tokens,
        decorative_grammar,
        composition_rules,
        prompt_seed,
        negative_prompt,
        reference_images,
        information_density,
    ) = infer_visual_style(bundle)

    visual_prompt_kernel = brain_models.VisualPromptKernel(
        creator_name=bundle.creator_hint or bundle.account_profile.display_name,
        platform=bundle.platform_hint or bundle.account_profile.platform,
        style_name=style_name,
        base_style=base_style,
        palette_tokens=palette_tokens,
        layout_grammar=layout_grammar,
        typography_tokens=typography_tokens,
        decorative_grammar=decorative_grammar,
        composition_rules=composition_rules,
        information_density=information_density,
        prompt_seed=prompt_seed,
        negative_prompt=negative_prompt,
        reference_images=unique(reference_images)[:12],
        evidence=[
            brain_models.RuleEvidence(
                description="Derived from the repeated visual asset grammar and page structure of the captured posts.",
                example_refs=[post.post_id for post in bundle.posts[:5]],
                confidence="inferred",
            )
        ],
    )

    meta = brain_models.AccountBrainMeta(
        generated_at=datetime.now(tz=UTC),
        input_completeness=bundle.capture_meta.completeness,
        total_posts_analyzed=len(bundle.posts),
        total_visuals_analyzed=len(bundle.visual_assets),
        notes="Derived dual-track learning assets: content knowledge KB + visual prompt kernel.",
    )

    return brain_models.LearningAssetsBundle(
        creator_name=bundle.creator_hint or bundle.account_profile.display_name,
        platform=bundle.platform_hint or bundle.account_profile.platform,
        content_knowledge_kb=content_knowledge_kb,
        visual_prompt_kernel=visual_prompt_kernel,
        meta=meta,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive content knowledge and visual prompt learning assets from a CaptureBundle JSON.")
    parser.add_argument("input_path", help="Path to normalized CaptureBundle JSON")
    parser.add_argument("-o", "--output", help="Output JSON path")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    input_path = Path(args.input_path).expanduser().resolve()
    bundle = load_capture_bundle(input_path)
    assets = build_learning_assets(bundle)
    output_text = assets.model_dump_json(indent=2 if args.pretty else None, ensure_ascii=False)

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_text, encoding="utf-8")
    else:
        print(output_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
