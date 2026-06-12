"""
PDF to Markdown converter for wenxuan-paper skill.
Uses pymupdf4llm for high-fidelity text extraction and PyMuPDF for images.
"""

import argparse
import os
import sys


def pdf_to_markdown(
    pdf_path: str,
    output_path: str | None = None,
    img_dir: str | None = None,
) -> str:
    """Convert a PDF to Markdown and extract embedded images."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    try:
        import fitz
        import pymupdf4llm
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency. Install it with: "
            "python -m pip install pymupdf4llm pymupdf"
        ) from exc

    md_text = pymupdf4llm.to_markdown(pdf_path)

    output_dir = os.path.dirname(os.path.abspath(output_path)) if output_path else os.getcwd()
    image_dir = os.path.abspath(img_dir or os.path.join(output_dir, "images"))
    os.makedirs(image_dir, exist_ok=True)

    image_refs: list[str] = []
    image_count = 0

    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            for img_index, image in enumerate(page.get_images(full=True), start=1):
                extracted = doc.extract_image(image[0])
                image_name = f"page{page_num}_img{img_index}.{extracted['ext']}"
                image_path = os.path.join(image_dir, image_name)

                with open(image_path, "wb") as image_file:
                    image_file.write(extracted["image"])

                relative_path = os.path.relpath(image_path, output_dir).replace(os.sep, "/")
                image_refs.append(f"![{image_name}]({relative_path})")
                image_count += 1

    if image_refs:
        md_text = f"{md_text.rstrip()}\n\n## Extracted Images\n\n" + "\n\n".join(image_refs)

    if output_path:
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(md_text)
        print(
            f"Markdown saved to: {output_path}; "
            f"{image_count} images extracted to: {image_dir}"
        )

    return md_text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert PDF to Markdown and extract embedded images."
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("-o", "--output", help="Output Markdown file path")
    parser.add_argument("-i", "--img-dir", help="Directory for extracted images")
    args = parser.parse_args()

    try:
        text = pdf_to_markdown(args.pdf_path, args.output, args.img_dir)
        if not args.output:
            print(text)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Conversion failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
