from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str
    doc_id: str
    bab: str
    pasal: int
    ayat: str | None  # "(2)–(3)", "angka 63–70", or None for a whole Pasal
    pages: tuple[int, ...]
    text: str

    def citation(self) -> str:
        where = f"Pasal {self.pasal}"
        if self.ayat:
            where += f" angka {self.ayat[6:]}" if self.ayat.startswith("angka ") else f" ayat {self.ayat}"
        first, last = self.pages[0], self.pages[-1]
        page = f"hal. {first}" if first == last else f"hal. {first}–{last}"
        return f"{where}, {page}"
