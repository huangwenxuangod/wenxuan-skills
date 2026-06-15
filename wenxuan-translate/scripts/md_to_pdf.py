#!/usr/bin/env python3
"""
wenxuan-translate 专用：Markdown → PDF 转换脚本（xhtml2pdf 后端）

特点：
- 纯 Python，无 GTK / wkhtmltopdf 依赖
- 自动注册 Windows 系统中文字体（雅黑 msyh.ttc / Noto Sans SC）
- 支持外链图片（https://...）：自动下载 → base64 嵌入
- 支持本地图片（相对路径）：直接读取
- 中英对照场景友好（虽然 v1.2 已默认纯中文）

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
import urllib3

import markdown
from xhtml2pdf import pisa
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily


# ── 字体注册 ────────────────────────────────────────────────────────
# Windows 系统中文字体优先级：微软雅黑 → Noto Sans SC → SimHei → SimSun
ZH_FONT_CANDIDATES = [
    # (name, path, subfontIndex)
    ("YaHei",   r"C:\Windows\Fonts\msyh.ttc",  0),
    ("NotoSC",  r"C:\Windows\Fonts\NotoSansSC-VF.ttf", None),
    ("NotoSC2", r"C:\Windows\Fonts\Noto Sans SC (TrueType).otf", None),
    ("SimHei",  r"C:\Windows\Fonts\simhei.ttf", None),
    ("SimSun",  r"C:\Windows\Fonts\simsun.ttc", 0),
]

EN_FONT_CANDIDATES = [
    # 等宽字体，给代码块用
    ("Consolas", r"C:\Windows\Fonts\consola.ttf", None),
    ("Courier",  r"C:\Windows\Fonts\cour.ttf",   None),
]

ZH_FONT = None
EN_FONT = None


def _register_fonts():
    """注册 Windows 系统中文字体。返回 (zh_name, en_name) 或 None。"""
    global ZH_FONT, EN_FONT

    for name, path, idx in ZH_FONT_CANDIDATES:
        if not os.path.exists(path):
            continue
        try:
            if idx is not None:
                pdfmetrics.registerFont(TTFont(name, path, subfontIndex=idx))
            else:
                pdfmetrics.registerFont(TTFont(name, path))
            # 让 bold/italic 都指向同一个字体（xhtml2pdf 的中文常见坑：bold 标签 fallback 到拉丁字体）
            registerFontFamily(name, normal=name, bold=name, italic=name, boldItalic=name)
            ZH_FONT = name
            break
        except Exception as e:
            print(f"[WARN] 注册字体 {name} 失败: {e}", file=sys.stderr)
            continue

    for name, path, idx in EN_FONT_CANDIDATES:
        if not os.path.exists(path):
            continue
        try:
            if idx is not None:
                pdfmetrics.registerFont(TTFont(name, path, subfontIndex=idx))
            else:
                pdfmetrics.registerFont(TTFont(name, path))
            EN_FONT = name
            break
        except Exception as e:
            continue

    return ZH_FONT, EN_FONT


# ── 外链图片下载 ────────────────────────────────────────────────────
# 全局缓存：URL → 临时文件路径
_IMAGE_CACHE: dict[str, str] = {}
_CACHE_DIR = None


def _ensure_cache_dir():
    global _CACHE_DIR
    if _CACHE_DIR is None:
        _CACHE_DIR = tempfile.mkdtemp(prefix="wenxuan_pdf_img_")
    return _CACHE_DIR


def _download_image(url: str, timeout: int = 15) -> str | None:
    """下载外链图片到本地临时文件，返回路径；失败返回 None。"""
    if url in _IMAGE_CACHE:
        return _IMAGE_CACHE[url]

    cache_dir = _ensure_cache_dir()
    # 用 URL 的 hash 作为文件名（避免特殊字符问题）
    url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()[:16]
    # 推断扩展名
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
    """
    xhtml2pdf 的 link_callback：把图片 URI 转成本地文件路径。
    支持：https:// 外链、./ 本地相对路径、绝对路径。
    """
    # 已经是本地路径
    if os.path.exists(uri):
        return uri

    # http(s) 外链 → 下载
    if uri.startswith(("http://", "https://")):
        local = _download_image(uri)
        if local:
            return local
        # 下载失败，返回空文件（PDF 里会显示破图占位）
        return ""

    # 相对路径（相对 MD 文件所在目录）
    if rel and not os.path.isabs(uri):
        # 拼绝对路径：rel 是 MD 文件所在目录
        abs_path = os.path.join(rel, uri)
        if os.path.exists(abs_path):
            return abs_path

    return uri


# ── CSS 模板 ────────────────────────────────────────────────────────
def _build_css() -> str:
    zh = ZH_FONT or "Helvetica"
    en = EN_FONT or "Courier"
    return f"""
@page {{
    size: A4;
    margin: 22mm 18mm 22mm 18mm;
}}

