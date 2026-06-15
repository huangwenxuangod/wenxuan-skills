#!/usr/bin/env python3
"""
wenxuan-translate 专用：Markdown → PDF 转换脚本（xhtml2pdf 后端 · v1.6 排版微调）

特点：
- 纯 Python，无 GTK / wkhtmltopdf 依赖
- **v1.5 关键修复**：monkey-patch xhtml2pdf 的 fontList 字典
  - xhtml2pdf 内部维护 fontList（小写 key → ReportLab 字体名）
  - 单独 `pdfmetrics.registerFont(TTFont)` **不会**让 xhtml2pdf 看到这个字体
  - 必须改 `xhtml2pdf.default.DEFAULT_FONT`，让后续创建的 context 知道这个别名
- **v1.6 排版微调**：
  - `text-align: justify` → `text-align: left`（修复中英混排时英文字间距被两端对齐撑大）
  - body `line-height: 1.7` → `1.55`（中文 PDF 阅读舒适值）
  - pre `line-height: 1.5` → `1.45`（code 块行高收紧，提升可读性）
  - 显式 `word-spacing: normal; letter-spacing: normal;` 重置
- 自动注册 Windows 系统中文字体（雅黑 msyh.ttc / Noto Sans SC / SimHei / SimSun）
- 支持外链图片（https://...）：自动下载 → 嵌入
- 支持本地图片（相对路径）：直接读取

用法：
    python md_to_pdf.py <input.md> <output.pdf> [--title "..."] [--author "..."]

依赖：pip install xhtml2pdf markdown
"""

import sys
import os
import re
import io
import base64
import argparse
import urllib.request
import urllib.parse
import urllib.error
import socket
import hashlib
import tempfile

# ── 关键：在 import xhtml2pdf 之后立即 monkey-patch fontList ──────────
# 必须在 pisa.CreatePDF 之前改 default.DEFAULT_FONT，
# xhtml2pdf 在创建 pisaContext 时会 copy.copy(default.DEFAULT_FONT)
import xhtml2pdf.default as xpdf_default

import markdown
from xhtml2pdf import pisa
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily


# ── 中文字体检测 ────────────────────────────────────────────────────
# 顺序很重要：优先 msyh.ttc 第一个 subfont（通常是 Regular），
# 备选 NotoSansSC-VF / SimHei / SimSun
ZH_FONT_CANDIDATES = [
    # (registered_name, path, subfontIndex, [aliases...])
    ("YaHei",  r"C:\Windows\Fonts\msyh.ttc",  0,             ["yahei", "microsoft yahei"]),
    ("NotoSC", r"C:\Windows\Fonts\NotoSansSC-VF.ttf", None,  ["noto sans sc", "notosc", "noto sans cjk sc"]),
    ("SimHei", r"C:\Windows\Fonts\simhei.ttf", None,         ["simhei"]),
    ("SimSun", r"C:\Windows\Fonts\simsun.ttc", 0,             ["simsun", "songti"]),
]

EN_FONT_CANDIDATES = [
    ("Consolas", r"C:\Windows\Fonts\consola.ttf", None, ["consolas", "consola"]),
    ("Courier",  r"C:\Windows\Fonts\cour.ttf",   None, ["courier", "courier new"]),
]

ZH_FONT: str | None = None
EN_FONT: str | None = None


