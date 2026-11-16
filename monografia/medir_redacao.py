#!/usr/bin/env python3
"""Count measurable writing-rule violations in the thesis LaTeX chapters.

Rules and sources: monografia/regras-redacao.md (slides [O] and [C], book [P]).
Usage: python3 medir_redacao.py <chapter.tex> [...] [--details]

Criticality: outside codigo.md (writing aid for the thesis, never cited as evidence).
Counts are a guide for revision, not a verdict: each hit still needs a human read.
"""

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

MAX_SENTENCE_WORDS = 40  # [O] 22, 24
MAX_PARAGRAPH_WORDS = 100  # [O] 22, 24

# Environments whose content is not running text (floats, math, code).
SKIPPED_ENVIRONMENTS = ("table", "figure", "quadro", "equation", "align", "tabular", "longtable", "lstlisting",
                        "verbatim")
# Commands whose argument is not prose: references, struck-out text, colors.
DROPPED_ARGUMENT_COMMANDS = ("ref", "eqref", "autoref", "label", "url", "sout", "includegraphics", "input")
CITATION_COMMANDS = ("cite", "citeonline", "citeauthor", "citeyear", "apud")
# Blocks starting with these are structure, not paragraphs.
STRUCTURAL_COMMANDS = ("chapter", "section", "subsection", "subsubsection", "paragraph", "begin", "end", "label",
                       "FloatBarrier", "clearpage", "newpage", "input", "addcontentsline", "refstepcounter")

PATTERNS = {
    # [O] 56: ele/ela/dele/dela/nele/nela are forbidden.
    "pronome pessoal": r"\b(?:ele|ela|eles|elas|dele|dela|deles|delas|nele|nela|neles|nelas)\b",
    # [O] 56: seu/sua should be removed or replaced by an article.
    "possessivo": r"\b(?:seu|sua|seus|suas)\b",
    # [C] 12: the author acts, not the work.
    "o trabalho como sujeito": r"\b(?:este|o) trabalho (?:desenvolve|realiza|tem|propõe|apresenta|busca|objetiva)\b",
    # [O] 79: quotes only for direct citations.
    "aspas": r"``|''|\"",
    # [O] 84: vague references to the text itself. "acima de", "abaixo do" (compared with a value) are technical.
    "remissão vaga": r"\b(?:supracitad[oa]s?|(?:acima|abaixo)(?! d[eoa]s?\b)|anteriormente|como já (?:dito|explicado)|"
                     r"a seguir)\b",
    # [O] 74: word used as linguistic habit ("possuir" is accepted by the advisor).
    "vício (através)": r"\batravés\b",
}

SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])")


@dataclass
class Paragraph:
    first_line: int
    text: str

    def word_count(self) -> int:
        return len(self.text.split())

    def sentences(self) -> list[str]:
        return [sentence for sentence in SENTENCE_BOUNDARY.split(self.text) if sentence.split()]


@dataclass
class Finding:
    rule: str
    line: int
    excerpt: str


def blank_preserving_lines(match: re.Match) -> str:
    """Replace a removed block by the same number of newlines, so line numbers stay valid."""
    return "\n" * match.group(0).count("\n")


def remove_non_prose(source: str) -> str:
    source = re.sub(r"(?<!\\)%.*", "", source)
    for environment in SKIPPED_ENVIRONMENTS:
        pattern = rf"\\begin\{{{environment}\*?\}}.*?\\end\{{{environment}\*?\}}"
        source = re.sub(pattern, blank_preserving_lines, source, flags=re.S)
    return re.sub(r"\\\[.*?\\\]|\$\$.*?\$\$", blank_preserving_lines, source, flags=re.S)


def is_structural(block: str) -> bool:
    command = re.match(r"\\([A-Za-z]+)", block.lstrip())
    return bool(command) and command.group(1) in STRUCTURAL_COMMANDS


def to_plain_text(block: str) -> str:
    text = re.sub(r"\\(?:textcolor|color)(?:\[[^\]]*\])?\{[^}]*\}", " ", block)
    text = re.sub(rf"\\(?:{'|'.join(DROPPED_ARGUMENT_COMMANDS)})\*?(?:\[[^\]]*\])?\{{[^}}]*\}}", " ", text)
    text = re.sub(rf"\\(?:{'|'.join(CITATION_COMMANDS)})\*?(?:\[[^\]]*\])*\{{[^}}]*\}}", "Autor", text)
    text = re.sub(r"\$[^$]*\$", "X", text)
    text = re.sub(r"\\([_&%#])", r"\1", text)
    text = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}~\\]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def read_paragraphs(path: Path) -> list[Paragraph]:
    source = remove_non_prose(path.read_text(encoding="utf-8"))
    paragraphs = []
    line = 1
    for block in re.split(r"(\n\s*\n)", source):
        if block.strip() and not is_structural(block):
            leading_newlines = len(block) - len(block.lstrip("\n"))
            text = to_plain_text(block)
            if text:
                paragraphs.append(Paragraph(line + leading_newlines, text))
        line += block.count("\n")
    return paragraphs


def find_violations(paragraph: Paragraph) -> list[Finding]:
    findings = []
    if paragraph.word_count() > MAX_PARAGRAPH_WORDS:
        findings.append(Finding(f"parágrafo > {MAX_PARAGRAPH_WORDS} palavras", paragraph.first_line,
                                f"{paragraph.word_count()} palavras: {paragraph.text[:60]}"))
    for sentence in paragraph.sentences():
        if len(sentence.split()) > MAX_SENTENCE_WORDS:
            findings.append(Finding(f"frase > {MAX_SENTENCE_WORDS} palavras", paragraph.first_line,
                                    f"{len(sentence.split())} palavras: {sentence[:60]}"))
    for rule, pattern in PATTERNS.items():
        for match in re.finditer(pattern, paragraph.text, flags=re.I):
            start = max(match.start() - 30, 0)
            findings.append(Finding(rule, paragraph.first_line, paragraph.text[start:match.end() + 30]))
    return findings


def report(path: Path, show_details: bool) -> None:
    paragraphs = read_paragraphs(path)
    findings = [finding for paragraph in paragraphs for finding in find_violations(paragraph)]
    print(f"\n{path.name}: {len(paragraphs)} parágrafos")
    for rule in sorted({finding.rule for finding in findings}):
        print(f"  {rule}: {sum(finding.rule == rule for finding in findings)}")
    if show_details:
        for finding in findings:
            print(f"    l.{finding.line} [{finding.rule}] {finding.excerpt}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--details", action="store_true", help="list each hit with the paragraph's first line")
    arguments = parser.parse_args()
    for path in arguments.files:
        report(path, arguments.details)


if __name__ == "__main__":
    main()
