"""Turn the regulation PDF into one chunk per Pasal, split by ayat or numbered item when long."""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path

from pypdf import PdfReader

from rag.models import Chunk

# OCR turns "Pasal 37" into "Pasa137" or "Fasal 55"; the sequence check below rejects
# cross-references such as a line that reads "Pasal 40." inside Pasal 44.
PASAL_RE = re.compile(r"[PF]asa[l1I]?\s*([0-9lIO]{1,3})\.?")
BAB_RE = re.compile(r"BAB\s+([IVXL]+|W)")
BAB_OCR_FIXES = {"BAB W": "BAB VI"}
SECTION_RE = re.compile(r"(Bagian|Paragraf)\s+\S+")
AYAT_RE = re.compile(r"\((\d+)\)\s")
ITEM_RE = re.compile(r"(\d+)\.\s")


def extract_pages(pdf_path: Path) -> list[str]:
    return [page.extract_text() or "" for page in PdfReader(str(pdf_path)).pages]


def _pasal_number(line: str) -> int | None:
    m = PASAL_RE.fullmatch(line)
    if not m:
        return None
    digits = m.group(1).translate(str.maketrans("lIO", "110"))
    return int(digits) if digits.isdigit() else None


def _split_units(lines: list[tuple[int, str]]) -> list[tuple[str | None, list[tuple[int, str]]]]:
    """Split a Pasal body into ayat, or into numbered items when it has no ayat."""
    for kind, pattern in (("ayat", AYAT_RE), ("angka", ITEM_RE)):
        starts = [i for i, (_, text) in enumerate(lines) if pattern.match(text)]
        if starts:
            # An intro sentence before the first ayat/item stays with that first unit.
            bounds = [0] + starts[1:] + [len(lines)]
            units = []
            for i, (a, b) in enumerate(zip(bounds, bounds[1:])):
                label = pattern.match(lines[starts[i]][1]).group(1)
                units.append((f"{kind}:{label}", lines[a:b]))
            return units
    return [(None, lines)]


def _label(labels: list[str]) -> str | None:
    if not labels or labels[0] is None:
        return None
    kind = labels[0].split(":")[0]
    first, last = labels[0].split(":")[1], labels[-1].split(":")[1]
    if kind == "ayat":
        return f"({first})" if first == last else f"({first})–({last})"
    return f"angka {first}" if first == last else f"angka {first}–{last}"


def _pack(pasal: int, units, max_chars: int):
    """Greedily group units into chunks that stay under max_chars including the heading."""
    heading = f"Pasal {pasal}"
    groups, current, size = [], [], len(heading)
    for label, lines in units:
        text = "\n".join(t for _, t in lines)
        if len(text) + len(heading) + 1 > max_chars:
            # A single oversized unit: cut it into line groups of its own.
            if current:
                groups.append(current)
                current, size = [], len(heading)
            piece, piece_size = [], len(heading)
            for line in lines:
                if piece and piece_size + len(line[1]) + 1 > max_chars:
                    groups.append([(label, piece)])
                    piece, piece_size = [], len(heading)
                piece.append(line)
                piece_size += len(line[1]) + 1
            if piece:
                groups.append([(label, piece)])
            continue
        if current and size + len(text) + 1 > max_chars:
            groups.append(current)
            current, size = [], len(heading)
        current.append((label, lines))
        size += len(text) + 1
    if current:
        groups.append(current)
    return groups


def chunk_regulation(pages: list[str], doc_id: str, max_chars: int = 1800) -> list[Chunk]:
    pasals: list[dict] = []
    bab, expect_bab_title, skip_title = "", False, False
    for page_no, page in enumerate(pages, start=1):
        for raw in page.split("\n"):
            line = " ".join(raw.split())
            if not line or line == str(page_no):
                continue
            if expect_bab_title:
                bab, expect_bab_title = f"{bab} {line}", False
                continue
            if skip_title:
                skip_title = False
                continue
            if BAB_RE.fullmatch(line):
                bab, expect_bab_title = BAB_OCR_FIXES.get(line, line), True
                continue
            if SECTION_RE.fullmatch(line):
                skip_title = True
                continue
            number = _pasal_number(line)
            if number is not None and number == (pasals[-1]["pasal"] + 1 if pasals else 1):
                pasals.append({"pasal": number, "bab": bab, "lines": []})
                continue
            if pasals:
                pasals[-1]["lines"].append((page_no, line))

    chunks = []
    for p in pasals:
        heading = f"Pasal {p['pasal']}"
        units = _split_units(p["lines"])
        for n, group in enumerate(_pack(p["pasal"], units, max_chars), start=1):
            lines = [line for _, unit_lines in group for line in unit_lines]
            body = "\n".join(t for _, t in lines)
            body = re.sub(r"(\w)-\n(\w)", r"\1\2", body)  # rejoin words hyphenated across lines
            chunks.append(
                Chunk(
                    id=f"{doc_id}-p{p['pasal']}-{n}",
                    doc_id=doc_id,
                    bab=p["bab"],
                    pasal=p["pasal"],
                    ayat=_label([label for label, _ in group]) if len(units) > 1 else None,
                    pages=tuple(sorted({pg for pg, _ in lines})) or (0,),
                    text=f"{heading}\n{body}",
                )
            )
    return chunks


def write_chunks(chunks: list[Chunk], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")


def read_chunks(path: Path) -> list[Chunk]:
    with open(path, encoding="utf-8") as f:
        return [Chunk(**{**row, "pages": tuple(row["pages"])}) for row in map(json.loads, f)]