def _register_fonts() -> tuple[str | None, str | None]:
    """注册字体到 ReportLab 全局表 + monkey-patch xhtml2pdf fontList。

    关键修复（v1.5）：
    - `pdfmetrics.registerFont(TTFont(...))` 让 ReportLab 知道字体存在
    - `registerFontFamily(...)` 让 bold/italic 都能找到
    - **`xhtml2pdf.default.DEFAULT_FONT['yahei'] = 'YaHei'`** ← 关键！
      让 xhtml2pdf 自己的 fontList（小写 key）知道"yahei"对应到 ReportLab 的 "YaHei"
    """
    global ZH_FONT, EN_FONT

    for full, path, idx, aliases in ZH_FONT_CANDIDATES:
        if not os.path.exists(path):
            continue
        try:
            if idx is not None:
                pdfmetrics.registerFont(TTFont(full, path, subfontIndex=idx))
            else:
                pdfmetrics.registerFont(TTFont(full, path))
            # 让 bold/italic 都指向同一个字体（中文常见坑：bold 标签 fallback 到拉丁字体）
            registerFontFamily(full, normal=full, bold=full, italic=full, boldItalic=full)

            # ★ v1.5 核心：monkey-patch xhtml2pdf 自己的 fontList 字典
            # 之后 xhtml2pdf 看到 font-family: "YaHei" 就能找到
            for alias in aliases:
                xpdf_default.DEFAULT_FONT[alias] = full
            xpdf_default.DEFAULT_FONT[full.lower()] = full

            ZH_FONT = full
            print(f"[INFO] 中文字体注册成功: {full} (aliases: {aliases})")
            break
        except Exception as e:
            print(f"[WARN] 注册中文字体 {full} 失败: {e}", file=sys.stderr)

    for full, path, idx, aliases in EN_FONT_CANDIDATES:
        if not os.path.exists(path):
            continue
        try:
            if idx is not None:
                pdfmetrics.registerFont(TTFont(full, path, subfontIndex=idx))
            else:
                pdfmetrics.registerFont(TTFont(full, path))
            for alias in aliases:
                xpdf_default.DEFAULT_FONT[alias] = full
            xpdf_default.DEFAULT_FONT[full.lower()] = full
            EN_FONT = full
            print(f"[INFO] 等宽字体注册成功: {full} (aliases: {aliases})")
            break
        except Exception as e:
            continue

    return ZH_FONT, EN_FONT


# ── 外链图片下载 ────────────────────────────────────────────────────
_IMAGE_CACHE: dict[str, str] = {}
_CACHE_DIR = None


def _ensure_cache_dir():
    global _CACHE_DIR
    if _CACHE_DIR is None:
        _CACHE_DIR = tempfile.mkdtemp(prefix="wenxuan_pdf_img_")
    return _CACHE_DIR


def _download_image(url: str, timeout: int = 15) -> str | None:
    if url in _IMAGE_CACHE:
        return _IMAGE_CACHE[url]

    cache_dir = _ensure_cache_dir()
    url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()[:16]
    ext = ".jpg"
    if ".png" in url.lower(): ext = ".png"
    elif ".gif" in url.lower(): ext = ".gif"
    elif ".webp" in url.lower(): ext = ".webp"
    elif ".svg" in url.lower(): ext = ".svg"

    local_path = os.path.join(cache_dir, f"{url_hash}{ext}")
    if os.path.exists(local_path):
        _IMAGE_CACHE[url] = local_path
        return local_path

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 wenxuan-translate"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        with open(local_path, "wb") as f:
            f.write(data)
        _IMAGE_CACHE[url] = local_path
        return local_path
    except (urllib.error.URLError, socket.timeout, Exception) as e:
        print(f"[WARN] 下载图片失败 {url[:60]}...: {e}", file=sys.stderr)
        return None


def link_callback(uri: str, rel: str) -> str:
    if os.path.exists(uri):
        return uri
    if uri.startswith(("http://", "https://")):
        local = _download_image(uri)
        return local if local else ""
    if rel and not os.path.isabs(uri):
        abs_path = os.path.join(rel, uri)
        if os.path.exists(abs_path):
            return abs_path
    return uri


