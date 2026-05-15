from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


for candidate in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
    if (candidate / "env_utils.py").exists():
        PROJECT_ROOT = candidate
        break
else:
    PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from env_utils import load_wenxuan_runtime_env


SKILL_ROOT = Path(__file__).resolve().parents[1]
load_wenxuan_runtime_env(PROJECT_ROOT, cwd=Path.cwd(), skill_root=SKILL_ROOT)


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the full wenxuan pipeline from knowledge base or search results to final content and image outputs.")
    parser.add_argument("--query", help="Search query; runs search -> knowledge base -> content -> image in one command")
    parser.add_argument("--search-result", help="Path to search-result.json")
    parser.add_argument("--knowledge-base", help="Path to knowledge-base.json")
    parser.add_argument("--json", action="store_true", help="Print final saved file paths as JSON")
    args = parser.parse_args()

    search_script_dir = PROJECT_ROOT / "skills" / "wenxuan-skills-search" / "scripts"
    if str(search_script_dir) not in sys.path:
        sys.path.insert(0, str(search_script_dir))
    search_module = load_module(search_script_dir / "search.py", "wenxuan_search_builder")
    kb_module = load_module(PROJECT_ROOT / "skills" / "wenxuan-skills-knowledge-base" / "scripts" / "build_knowledge_base.py", "wenxuan_kb_builder")
    content_module = load_module(PROJECT_ROOT / "skills" / "wenxuan-skills-content-studio" / "scripts" / "generate_content.py", "wenxuan_content_builder")
    image_module = load_module(PROJECT_ROOT / "skills" / "wenxuan-skills-image-studio" / "scripts" / "render_images.py", "wenxuan_image_builder")

    search_saved = None
    if args.knowledge_base:
        knowledge_base = kb_module.read_json(Path(args.knowledge_base).expanduser().resolve())
        kb_output_dir = kb_module.get_wenxuan_stage_output_dir("knowledge-base")
        kb_saved = kb_module.save_outputs(knowledge_base, kb_output_dir)
        kb_path = Path(kb_saved["knowledge_base"])
    elif args.query:
        task_type = search_module.infer_task_type(args.query)
        planned_providers = search_module.build_provider_plan(args.query, task_type, "", [], only_available=False)
        availability = search_module.filter_available_providers(planned_providers)
        pre_mode_providers = availability["available"] or planned_providers
        mode_plan = search_module.apply_provider_mode(pre_mode_providers, "", task_type, budget="medium")
        search_result = search_module.aggregate_search(
            args.query,
            mode_plan["providers"],
            task_type=task_type,
            platform_hint="",
            creator_hint="",
            limit=None,
            sort_order="relevance",
        )
        search_result["route_plan"]["planned_providers"] = planned_providers
        search_result["route_plan"]["providers_before_mode"] = pre_mode_providers
        search_result["route_plan"]["provider_mode"] = mode_plan["mode"]
        search_result["route_plan"]["budget"] = "medium"
        search_result["route_plan"]["provider_mode_profile"] = mode_plan["profile"]
        search_result["route_plan"]["truncated_providers"] = mode_plan["truncated_providers"]
        search_result["route_plan"]["skipped_providers"] = availability["skipped"]
        search_result["capture_meta"]["skipped_providers"] = availability["skipped"]
        search_result["capture_meta"]["provider_mode"] = mode_plan["mode"]
        search_result["capture_meta"]["budget"] = "medium"
        search_saved = search_module.save_capture(search_result, task_type, args.query)
        knowledge_base = kb_module.build_knowledge_base(search_result, Path(search_saved["json"]).stem)
        kb_output_dir = kb_module.get_wenxuan_stage_output_dir("knowledge-base")
        kb_saved = kb_module.save_outputs(knowledge_base, kb_output_dir)
        kb_path = Path(kb_saved["knowledge_base"])
    elif args.search_result:
        search_payload = kb_module.read_json(Path(args.search_result).expanduser().resolve())
        knowledge_base = kb_module.build_knowledge_base(search_payload, Path(args.search_result).stem)
        kb_output_dir = kb_module.get_wenxuan_stage_output_dir("knowledge-base")
        kb_saved = kb_module.save_outputs(knowledge_base, kb_output_dir)
        kb_path = Path(kb_saved["knowledge_base"])
    else:
        raise SystemExit("Provide either --search-result or --knowledge-base.")

    topics = content_module.build_topics(knowledge_base)
    selected_topic = content_module.select_topic(topics)
    content_bundle, page_plan, markdown_text = content_module.build_content_bundle(knowledge_base, selected_topic)
    content_output_dir = content_module.get_wenxuan_stage_output_dir("content-studio")
    content_saved = content_module.save_outputs(topics, content_bundle, page_plan, markdown_text, content_output_dir)

    image_output_dir = image_module.get_wenxuan_stage_output_dir("image-studio")
    prompts = image_module.build_image_prompts(knowledge_base, content_bundle)
    rendered = image_module.render_prompts(prompts, image_output_dir)
    image_saved = image_module.save_outputs(prompts, rendered, image_output_dir)

    result = {
        "search": search_saved,
        "knowledge_base": str(kb_path),
        "content": content_saved,
        "images": image_saved,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
