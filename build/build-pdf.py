#!/usr/bin/env python3
"""Markdown -> HTML -> PDF (Chrome headless) with truncation guards.

Guards against the usual PDF truncation causes:
  - wide tables clipped at the right margin  -> fixed layout + word-break
  - table headers lost on page split         -> thead repeats per page
  - rows sliced mid-row                      -> tr break-inside avoid
  - long code lines overflowing              -> pre white-space pre-wrap
  - missing CJK glyphs                       -> explicit Korean font stack
  - content cut at page end                  -> verify every heading in output
"""
import os
import re
import subprocess
import sys

import markdown
from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARG = sys.argv[1] if len(sys.argv) > 1 else "v0.6"
_IS_FILE = os.path.exists(os.path.join(ROOT, f"{ARG}.md"))
BASE = ARG if (_IS_FILE or ARG.startswith("proposal-")) else f"proposal-methodology-{ARG}"
SRC = os.path.join(ROOT, f"{BASE}.md")
HTML = os.path.join(ROOT, "build", f"{BASE}.html")
PDF = os.path.join(ROOT, "build", f"{BASE}.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 15mm 14mm 16mm 14mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  font-family: "Apple SD Gothic Neo", "Helvetica Neue", Arial, sans-serif;
  font-size: 9.6pt; line-height: 1.62; color: #111; margin: 0;
  word-break: keep-all; overflow-wrap: anywhere;
}
h1 { font-size: 19pt; line-height: 1.28; margin: 0 0 2mm; letter-spacing: -0.4pt; }
h2 { font-size: 12.4pt; margin: 6mm 0 2.2mm; padding-bottom: 1.4mm;
     border-bottom: 1.1pt solid #111; break-after: avoid; break-inside: avoid; }
h2 + h3 { margin-top: 3mm; }
h3 { font-size: 10.6pt; margin: 5mm 0 1.8mm; break-after: avoid; }
p { margin: 0 0 2.2mm; text-align: left; orphans: 2; widows: 2; }
ul, ol { margin: 0 0 2.4mm; padding-left: 5.2mm; }
li { margin-bottom: 1.1mm; }
strong { font-weight: 700; }
hr { border: 0; border-top: 0.5pt solid #ccc; margin: 5mm 0; }
table {
  width: 100%; border-collapse: collapse; margin: 2mm 0 3.4mm;
  table-layout: fixed; font-size: 8.5pt; line-height: 1.45;
}
thead { display: table-header-group; }
tfoot { display: table-footer-group; }
tr { break-inside: avoid; page-break-inside: avoid; }
th, td {
  border: 0.5pt solid #999; padding: 1.3mm 1.6mm; vertical-align: top;
  text-align: left; overflow-wrap: anywhere; word-break: keep-all;
}
th { background: #efefef; font-weight: 700; }
td:first-child { font-weight: 600; }
pre {
  background: #f6f6f6; border: 0.5pt solid #ddd; border-radius: 1.2mm;
  padding: 2.4mm 3mm; margin: 2mm 0 3mm; overflow: hidden;
  white-space: pre-wrap; overflow-wrap: anywhere; word-break: break-word;
  font-family: "SF Mono", Menlo, monospace; font-size: 7.6pt; line-height: 1.5;
  break-inside: avoid;
}
code { font-family: "SF Mono", Menlo, monospace; font-size: 8.3pt; }
p code, li code, td code { background: #f1f1f1; padding: 0 0.8mm; border-radius: 0.8mm; }
div.pb { break-after: page; page-break-after: always; height: 0; }
.keep { break-inside: avoid; }
div.meta table { font-size: 8.6pt; }
div.meta td:first-child { width: 26%; }
h1 + h2 { margin-top: 0; border-bottom: 0; font-size: 12.8pt; font-weight: 500; color: #444; }
"""


def to_html(md_text: str) -> str:
    body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"],
        output_format="html5",
    )
    return (
        "<!doctype html><html lang='ko'><head><meta charset='utf-8'>"
        "<title>워커힐 호텔 에이전트 시뮬레이션 방법론</title>"
        f"<style>{CSS}</style></head><body>{body}</body></html>"
    )


def build_pdf() -> None:
    subprocess.run(
        [
            CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=10000",
            f"--print-to-pdf={PDF}", f"file://{HTML}",
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def _norm(s: str) -> str:
    """Normalize extracted PDF text and markdown source to a comparable form."""
    s = s.replace("\u200b", "")
    s = re.sub(r"[\s\x00-\x1f\x7f]", "", s)      # Chrome emits \x01 in place of spaces
    s = re.sub(r"[*`#|]", "", s)
    return s


def _max_table_cols(md_text: str) -> int:
    """Largest column count among markdown table rows (fenced code excluded)."""
    best, in_code = 0, False
    for line in md_text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        s = line.strip()
        if s.startswith("|") and s.endswith("|") and len(s) > 1:
            best = max(best, len(s.split("|")) - 2)
    return best


def _right_margin_stats() -> tuple[float, int]:
    """Smallest remaining right margin across pages, and the page it occurs on."""
    import fitz

    doc = fitz.open(PDF)
    width = doc[0].rect.width
    min_gap, min_page = 1e9, 0
    for i, page in enumerate(doc, 1):
        xs = [b[2] for b in page.get_text("blocks") if (b[4] or "").strip()]
        if not xs:
            continue
        gap = width - max(xs)
        if gap < min_gap:
            min_gap, min_page = gap, i
    return min_gap, min_page


def verify(md_text: str) -> int:
    reader = PdfReader(PDF)
    text = "\n".join((p.extract_text() or "") for p in reader.pages)
    flat = _norm(text)

    headings = re.findall(r"^(#{2,3})\s+(.+)$", md_text, flags=re.M)
    missing = []
    for _, h in headings:
        token = _norm(h)
        token = re.sub(r"^(?:\d+\.)+", "", token)[:12]
        if token and token not in flat:
            missing.append(h)

    m = re.search(r"<!--\s*anchors:(.*?)-->", md_text, flags=re.S)
    parsed = [a.strip() for a in m.group(1).split("|") if a.strip()] if m else []
    anchors = parsed
    if not anchors:
        anchors = [
        "진화가 허용되는 에이전트 범위를 정한 규칙",
        "이 절차는 내장된 반증 루프다",
        "재생성률 20% 초과 시 생성 프롬프트를 재설계한다",
        "동결 모델 + 외부 메모리",
        "코드·프롬프트 미공개",
        "본 과업은 메커니즘을 재구현하며",
        "분포는 샘플러가 보장한다",
        "벤치마크의 행동 규율을 훼손할 수 있기 때문이다",
        "우선순위는 모순 우선이다",
        "ε_z는 고르는 값이 아니라 계산하는 값이다",
        "유의하게 초과한 개수",
        "현행 정찰가 정책 + 예외 승인 절차",
        "사전 등록 잠금",
        "압축 경고",
        "메커니즘 재구현",
        "시뮬레이터는 예약 시스템에 쓰기를 하지 않는다",
        "총 22주",
        "대리 지표 값은 실측 로그에서 산출하고 문서에 고정한다",
        "본 문서는 지표를 새로 제안하지 않는다",
        "기권은 본 과업의 발명이 아니다",
        "보정은 선택이 아니라 필수다",
        "의도적으로 반대 방향을 택한 지점",
        "LLM별 가격 민감도 10배 차이",
        "계획 표본이 아니라 실제 방문 수다",
        ]
    anchor_fail = [a for a in anchors if _norm(a) not in flat]

    max_cols = _max_table_cols(md_text)
    min_gap, gap_page = _right_margin_stats()

    print(f"pages      : {len(reader.pages)}")
    print(f"chars      : {len(text)}")
    print(f"headings   : {len(headings)} checked, {len(missing)} missing")
    print(f"anchors    : {len(anchors)} checked, {len(anchor_fail)} missing")
    print(f"table cols : max {max_cols} (limit 4)")
    print(f"right gap  : min {min_gap:.1f}pt (page {gap_page}, margin 39.7pt)")
    for h in missing:
        print(f"  MISSING HEADING: {h}")
    for a in anchor_fail:
        print(f"  MISSING ANCHOR : {a}")
    if max_cols > 4:
        print(f"  TABLE TOO WIDE : {max_cols} columns")
    if min_gap < 20:
        print(f"  RIGHT OVERFLOW : page {gap_page} gap {min_gap:.1f}pt")
    ok = not missing and not anchor_fail and max_cols <= 4 and min_gap >= 20
    return 0 if ok else 1


def main() -> None:
    os.makedirs(os.path.dirname(HTML), exist_ok=True)
    print(f"source     : {SRC}")
    md_text = open(SRC, encoding="utf-8").read()
    open(HTML, "w", encoding="utf-8").write(to_html(md_text))
    build_pdf()
    size = os.path.getsize(PDF)
    print(f"pdf        : {PDF} ({size/1024:.0f} KB)")
    sys.exit(verify(md_text))


if __name__ == "__main__":
    main()