# ── CSS 模板 ────────────────────────────────────────────────────────
def _build_css(zh: str, en: str) -> str:
    """构造 CSS 模板。多重 font-family fallback 确保中英文都能找到字体。"""
    zh_family = f'"{zh}", "Microsoft YaHei", "Noto Sans SC", "SimHei", sans-serif'
    en_family = f'"{en}", "Consolas", "Courier New", monospace'

    return f"""
@page {{
    size: A4;
    margin: 22mm 18mm 22mm 18mm;
}}

body {{
    font-family: {zh_family};
    font-size: 10.5pt;
    line-height: 1.55;
    color: #2c3e50;
    text-align: left;          /* v1.6: 改 left,justify 会让中英混排时英文间距撑大 */
    word-spacing: normal;
    letter-spacing: normal;
}}

/* 封面 */
.cover {{
    page-break-after: always;
    text-align: center;
    padding-top: 30%;
}}
.cover h1 {{
    font-size: 26pt;
    color: #1a5276;
    margin-bottom: 8mm;
    font-weight: bold;
    font-family: {zh_family};
}}
.cover .subtitle {{
    font-size: 13pt;
    color: #5d6d7e;
    margin-bottom: 12mm;
    font-family: {zh_family};
}}
.cover .meta {{
    font-size: 10pt;
    color: #7f8c8d;
    margin: 3mm 0;
    font-family: {zh_family};
}}
.cover .divider {{
    width: 60mm;
    margin: 8mm auto;
    border: none;
    border-top: 1pt solid #bdc3c7;
}}

/* 标题 */
h1 {{
    font-size: 18pt;
    color: #1a5276;
    margin-top: 8mm;
    margin-bottom: 5mm;
    border-bottom: 1.5pt solid #1a5276;
    padding-bottom: 2mm;
    page-break-before: auto;
    font-family: {zh_family};
}}

h2 {{
    font-size: 15pt;
    color: #2874a6;
    margin-top: 6mm;
    margin-bottom: 3mm;
    border-bottom: 0.5pt solid #aed6f1;
    padding-bottom: 1.5mm;
    font-family: {zh_family};
}}

h3 {{
    font-size: 12.5pt;
    color: #2e86c1;
    margin-top: 5mm;
    margin-bottom: 2.5mm;
    font-family: {zh_family};
}}

h4 {{
    font-size: 11pt;
    color: #5b2c6f;
    margin-top: 4mm;
    margin-bottom: 2mm;
    font-family: {zh_family};
}}

p {{
    margin: 1.2mm 0;
    orphans: 3;
    widows: 3;
    text-indent: 0;
    font-family: {zh_family};
    word-spacing: normal;
    letter-spacing: normal;
}}

blockquote {{
    margin: 4mm 0;
    padding: 3mm 4mm 3mm 8mm;
    background: #f8f9fa;
    border-left: 2.5pt solid #1a5276;
    color: #5d6d7e;
    font-size: 10pt;
    font-family: {zh_family};
}}

strong, b {{
    font-weight: bold;
    color: #1a252f;
    font-family: {zh_family};
}}

code, pre {{
    font-family: {en_family};
    word-spacing: normal;
    letter-spacing: normal;
}}
code {{
    background: #fdf2e9;
    color: #c0392b;
    padding: 0.3mm 1.2mm;
    border-radius: 1.5pt;
    font-size: 9.5pt;
}}
pre {{
    background: #2c3e50;
    color: #ecf0f1;
    padding: 4mm 5mm;
    border-radius: 2pt;
    font-size: 9pt;
    line-height: 1.45;          /* v1.6: 1.5 → 1.45,code 块行间距收紧 */
    margin: 3mm 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    word-spacing: normal;
    letter-spacing: normal;
}}
pre code {{
    background: transparent;
    color: inherit;
    padding: 0;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 3mm 0;
    font-size: 9.5pt;
    font-family: {zh_family};
}}
thead th {{
    background: #1a5276;
    color: white;
    padding: 2.5mm 3mm;
    text-align: left;
    font-weight: bold;
    font-family: {zh_family};
}}
tbody td {{
    padding: 2mm 3mm;
    border-bottom: 0.4pt solid #bdc3c7;
    font-family: {zh_family};
}}
tbody tr:nth-child(even) {{
    background: #f8f9fa;
}}

hr {{
    border: none;
    border-top: 0.5pt solid #bdc3c7;
    margin: 4mm 0;
}}

ul, ol {{
    margin: 2mm 0;
    padding-left: 8mm;
    font-family: {zh_family};
}}
li {{
    margin-bottom: 0.8mm;
    font-family: {zh_family};
}}

a {{
    color: #2e86c1;
    text-decoration: none;
}}

img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 3mm auto;
}}

em, figcaption {{
    color: #7f8c8d;
    font-size: 9.5pt;
    font-style: italic;
    font-family: {zh_family};
}}
"""