body {{
    font-family: "{zh}";
    font-size: 10.5pt;
    line-height: 1.7;
    color: #2c3e50;
    text-align: justify;
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
}}
.cover .subtitle {{
    font-size: 13pt;
    color: #5d6d7e;
    margin-bottom: 12mm;
}}
.cover .meta {{
    font-size: 10pt;
    color: #7f8c8d;
    margin: 3mm 0;
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
}}

h2 {{
    font-size: 15pt;
    color: #2874a6;
    margin-top: 6mm;
    margin-bottom: 3mm;
    border-bottom: 0.5pt solid #aed6f1;
    padding-bottom: 1.5mm;
}}

h3 {{
    font-size: 12.5pt;
    color: #2e86c1;
    margin-top: 5mm;
    margin-bottom: 2.5mm;
}}

h4 {{
    font-size: 11pt;
    color: #5b2c6f;
    margin-top: 4mm;
    margin-bottom: 2mm;
}}

/* 段落 */
p {{
    margin: 1.5mm 0;
    orphans: 3;
    widows: 3;
    text-indent: 0;
}}

/* 引用块 */
blockquote {{
    margin: 4mm 0;
    padding: 3mm 4mm 3mm 8mm;
    background: #f8f9fa;
    border-left: 2.5pt solid #1a5276;
    color: #5d6d7e;
    font-size: 10pt;
}}

/* 粗体 */
strong, b {{
    font-weight: bold;
    color: #1a252f;
}}

/* 行内代码 */
code {{
    font-family: "{en}";
    background: #fdf2e9;
    color: #c0392b;
    padding: 0.3mm 1.2mm;
    border-radius: 1.5pt;
    font-size: 9.5pt;
}}

/* 代码块 */
pre {{
    font-family: "{en}";
    background: #2c3e50;
    color: #ecf0f1;
    padding: 3mm 4mm;
    border-radius: 2pt;
    font-size: 9pt;
    line-height: 1.5;
    margin: 3mm 0;
    white-space: pre-wrap;
    word-wrap: break-word;
}}
pre code {{
    background: transparent;
    color: inherit;
    padding: 0;
}}

/* 表格 */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 3mm 0;
    font-size: 9.5pt;
}}
thead th {{
    background: #1a5276;
    color: white;
    padding: 2.5mm 3mm;
    text-align: left;
    font-weight: bold;
}}
tbody td {{
    padding: 2mm 3mm;
    border-bottom: 0.4pt solid #bdc3c7;
}}
tbody tr:nth-child(even) {{
    background: #f8f9fa;
}}

/* 分隔线 */
hr {{
    border: none;
    border-top: 0.5pt solid #bdc3c7;
    margin: 4mm 0;
}}

/* 列表 */
ul, ol {{
    margin: 2mm 0;
    padding-left: 8mm;
}}
li {{
    margin-bottom: 0.8mm;
}}

/* 链接 */
a {{
    color: #2e86c1;
    text-decoration: none;
}}

/* 图片 */
img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 3mm auto;
}}

/* 强调（figcaption / 注释） */
em, figcaption {{
    color: #7f8c8d;
    font-size: 9.5pt;
    font-style: italic;
}}

/* 元信息行（YAML frontmatter 提取的） */
.frontmatter {{
    background: #fef9e7;
    border-left: 2.5pt solid #f39c12;
    padding: 2mm 4mm;
    margin: 3mm 0;
    font-size: 9pt;
    color: #7d6608;
}}
"""


# ── HTML 转换 ────────────────────────────────────────────────────────
def _extract_frontmatter(md_text: str) -> tuple[dict, str]:
    """提取 YAML frontmatter，剩余正文。"""
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


def md_to_html(md_text: str, title: str, author: str = "wenxuan-translate",
               source: str = None, published: str = None) -> str:
    """MD → 完整 HTML（含封面 + 正文）"""
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

    css = _build_css()

    # 构建封面
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
    parser = argparse.ArgumentParser(description="wenxuan-translate MD → PDF（xhtml2pdf 后端）")
    parser.add_argument("input", help="输入的 Markdown 文件路径")
    parser.add_argument("output", help="输出的 PDF 文件路径")
    parser.add_argument("--title", default=None, help="译文标题（默认从 frontmatter 读）")
    parser.add_argument("--author", default="wenxuan-translate", help="作者/译者名")
    parser.add_argument("--source", default=None, help="原文链接（封面用）")
    parser.add_argument("--published", default=None, help="原文日期（封面用）")
    args = parser.parse_args()

    # 1. 注册字体
    zh_font, en_font = _register_fonts()
    print(f"[INFO] 中文字体: {zh_font or '(未注册，可能中文渲染异常)'}")
    print(f"[INFO] 等宽字体: {en_font or '(未注册)'}")
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
    # link_callback 需要知道 MD 文件所在目录（用于解析 ./images/... 等相对路径）
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


if __name__ == "__main__":
    main()
