#!/usr/bin/env python3
"""wenxuan-exam 会话校验与进度检查（仅标准库，无第三方依赖）。

用法：
    python check_session.py <会话目录>
    python check_session.py <会话目录> --stage 3
    python check_session.py --new <slug> --dir <父目录>

只校验形式（文件存在、占位符是否填、证据卡是否含反方、大纲引用是否越界），
不判断内容质量，也不生成任何结论。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import shutil
import sys
from pathlib import Path

PLACEHOLDER = "[待你填写]"

FILES = {
    "card": "00-选题卡.md",
    "exam": "01-考题单.md",
    "evidence": "02-证据卡.md",
    "note": "03-分析笔记.md",
    "review": "04-讲解批改.md",
    "outline": "05-传播大纲.md",
    "archive": "06-归档.md",
}

ASSETS = {
    "card": "session-card.md",
    "note": "research-note.md",
    "archive": "archive.md",
}

# 每个阶段进入前必须满足的条件：(阶段号, 阶段名, 需要检查的项)
STAGE_REQUIREMENTS = {
    1: "出题：00-选题卡 存在且研究前判断已填",
    2: "地图：01-考题单 存在且含六维与纵横问法",
    3: "查证：02-证据卡 至少 3 张，且至少 1 条反方/冲突材料",
    4: "判断：03-分析笔记 的五段判断栏位不再全是占位符",
    5: "讲解批改：04-讲解批改 存在，且 03 的判断已落笔",
    6: "传播大纲：05-传播大纲 存在且引用编号都在 02/03 范围内",
}


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _count_cards(text: str) -> int:
    return len(re.findall(r"^###\s*卡\s*[EA-Z]?\d*", text, flags=re.M))


_EMPTY_VALUES = {"", "无", "没有", "暂无", "未找到", "待你填写", "待查", "none", "n/a", "na", "null", "-", "—"}


def _has_counter(text: str) -> bool:
    """证据卡里是否真的存在反方/冲突材料（空值、占位符不算）。"""
    pattern = re.compile(r"(反例|反方|冲突材料|批评|不支持|相反结果)[^\n]*?[:：]([^\n]*)")
    for m in pattern.finditer(text):
        value = m.group(2).strip().strip("「」\"' 　")
        if value.lower() not in _EMPTY_VALUES and PLACEHOLDER not in value:
            return True
    return False


def _unfilled(text: str) -> int:
    return text.count(PLACEHOLDER)


def _judgement_filled(text: str) -> bool:
    """03 笔记里 '判断 1' 之后的观点一行是否已填。"""
    m = re.search(r"观点（可被反驳的一句话）[:：]\s*(.*)", text)
    if not m:
        return False
    value = m.group(1).strip()
    return bool(value) and PLACEHOLDER not in value


def _evidence_ids(coach: str, evidence: str, note: str) -> set[str]:
    """02 定义的卡号 + 考题单/分析笔记正文里引用过的编号。"""
    ids: set[str] = set()
    ids.update(re.findall(r"^###\s*卡\s*[EA-Z]?(\d+)", evidence, flags=re.M))
    ids.update(re.findall(r"[Ee](\d+)", coach))
    ids.update(re.findall(r"[Ee](\d+)", note))
    return ids


def _outline_refs(text: str) -> set[str]:
    return set(re.findall(r"[Ee](\d+)", text))


def check(session: Path, stage: int | None = None) -> int:
    print(f"会话目录：{session}")
    if not session.exists():
        print("  [FAIL] 目录不存在")
        return 2

    texts = {k: _read(session / v) for k, v in FILES.items()}
    problems: list[str] = []
    done: list[str] = []

    # 文件完整性
    for key, name in FILES.items():
        mark = "OK  " if (session / name).exists() else "MISS"
        print(f"  [{mark}] {name}")

    # 阶段 1
    if texts["card"]:
        if _unfilled(texts["card"]):
            problems.append(f"阶段1：00-选题卡 仍有 {_unfilled(texts['card'])} 处 [待你填写]（重点看研究前判断）")
        else:
            done.append("阶段1：选题卡已填完")
    else:
        problems.append("阶段1：缺少 00-选题卡.md")

    # 阶段 2
    if texts["exam"]:
        dims = ["定义", "背景", "原理", "价值", "比较", "局限"]
        missing = [d for d in dims if d not in texts["exam"]]
        if missing:
            problems.append("阶段2：01-考题单 缺少维度：" + "、".join(missing))
        elif "纵向" not in texts["exam"] or "横向" not in texts["exam"]:
            problems.append("阶段2：01-考题单 缺少纵横问法")
        else:
            done.append("阶段2：六维与纵横问法齐备")
    else:
        problems.append("阶段2：缺少 01-考题单.md（AI 应生成）")

    # 阶段 3
    if texts["evidence"]:
        n = _count_cards(texts["evidence"])
        if n < 3:
            problems.append(f"阶段3：02-证据卡 只有 {n} 张，至少 3 张")
        elif not _has_counter(texts["evidence"]):
            problems.append("阶段3：02-证据卡 里没有任何反方/冲突材料，还不能进入判断阶段")
        else:
            done.append(f"阶段3：{n} 张证据卡，含反方材料")
    else:
        problems.append("阶段3：缺少 02-证据卡.md")

    # 阶段 4
    if texts["note"]:
        if not _judgement_filled(texts["note"]):
            problems.append("阶段4：03-分析笔记 的「观点」仍是占位符——判断必须由你写")
        elif PLACEHOLDER in texts["note"]:
            problems.append(f"阶段4：03-分析笔记 还有 {_unfilled(texts['note'])} 处未填（含边界/置信度/未知清单）")
        else:
            done.append("阶段4：判断、边界、未知清单已落笔")
    else:
        problems.append("阶段4：缺少 03-分析笔记.md")

    # 阶段 5
    if texts["review"]:
        for block in ["讲清楚了的", "讲糊了的", "该补查什么"]:
            if block not in texts["review"]:
                problems.append(f"阶段5：04-讲解批改 缺少「{block}」区块")
                break
        else:
            done.append("阶段5：批改四块齐备")
    else:
        problems.append("阶段5：缺少 04-讲解批改.md（等你贴讲解后再检查）")

    # 阶段 6
    if texts["outline"]:
        refs = _outline_refs(texts["outline"])
        known = _evidence_ids(texts["exam"], texts["evidence"], texts["note"])
        unknown = sorted(r for r in refs if r not in known)
        if unknown:
            problems.append("阶段6：05-传播大纲 引用了未知证据编号：" + "、".join(unknown[:8]))
        else:
            done.append("阶段6：大纲引用未越界")
    else:
        problems.append("阶段6：缺少 05-传播大纲.md")

    budget = 0 if not texts["archive"] else texts["archive"].count("____")

    print("\n已完成：")
    for d in done or ["（暂无）"]:
        print(f"  + {d}")
    print("\n待处理：")
    for p in problems or ["（无，五阶段全通过）"]:
        print(f"  - {p}")
    if budget:
        print(f"\n归档提示：06-归档.md 还有 {budget} 处待填，发布后 48 小时再补。")

    if stage is not None:
        print(f"\n进入阶段 {stage} 的前置条件：{STAGE_REQUIREMENTS.get(stage, '未知阶段')}")
        if stage <= 1:
            ok = bool(texts["card"]) and _unfilled(texts["card"]) == 0
        elif stage == 2:
            ok = bool(texts["card"])
        elif stage == 3:
            ok = bool(texts["card"]) and bool(texts["exam"])
        elif stage == 4:
            ok = _count_cards(texts["evidence"]) >= 3 and _has_counter(texts["evidence"])
        elif stage == 5:
            ok = _judgement_filled(texts["note"])
        elif stage == 6:
            unknown_refs = [r for r in _outline_refs(texts["outline"])
                            if r not in _evidence_ids(texts["exam"], texts["evidence"], texts["note"])]
            ok = _judgement_filled(texts["note"]) and bool(texts["review"]) and not unknown_refs
        else:
            ok = False
        print("  结果：" + ("可以进入" if ok else "还不满足，先补齐上面的待处理项"))
        return 0 if ok else 1

    return 0 if not problems else 1


def scaffold(slug: str, parent: Path, assets_dir: Path) -> int:
    today = _dt.date.today().strftime("%Y%m%d")
    session = parent / f"{today}-{slug}"
    session.mkdir(parents=True, exist_ok=True)

    for key, src_name in ASSETS.items():
        src = assets_dir / src_name
        dst = session / FILES[key]
        if not dst.exists():
            if src.exists():
                text = src.read_text(encoding="utf-8")
                # 第一行形如 "# 选题卡 · <概念名>"，把占位名替换为 slug
                head, _, rest = text.partition("\n")
                head = head.replace("<概念名>", slug)
                text = head + "\n" + rest
                dst.write_text(text, encoding="utf-8")
            else:
                dst.write_text(f"# {slug}\n", encoding="utf-8")

    for key in ("exam", "evidence", "review", "outline"):
        dst = session / FILES[key]
        if not dst.exists():
            header = {
                "exam": f"# 考题单 · {slug}\n\n> AI 生成。只写查什么/想什么/答什么，不写结论。\n",
                "evidence": f"# 证据卡 · {slug}\n\n> AI 搬材料，判断栏由你填。\n",
                "review": f"# 讲解批改 · {slug}\n\n> 先贴你的讲解原文，再批改。\n",
                "outline": f"# 传播大纲 · {slug}\n\n> 只能引用 02/03 的证据编号。\n",
            }[key]
            dst.write_text(header, encoding="utf-8")

    print(f"已创建会话：{session}")
    print("下一步：填 00-选题卡.md 的「研究前判断」，再让 AI 出 01-考题单。")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="wenxuan-exam 会话校验")
    ap.add_argument("session", nargs="?", help="会话目录")
    ap.add_argument("--stage", type=int, choices=[1, 2, 3, 4, 5, 6], help="只检查某阶段前置条件")
    ap.add_argument("--new", metavar="SLUG", help="新建会话，参数为 slug")
    ap.add_argument("--dir", default=".", help="--new 时的父目录")
    args = ap.parse_args()

    assets_dir = Path(__file__).resolve().parent.parent / "assets"

    if args.new:
        return scaffold(args.new, Path(args.dir).expanduser().resolve(), assets_dir)

    if not args.session:
        ap.print_help()
        return 2
    return check(Path(args.session).expanduser().resolve(), args.stage)


if __name__ == "__main__":
    sys.exit(main())