# ── HTML 转换 ────────────────────────────────────────────────────────
def _extract_frontmatter(md_text: str) -> tuple[dict, str]:
    if not md_text.startswith("---"):
        return {}, md_text
    parts = md_text.split("---", 2)
    if len(parts) < 3:
        return {}, md_text
    meta = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, parts[2]


def md_to_html(md_text: str, title: str, author: str, source: str | None,
               published: str | None) -> str:
    meta, body = _extract_frontmatter(md_text)
    if not title and "title" in meta:
        title = meta["title"]
    if not source and "source" in meta:
        source = meta["source"]
    if not published and "published" in meta:
        published = meta["published"]

    html_body = markdown.markdown(
        body,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
        output_format="html5",
    )

    css = _build_css(ZH_FONT or "Helvetica", EN_FONT or "Courier")

    cover_html = f"""
    <div class="cover">
        <h1>{title}</h1>
        <div class="subtitle">译文 / Translation</div>
        <hr class="divider">
        <div class="meta">翻译工具：wenxuan-translate</div>
        <div class="meta">生成日期：{published or ''}</div>
        {f'<div class="meta">原文链接：{source}</div>' if source else ''}
        <div class="meta">{author}</div>
    </div>
    """

    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>{css}</style>
</head>
<body>
{cover_html}
{html_body}
</body>
</html>"""

    return full_html


# ── 主流程 ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="wenxuan-translate MD → PDF（xhtml2pdf 后端 v1.5）")
    parser.add_argument("input", help="输入的 Markdown 文件路径")
    parser.add_argument("output", help="输出的 PDF 文件路径")
    parser.add_argument("--title", default=None, help="译文标题（默认从 frontmatter 读）")
    parser.add_argument("--author", default="wenxuan-translate", help="作者/译者名")
    parser.add_argument("--source", default=None, help="原文链接（封面用）")
    parser.add_argument("--published", default=None, help="原文日期（封面用）")
    args = parser.parse_args()

    # 1. 注册字体（Python 端 + xhtml2pdf 端双注册，v1.5 关键）
    zh_font, en_font = _register_fonts()
    if not zh_font:
        print("[ERROR] 找不到系统中文字体。PDF 中文会显示为方块字。", file=sys.stderr)
        sys.exit(1)

    # 2. 读 MD
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"[ERROR] 找不到输入文件: {input_path}", file=sys.stderr)
        sys.exit(1)
    with open(input_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # 3. 转 HTML
    html = md_to_html(
        md_text,
        title=args.title or "译文",
        author=args.author,
        source=args.source,
        published=args.published,
    )

    # 4. 保存中间 HTML（便于调试）
    html_path = os.path.splitext(args.output)[0] + ".html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] HTML 已生成: {html_path}")

    # 5. 转 PDF
    md_dir = os.path.dirname(input_path)
    def _callback(uri, rel):
        return link_callback(uri, md_dir)

    with open(args.output, "wb") as out:
        result = pisa.CreatePDF(
            src=html.encode("utf-8"),
            dest=out,
            encoding="utf-8",
            link_callback=_callback,
        )

    if result.err:
        print(f"[ERROR] PDF 生成失败: {result.err}", file=sys.stderr)
        sys.exit(1)

    size_kb = os.path.getsize(args.output) / 1024
    print(f"[OK] PDF 已生成: {args.output} ({size_kb:.1f} KB)")

    # 6. 验证中文字体是否真的嵌入
    with open(args.output, "rb") as f:
        data = f.read()
    has_yahei = b"YaHei_" in data or b"NotoSC_" in data or b"SimHei_" in data
    if not has_yahei:
        print(f"[WARN] PDF 里没找到中文字体嵌入标记（{zh_font}_），中文可能渲染异常！", file=sys.stderr)
    else:
        print(f"[OK] 中文字体已嵌入: {zh_font}")


if __name__ == "__main__":
    main()
