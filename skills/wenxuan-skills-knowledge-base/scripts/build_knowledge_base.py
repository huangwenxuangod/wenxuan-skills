from __future__ import annotations

import argparse
import json
import re
from collections import Counter
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


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def extract_terms(text: str) -> list[str]:
    raw_terms = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]{2,12}", text)
    stopwords = {
        "我们", "你们", "他们", "这个", "那个", "一个", "可以", "如何", "什么", "就是",
        "进行", "以及", "内容", "项目", "问题", "方法", "效果", "因为", "所以", "如果",
        "时候", "已经", "关于", "使用", "实现", "需要", "支持", "推荐", "平台", "账号",
        "search", "result", "content", "guide", "with", "from", "this", "that",
    }
    return [term for term in raw_terms if term.lower() not in stopwords]


def gather_documents(payload: dict[str, Any]) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    if isinstance(payload.get("results"), list):
        for item in payload["results"]:
            documents.append(
                {
                    "title": normalize_text(item.get("title")),
                    "body": normalize_text(item.get("body") or item.get("snippet")),
                    "source_url": normalize_text(item.get("source_url")),
                    "platform": normalize_text(item.get("platform")),
                    "tags": item.get("tags") or [],
                }
            )
    elif isinstance(payload.get("posts"), list):
        for post in payload["posts"]:
            documents.append(
                {
                    "title": normalize_text(post.get("title")),
                    "body": normalize_text(post.get("body")),
                    "source_url": normalize_text(post.get("source_url")),
                    "platform": normalize_text(post.get("platform")),
                    "tags": post.get("hashtags") or [],
                }
            )
    return documents


def infer_visual_style(documents: list[dict[str, Any]]) -> dict[str, Any]:
    corpus = "\n".join(
        " ".join([doc["title"], doc["body"]]) for doc in documents
    )
    palette = ["warm beige", "dark brown", "soft orange"]
    if any(token in corpus for token in ["极简", "简洁", "干净"]):
        palette = ["off-white", "charcoal", "soft gray"]
    layout_rules = ["cover with strong title", "one idea per page", "card-based structure", "high readability"]
    if any(token in corpus for token in ["清单", "步骤", "总结", "盘点"]):
        layout_rules.append("numbered checklist layout")
    return {
        "palette": palette,
        "layout_rules": layout_rules,
        "typography": ["bold Chinese title", "high contrast body text"],
        "decorative_elements": ["thin borders", "simple icons", "annotation marks"],
        "composition_rules": ["single focus per page", "3-6 content blocks", "white space first"],
    }


def build_knowledge_base(payload: dict[str, Any], input_name: str) -> dict[str, Any]:
    documents = gather_documents(payload)
    corpus = "\n".join(
        " ".join([doc["title"], doc["body"], " ".join(doc["tags"])]) for doc in documents
    )
    terms = extract_terms(corpus)
    term_counts = Counter(terms)
    top_terms = [term for term, count in term_counts.most_common(30) if count >= 1]
    topic_clusters = []
    for term in top_terms[:12]:
        hits = sum(1 for doc in documents if term in f"{doc['title']} {doc['body']}")
        topic_clusters.append({"topic": term, "hits": hits})

    fact_kb = {
        "entities": top_terms[:8],
        "concepts": top_terms[:15],
        "methods": [term for term in top_terms if any(token in term for token in ["方法", "步骤", "流程", "模板"])][:8],
        "cases": [doc["title"] for doc in documents[:8] if doc["title"]],
        "claims": [doc["body"][:120] for doc in documents[:10] if doc["body"]],
        "evidence_refs": [doc["source_url"] for doc in documents[:20] if doc["source_url"]],
    }

    writing_style = {
        "tone": ["educational", "practical", "concise"],
        "title_patterns": ["数字+结果", "问题+解决方案", "人群+场景+收益"],
        "opening_patterns": ["先给结论", "先给场景", "先给痛点"],
        "cta_patterns": ["收藏备用", "关注获取更多", "评论区交流"],
        "sentence_rhythm": ["short declarative sentences", "list-driven paragraphs"],
    }
    style_kb = {
        "writing_style": writing_style,
        "visual_style": infer_visual_style(documents),
    }

    prompt_kb = {
        "content_prompt_fragments": [
            "用小红书图文风格写作",
            "先给结果，再给步骤",
            "强调可执行性和收藏价值",
        ],
        "image_prompt_fragments": [
            "editorial xiaohongshu carousel cover",
            "clean Chinese knowledge poster",
            "high readability, card layout, strong title hierarchy",
        ],
        "negative_prompt_fragments": [
            "low quality",
            "cluttered layout",
            "unreadable tiny text",
            "generic ai slop",
        ],
        "style_modifiers": style_kb["visual_style"]["palette"] + style_kb["visual_style"]["layout_rules"],
        "layout_modifiers": style_kb["visual_style"]["composition_rules"],
    }

    return {
        "project_id": re.sub(r"[^\w\-]+", "-", input_name.lower()).strip("-") or "knowledge-base",
        "project_name": input_name,
        "topic_domain": top_terms[0] if top_terms else input_name,
        "sources": documents,
        "fact_kb": fact_kb,
        "style_kb": style_kb,
        "prompt_kb": prompt_kb,
        "topic_clusters": topic_clusters,
        "metadata": {
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "document_count": len(documents),
            "source_type": "search-results" if "results" in payload else "capture-bundle",
        },
    }


def save_outputs(knowledge_base: dict[str, Any], output_dir: Path) -> dict[str, str]:
    knowledge_base_path = output_dir / "knowledge-base.json"
    fact_kb_path = output_dir / "fact-kb.json"
    style_kb_path = output_dir / "style-kb.json"
    prompt_kb_path = output_dir / "prompt-kb.json"

    knowledge_base_path.write_text(json.dumps(knowledge_base, ensure_ascii=False, indent=2), encoding="utf-8")
    fact_kb_path.write_text(json.dumps(knowledge_base["fact_kb"], ensure_ascii=False, indent=2), encoding="utf-8")
    style_kb_path.write_text(json.dumps(knowledge_base["style_kb"], ensure_ascii=False, indent=2), encoding="utf-8")
    prompt_kb_path.write_text(json.dumps(knowledge_base["prompt_kb"], ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "knowledge_base": str(knowledge_base_path),
        "fact_kb": str(fact_kb_path),
        "style_kb": str(style_kb_path),
        "prompt_kb": str(prompt_kb_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a project knowledge base from search results or captured materials.")
    parser.add_argument("input_path", help="Path to search-result.json or capture-bundle.json")
    parser.add_argument("--project-name", help="Optional project name override")
    parser.add_argument("--json", action="store_true", help="Print saved file paths as JSON")
    args = parser.parse_args()

    input_path = Path(args.input_path).expanduser().resolve()
    payload = read_json(input_path)
    project_name = args.project_name or input_path.stem
    knowledge_base = build_knowledge_base(payload, project_name)
    output_dir = get_wenxuan_stage_output_dir("knowledge-base")
    saved = save_outputs(knowledge_base, output_dir)

    if args.json:
        print(json.dumps(saved, ensure_ascii=False, indent=2))
    else:
        print(saved["knowledge_base"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
