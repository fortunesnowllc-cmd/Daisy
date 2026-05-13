#!/usr/bin/env python3
"""Generate a PDF version of the Ladnut Amazon Storefront plan.

The script intentionally avoids third-party dependencies so it can run in the
minimal execution environment used for this repository. It writes a basic PDF
with a standard CJK CID font (STSong-Light) so Chinese and English text can be
rendered by common PDF viewers.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "ladnut_amazon_storefront_plan.md"
OUTPUT = ROOT / "docs" / "ladnut_amazon_storefront_plan.pdf"

PAGE_W = 595.28  # A4 points
PAGE_H = 841.89
MARGIN_X = 54
MARGIN_TOP = 58
MARGIN_BOTTOM = 56


@dataclass
class Line:
    text: str
    size: float = 11
    leading: float = 16
    color: tuple[float, float, float] = (0.12, 0.12, 0.12)
    top_gap: float = 0


def strip_markdown(text: str) -> str:
    text = text.replace("  ", "")
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    return text.strip()


def visual_width(text: str) -> float:
    width = 0.0
    for ch in text:
        if ch == "\t":
            width += 2.0
        elif ord(ch) < 128:
            width += 0.56
        else:
            width += 1.0
    return width


def wrap_text(text: str, max_units: float, prefix: str = "") -> list[str]:
    if not text:
        return [""]

    parts = re.findall(r"[A-Za-z0-9_./:#%&+\-™]+|\s+|.", text)
    lines: list[str] = []
    current = ""
    for part in parts:
        if part.isspace():
            candidate = current + " "
        else:
            candidate = current + part
        allowed = max_units if not lines else max_units - visual_width(prefix)
        if current and visual_width(candidate) > allowed:
            lines.append(current.rstrip())
            current = prefix + (part.strip() if part.isspace() else part)
        else:
            current = candidate
    if current.strip():
        lines.append(current.rstrip())
    return lines or [""]


def parse_markdown(markdown: str) -> list[Line]:
    lines: list[Line] = []
    for raw in markdown.splitlines():
        text = raw.rstrip()
        if not text.strip():
            lines.append(Line("", leading=8))
            continue
        if text.strip() == "---":
            lines.append(Line("─" * 54, size=9, leading=14, color=(0.62, 0.69, 0.63), top_gap=2))
            continue

        leading = 16
        size = 11
        color = (0.13, 0.13, 0.13)
        top_gap = 0
        clean = strip_markdown(text)
        prefix = ""

        if clean.startswith("# "):
            clean = clean[2:].strip()
            size, leading, color, top_gap = 22, 28, (0.08, 0.32, 0.22), 8
        elif clean.startswith("## "):
            clean = clean[3:].strip()
            size, leading, color, top_gap = 16, 22, (0.10, 0.38, 0.26), 12
        elif clean.startswith("### "):
            clean = clean[4:].strip()
            size, leading, color, top_gap = 13.5, 19, (0.12, 0.42, 0.30), 8
        elif clean.startswith("#### "):
            clean = clean[5:].strip()
            size, leading, color, top_gap = 12, 17, (0.23, 0.36, 0.30), 5
        elif clean.startswith("- "):
            clean = "• " + clean[2:].strip()
            prefix = "  "
        elif re.match(r"^\d+\.\s", clean):
            prefix = "   "
        elif clean.startswith("|"):
            size, leading, color = 9.2, 14, (0.12, 0.12, 0.12)

        max_units = (PAGE_W - 2 * MARGIN_X) / size
        for i, wrapped in enumerate(wrap_text(clean, max_units, prefix=prefix)):
            lines.append(Line(wrapped, size=size, leading=leading, color=color, top_gap=top_gap if i == 0 else 0))
    return lines


def paginate(lines: list[Line]) -> list[list[Line]]:
    pages: list[list[Line]] = [[]]
    y = PAGE_H - MARGIN_TOP
    for line in lines:
        needed = line.leading + line.top_gap
        if y - needed < MARGIN_BOTTOM and pages[-1]:
            pages.append([])
            y = PAGE_H - MARGIN_TOP
        pages[-1].append(line)
        y -= needed
    return pages


def pdf_text_hex(text: str) -> str:
    return text.encode("utf-16-be", errors="replace").hex().upper()


def make_stream(page_lines: list[Line], page_no: int, total_pages: int) -> bytes:
    ops: list[str] = ["q"]
    y = PAGE_H - MARGIN_TOP
    for line in page_lines:
        y -= line.top_gap
        if line.text:
            r, g, b = line.color
            ops.append(f"BT /F1 {line.size:.2f} Tf {r:.3f} {g:.3f} {b:.3f} rg 1 0 0 1 {MARGIN_X:.2f} {y:.2f} Tm <{pdf_text_hex(line.text)}> Tj ET")
        y -= line.leading
    footer = f"Ladnut Amazon Storefront Plan · {page_no}/{total_pages}"
    ops.append(f"BT /F1 8.50 Tf 0.45 0.45 0.45 rg 1 0 0 1 {MARGIN_X:.2f} 30.00 Tm <{pdf_text_hex(footer)}> Tj ET")
    ops.append("Q")
    return ("\n".join(ops) + "\n").encode("ascii")


def build_pdf(pages: list[list[Line]]) -> bytes:
    objects: list[bytes] = []

    def add(obj: bytes) -> int:
        objects.append(obj)
        return len(objects)

    catalog_id = add(b"<< /Type /Catalog /Pages 2 0 R >>")
    pages_id = add(b"PLACEHOLDER")
    font_id = add(
        b"<< /Type /Font /Subtype /Type0 /BaseFont /STSong-Light "
        b"/Encoding /UniGB-UCS2-H /DescendantFonts [ << /Type /Font "
        b"/Subtype /CIDFontType0 /BaseFont /STSong-Light /CIDSystemInfo "
        b"<< /Registry (Adobe) /Ordering (GB1) /Supplement 2 >> >> ] >>"
    )
    page_ids: list[int] = []
    for idx, page in enumerate(pages, start=1):
        stream = make_stream(page, idx, len(pages))
        content_id = add(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"endstream")
        page_id = add(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {PAGE_W:.2f} {PAGE_H:.2f}] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>".encode("ascii")
        )
        page_ids.append(page_id)

    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii")

    out = bytearray(b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n")
    offsets = [0]
    for obj_id, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{obj_id} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode("ascii"))
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    out.extend(
        f"trailer\n<< /Size {len(objects)+1} /Root {catalog_id} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return bytes(out)


def main() -> None:
    markdown = SOURCE.read_text(encoding="utf-8")
    pages = paginate(parse_markdown(markdown))
    OUTPUT.write_bytes(build_pdf(pages))
    print(f"Generated {OUTPUT.relative_to(ROOT)} ({len(pages)} pages)")


if __name__ == "__main__":
    main()
