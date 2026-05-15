from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from typing import Any

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


from generate_image_via_local_api import DEFAULT_BASE_URL, DEFAULT_MODEL, call_image_api, load_api_key


def build_image_prompts(knowledge_base: dict[str, Any], content_bundle: dict[str, Any]) -> list[dict[str, Any]]:
    visual_style = knowledge_base.get("style_kb", {}).get("visual_style", {})
    prompt_kb = knowledge_base.get("prompt_kb", {})
    base_style = ", ".join(
        visual_style.get("palette", [])
        + visual_style.get("layout_rules", [])
        + visual_style.get("composition_rules", [])
        + prompt_kb.get("image_prompt_fragments", [])
    )
    negative_prompt = ", ".join(prompt_kb.get("negative_prompt_fragments", []))

    prompts = []
    for page in content_bundle.get("pages", []):
        prompt = (
            f"Xiaohongshu educational carousel page, {base_style}, "
            f"page title: {page['title']}, key points: {'; '.join(page['bullets'])}, "
            "Chinese readable layout, editorial composition, strong hierarchy"
        )
        prompts.append(
            {
                "page_number": page["page_number"],
                "role": page["role"],
                "title": page["title"],
                "prompt": prompt,
                "negative_prompt": negative_prompt,
            }
        )
    return prompts


def render_prompts(prompts: list[dict[str, Any]], output_dir: Path) -> list[dict[str, Any]]:
    api_key = load_api_key(None)
    rendered: list[dict[str, Any]] = []
    images_dir = output_dir / "generated-images"
    images_dir.mkdir(parents=True, exist_ok=True)

    for prompt_item in prompts:
        output_path = images_dir / f"page-{prompt_item['page_number']:02d}.png"
        result = call_image_api(
            base_url=os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL),
            api_key=api_key,
            model=os.environ.get("OPENAI_IMAGE_MODEL", DEFAULT_MODEL),
            prompt=prompt_item["prompt"],
            n=1,
            response_format="b64_json",
            size=os.environ.get("OPENAI_IMAGE_SIZE", ""),
        )
        images = result.get("data") or []
        first = images[0] if images else {}
        b64 = first.get("b64_json") if isinstance(first, dict) else None
        if not isinstance(b64, str) or not b64:
            raise RuntimeError(f"No image data returned for page {prompt_item['page_number']}")
        output_path.write_bytes(base64.b64decode(b64))
        rendered.append({**prompt_item, "image_path": str(output_path)})

    return rendered


def save_outputs(prompts: list[dict[str, Any]], rendered: list[dict[str, Any]], output_dir: Path) -> dict[str, str]:
    prompts_path = output_dir / "image-prompts.json"
    plan_path = output_dir / "image-plan.json"
    summary_path = output_dir / "result-summary.md"

    prompts_path.write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    plan_path.write_text(json.dumps(rendered, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# 最终图文结果", ""]
    for item in rendered:
        lines.append(f"## 第{item['page_number']}页 - {item['title']}")
        lines.append(f"- 图片: {item['image_path']}")
        lines.append(f"- Prompt: {item['prompt']}")
        lines.append("")
    summary_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "image_prompts": str(prompts_path),
        "image_plan": str(plan_path),
        "summary": str(summary_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render final Xiaohongshu images from a knowledge base and content bundle.")
    parser.add_argument("knowledge_base_path", help="Path to knowledge-base.json")
    parser.add_argument("content_bundle_path", help="Path to content-bundle.json")
    parser.add_argument("--json", action="store_true", help="Print saved file paths as JSON")
    args = parser.parse_args()

    knowledge_base = read_json(Path(args.knowledge_base_path).expanduser().resolve())
    content_bundle = read_json(Path(args.content_bundle_path).expanduser().resolve())
    output_dir = get_wenxuan_stage_output_dir("image-studio")
    prompts = build_image_prompts(knowledge_base, content_bundle)
    rendered = render_prompts(prompts, output_dir)
    saved = save_outputs(prompts, rendered, output_dir)

    if args.json:
        print(json.dumps(saved, ensure_ascii=False, indent=2))
    else:
        print(saved["summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
