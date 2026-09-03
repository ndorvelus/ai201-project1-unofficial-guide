"""
Boilerplate removal (runs between scrape.py and chunk.py).

scrape.py's html_to_text() already strips actual HTML tags, but the visible
text it extracts still carries site chrome that isn't part of the substantive
content: nav/skip links, cookie-consent banners, newsletter signup widgets,
UI button labels ("Retry", "Get Directions"), and, for Reddit, the
submitted-by/link/comments footer on every post. This pass removes that,
leaving reviews, opinions, descriptions, hours, prices, and other content a
retrieval system should actually match against.

Reads documents/raw/*.txt, writes documents/clean/*.txt (same metadata
header, cleaned body). Raw files are left untouched as the unmodified record
of what was scraped.
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).parent.parent
RAW_DIR = ROOT / "documents" / "raw"
CLEAN_DIR = ROOT / "documents" / "clean"

# Lines that are pure site chrome no matter which page they appear on:
# nav/skip links, cookie/consent UI, newsletter widget, filter/sort controls,
# error-state buttons. Matched exact (case-insensitive, after stripping).
BOILERPLATE_LINES = {
    # nav / accessibility chrome
    "skip to content",
    "skip to chat",
    "skip to main content",
    "web accessibility support",
    "section menu",
    "bison one card",  # breadcrumb repeated on every auxiliary.howard.edu page
    # SPA error-state / filter / sort controls
    "retry",
    "return to home",
    "show all",
    "open now",
    "sort by distance",
    "get directions",
    # newsletter signup widget
    "dining with us?",
    "enter your email and get rewarded!",
    "*= required field",
    "email",
    "*",
    "join",
    "privacy policy",
    # generic link labels left over after tag stripping
    "read more",
    "share",
    "read tips & tools",
}

# The cookie-consent banner is one long run of paragraphs; drop the whole
# span rather than trying to list every sentence in it.
COOKIE_BANNER_RE = re.compile(
    r"The MyDiningHub family of websites uses cookies\..*?Save My Preferences",
    re.DOTALL,
)

# Reddit's per-post footer: "submitted by\n/u/<user>\n[link]\n[comments]"
REDDIT_FOOTER_RE = re.compile(
    r"\s*submitted by\s*/u/\S+\s*\[link\]\s*\[comments\]\s*\Z",
    re.IGNORECASE,
)

# The page's own <title> text, e.g. "Locations & Menus - Howard University"
# or "Laundry | Office of Auxiliary Enterprises" — redundant with the
# SOURCE_ID/URL/DESCRIPTION header already attached to each document.
PAGE_TITLE_RE = re.compile(
    r"^.+(-\s*Howard University|\|\s*Office of Auxiliary Enterprises|\|\s*Howard University Student Affairs)\s*$"
)


def parse_raw_file(path: pathlib.Path) -> tuple[str, str]:
    raw = path.read_text(encoding="utf-8")
    header, _, body = raw.partition("---\n")
    return header, body


def drop_repeated_blocks(lines: list[str]) -> list[str]:
    """Collapse a consecutive run of lines that repeats immediately after
    itself (e.g. a promo block the site renders 3x in a row) to one copy."""
    out = []
    i = 0
    n = len(lines)
    while i < n:
        matched = False
        max_block = min(20, (n - i) // 2)
        for block_len in range(max_block, 2, -1):
            block = lines[i : i + block_len]
            if lines[i + block_len : i + 2 * block_len] == block:
                out.extend(block)
                j = i + block_len
                while lines[j : j + block_len] == block:
                    j += block_len
                i = j
                matched = True
                break
        if not matched:
            out.append(lines[i])
            i += 1
    return out


def clean_body(body: str) -> str:
    body = COOKIE_BANNER_RE.sub("", body)
    body = REDDIT_FOOTER_RE.sub("", body)

    lines = [line.strip() for line in body.splitlines()]
    lines = [line for line in lines if line]
    lines = [line for line in lines if line.lower() not in BOILERPLATE_LINES]
    lines = [line for line in lines if not PAGE_TITLE_RE.match(line)]
    lines = drop_repeated_blocks(lines)

    return "\n".join(lines).strip()


def main():
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    raw_files = sorted(RAW_DIR.glob("*.txt"))

    for path in raw_files:
        header, body = parse_raw_file(path)
        cleaned = clean_body(body)
        out_path = CLEAN_DIR / path.name
        out_path.write_text(header + "---\n" + cleaned + "\n", encoding="utf-8")

    print(f"Cleaned {len(raw_files)} documents into {CLEAN_DIR}")


if __name__ == "__main__":
    main()
