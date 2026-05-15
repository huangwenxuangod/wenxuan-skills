from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

for candidate in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
    if (candidate / "env_utils.py").exists():
        PROJECT_ROOT = candidate
        break
else:
    PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from env_utils import get_wenxuan_stage_output_dir, load_wenxuan_runtime_env


SKILL_ROOT = Path(__file__).resolve().parents[1]
load_wenxuan_runtime_env(PROJECT_ROOT, cwd=Path.cwd(), skill_root=SKILL_ROOT)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_topics(knowledge_base: dict[str, Any]) -> list[dict[str, Any]]:
    concepts = knowledge_base.get("fact_kb", {}).get("concepts", [])[:8]
    project_name = knowledge_base.get("project_name", "项目")
    topics = []
    for concept in concepts[:5]:
        topics.append(
            {
                "topic_id": f"topic-{len(topics)+1}",
                "title": f"{concept} 速懂：新手怎么快速上手",
                "angle": f"围绕 {concept} 做小红书式知识整理，强调实操和收藏价值",
                "audience": "想快速理解并实际使用该主题的新手",
                "promise": f"看完就能掌握 {concept} 的核心框架",
                "project_name": project_name,
            }
        )
    if not topics:
        topics.append(
            {
                "topic_id": "topic-1",
                "title": f"{project_name} 入门指南",
                "angle": "从概念、方法、场景三部分切入",
                "audience": "对该主题感兴趣的新手",
                "promise": "一篇看懂核心逻辑",
                "project_name": project_name,
            }
        )
    return topics


def select_topic(topics: list[dict[str, Any]], topic_id: str = "") -> dict[str, Any]:
    if topic_id:
        for topic in topics:
            if topic["topic_id"] == topic_id:
                return topic
    return topics[0]


def build_content_bundle(knowledge_base: dict[str, Any], topic: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], str]:
    concepts = knowledge_base.get("fact_kb", {}).get("concepts", [])[:6]
    methods = knowledge_base.get("fact_kb", {}).get("methods", [])[:4]
    claims = knowledge_base.get("fact_kb", {}).get("claims", [])[:6]
    palette = knowledge_base.get("style_kb", {}).get("visual_style", {}).get("palette", [])

    page_titles = [
        "封面",
        "为什么值得看",
        "核心概念",
        "操作步骤",
        "常见误区",
        "总结与CTA",
    ]
    page_bodies = [
        [topic["title"], topic["promise"]],
        [f"适合人群：{topic['audience']}", f"阅读收益：{topic['promise']}"],
        concepts[:3] or ["核心概念一", "核心概念二", "核心概念三"],
        methods[:3] or ["先理解框架", "再看案例", "最后马上实操"],
        claims[:3] or ["不要只看表面概念", "不要堆信息不整理", "不要缺少明确结论"],
        ["建议先收藏", "按照步骤立即实践", "关注获取后续专题整理"],
    ]

    pages = []
    for index, title in enumerate(page_titles):
        pages.append(
            {
                "page_number": index + 1,
                "role": "cover" if index == 0 else ("cta" if index == len(page_titles) - 1 else "content"),
                "title": title,
                "bullets": page_bodies[index],
            }
        )

    content_bundle = {
        "platform": "xhs",
        "topic": topic,
        "title": topic["title"],
        "summary": topic["angle"],
        "pages": pages,
        "cta": "收藏这篇，按页照着做；想看下一篇可以评论区告诉我。",
        "hashtags": concepts[:6] or ["知识整理", "小红书图文", "干货分享"],
        "style_refs": {
            "palette": palette,
            "tone": knowledge_base.get("style_kb", {}).get("writing_style", {}).get("tone", []),
        },
        "source_refs": knowledge_base.get("fact_kb", {}).get("evidence_refs", [])[:10],
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }

    page_plan = {
        "platform": "xhs",
        "page_count": len(pages),
        "pages": [{"page_number": page["page_number"], "role": page["role"], "title": page["title"]} for page in pages],
    }

    markdown = [f"# {content_bundle['title']}", "", content_bundle["summary"], ""]
    for page in pages:
        markdown.append(f"## 第{page['page_number']}页 - {page['title']}")
        markdown.extend([f"- {bullet}" for bullet in page["bullets"]])
        markdown.append("")
    markdown.append("## CTA")
    markdown.append(content_bundle["cta"])
    markdown_text = "\n".join(markdown)

    return content_bundle, page_plan, markdown_text


def save_outputs(topics: list[dict[str, Any]], content_bundle: dict[str, Any], page_plan: dict[str, Any], markdown_text: str, output_dir: Path) -> dict[str, str]:
    topic_path = output_dir / "topic-set.json"
    content_path = output_dir / "content-bundle.json"
    page_plan_path = output_dir / "page-plan.json"
    markdown_path = output_dir / "final-post.md"

    topic_path.write_text(json.dumps(topics, ensure_ascii=False, indent=2), encoding="utf-8")
    content_path.write_text(json.dumps(content_bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    page_plan_path.write_text(json.dumps(page_plan, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(markdown_text, encoding="utf-8")

    return {
        "topic_set": str(topic_path),
        "content_bundle": str(content_path),
        "page_plan": str(page_plan_path),
        "markdown": str(markdown_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Xiaohongshu topics and content from a knowledge base.")
    parser.add_argument("knowledge_base_path", help="Path to knowledge-base.json")
    parser.add_argument("--topic-id", help="Optional topic id to choose from topic-set")
    parser.add_argument("--json", action="store_true", help="Print saved file paths as JSON")
    args = parser.parse_args()

    knowledge_base = read_json(Path(args.knowledge_base_path).expanduser().resolve())
    topics = build_topics(knowledge_base)
    selected_topic = select_topic(topics, args.topic_id or "")
    content_bundle, page_plan, markdown_text = build_content_bundle(knowledge_base, selected_topic)
    output_dir = get_wenxuan_stage_output_dir("content-studio")
    saved = save_outputs(topics, content_bundle, page_plan, markdown_text, output_dir)

    if args.json:
        print(json.dumps(saved, ensure_ascii=False, indent=2))
    else:
        print(saved["markdown"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
