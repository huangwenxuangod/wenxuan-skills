#!/usr/bin/env python3
"""检查一份已填写的单页研究表单是否完整（仅标准库）。

用法：
    python check_sheet.py <表单.md>

只检查形式：认知地图六维是否齐、有没有反方证据、判断是否落笔、大纲引用是否越界。
不判断内容质量，也不生成结论。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PLACEHOLDER = "[待你填写]"
DIMENSIONS = ["是什么", "从哪来", "和谁比", "证据", "反方", "失效"]
EMPTY_VALUES = {"", "无", "没有", "暂无", "未找到", "待查", "none", "n/a", "na", "-", "—"}


def has_counter(text: str) -> bool:
    pattern = re.compile(r"(反例|反方|冲突材料)[^\n]*?[:：]([^\n]*)")
    for m in pattern.finditer(text):
        value = m.group(2).strip().strip("「」\"' 　")
        if value.lower() not in EMPTY_VALUES and PLACEHOLDER not in value:
            return True
    return False


def evidence_ids(text: str) -> set[str]:
    return set(re.findall(r"^###\s*E(\d+)", text, flags=re.M))


def outline_refs(text: str) -> set[str]:
    section = text.split("## 六、传播大纲")
    if len(section) < 2:
        return set()
    return set(re.findall(r"[Ee](\d+)", section[1].split("## 七、")[0]))


def judgement_filled(text: str) -> bool:
    m = re.search(r"观点（一句可被反驳的话）[:：]\s*(.*)", text)
    return bool(m) and bool(m.group(1).strip()) and PLACEHOLDER not in m.group(1)


def main() -> int:
    if len(sys.argv) < 2:
        print("用法：python check_sheet.py <表单.md>")
        return 2

    path = Path(sys.argv[1]).expanduser()
    if not path.exists():
        print(f"文件不存在：{path}")
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")

    problems: list[str] = []
    done: list[str] = []

    missing = [d for d in DIMENSIONS if d not in text]
    if missing:
        problems.append("认知地图缺维度：" + "、".join(missing))
    else:
        done.append("认知地图六维齐备")

    ids = evidence_ids(text)
    if len(ids) < 3:
        problems.append(f"证据只有 {len(ids)} 条，至少 3 条")
    elif not has_counter(text):
        problems.append("没有任何反方/冲突材料，还不能进入判断")
    else:
        done.append(f"{len(ids)} 条证据，含反方材料")

    if not judgement_filled(text):
        problems.append("「观点」仍是占位符——判断必须由你写")
    elif PLACEHOLDER in text:
        problems.append(f"还有 {text.count(PLACEHOLDER)} 处未填（边界/置信度/未知清单）")
    else:
        done.append("判断、边界、未知清单已落笔")

    refs = outline_refs(text)
    unknown = sorted(r for r in refs if r not in ids)
    if unknown:
        problems.append("大纲引用了不存在的证据编号：" + "、".join(unknown))
    elif refs:
        done.append("大纲引用未越界")

    for line in ["讲清楚了的", "讲糊了的", "该补查什么"]:
        if line not in text:
            problems.append(f"批改缺「{line}」区块")
            break
    else:
        done.append("讲解批改四块齐备")

    print(f"表单：{path.name}")
    print("\n已完成：")
    for d in done or ["（暂无）"]:
        print(f"  + {d}")
    print("\n待处理：")
    for p in problems or ["（无，全部通过）"]:
        print(f"  - {p}")

    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
