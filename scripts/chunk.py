"""
Chunking (stage 2 of the RAG pipeline — run after clean.py).

Reads every cleaned document in documents/clean/ (boilerplate already
stripped by clean.py) and splits it into overlapping chunks capped at:

    CHUNK_SIZE = 256 tokens (max)
    OVERLAP    = 26 tokens (~10% of 256)

Splitting is recursive: it tries to break on paragraph boundaries first,
then lines, then sentences, then words, only falling back to a hard
token-count cut if a single unit (e.g. one run-on sentence) still exceeds
CHUNK_SIZE on its own. This keeps most chunks ending at a natural boundary
instead of mid-sentence, at the cost of chunk sizes varying (always <=
CHUNK_SIZE, not always exactly CHUNK_SIZE) and overlap being an approximate
~10%, applied by carrying the trailing tokens of one chunk into the next,
rather than an exact token-count splice.

Token counts use tiktoken's cl100k_base encoding (same family as the
embedding/generation models in the pipeline diagram), so a "128-token chunk"
here matches what actually gets sent to the embedding model. Output is a
single JSONL file, one chunk per line, ready to embed and load into a vector
index.
"""

import json
import pathlib
import re

import tiktoken

ROOT = pathlib.Path(__file__).parent.parent
RAW_DIR = ROOT / "documents" / "clean"
OUT_PATH = ROOT / "documents" / "processed" / "chunks.jsonl"

CHUNK_SIZE = 256
OVERLAP = 26  # ~10% of CHUNK_SIZE

ENCODING = tiktoken.get_encoding("cl100k_base")


def parse_raw_file(path: pathlib.Path) -> dict:
    """Split the 'SOURCE_ID / URL / DESCRIPTION / ---' header from the body."""
    raw = path.read_text(encoding="utf-8")
    header, _, body = raw.partition("---\n")
    meta = {}
    for line in header.strip().splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip().lower()] = val.strip()
    return {**meta, "text": body}


def clean_text(text: str) -> str:
    """Normalize whitespace and drop boilerplate/near-empty lines."""
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Drop lines that are just symbols/nav crumbs (e.g. "»", "|", "...").
        if not re.search(r"[A-Za-z0-9]", line):
            continue
        cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


# Tried in order: paragraph break, line break, sentence end, word boundary.
# Whatever doesn't fit CHUNK_SIZE on its own gets recursively split by the
# next, finer-grained separator.
SEPARATORS = ["\n\n", "\n", ". ", " "]


def _token_len(text: str) -> int:
    return len(ENCODING.encode(text))


def _hard_split(text: str, chunk_size: int) -> list[str]:
    """Last resort: a single unit too long even at word granularity — cut by
    raw token count."""
    tokens = ENCODING.encode(text)
    return [
        ENCODING.decode(tokens[i : i + chunk_size])
        for i in range(0, len(tokens), chunk_size)
    ]


def _split_recursive(text: str, separators: list[str], chunk_size: int) -> list[str]:
    if _token_len(text) <= chunk_size:
        return [text]
    if not separators:
        return _hard_split(text, chunk_size)

    sep, rest = separators[0], separators[1:]
    parts = [p for p in text.split(sep) if p]

    # Any part still too big on its own gets split by the next separator down.
    units = []
    for part in parts:
        if _token_len(part) > chunk_size:
            units.extend(_split_recursive(part, rest, chunk_size))
        else:
            units.append(part)

    # Greedily re-merge units (with `sep` reinserted) up to chunk_size tokens,
    # so we don't end up with one chunk per sentence/line when several fit.
    chunks = []
    current = ""
    for unit in units:
        candidate = current + sep + unit if current else unit
        if current and _token_len(candidate) > chunk_size:
            chunks.append(current)
            current = unit
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def _word_aligned_tail(tokens: list[int], overlap: int) -> list[int]:
    """Return ~`overlap` trailing tokens, extended backward if needed so the
    slice starts at a word boundary instead of mid-word.

    cl100k_base often splits a word into multiple sub-word tokens (e.g.
    "enjoy" -> ["en", "joy"]); a token whose decoded text starts a new word
    is prefixed with a space/newline, a continuation token is not. Walking
    back until we hit a space-prefixed token avoids carrying a fragment like
    "joy" into the next chunk with its "en" prefix dropped.
    """
    if not overlap or not tokens:
        return []
    n = len(tokens)
    start = max(0, n - overlap)
    floor = max(0, n - overlap * 2)  # cap the backward search
    while start > floor and not ENCODING.decode([tokens[start]]).startswith((" ", "\n", "\t")):
        start -= 1
    return tokens[start:]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP):
    """Yield recursively-split chunks of `text`, each <= `chunk_size` tokens,
    with the trailing `overlap` tokens of each chunk carried into the next."""
    base_chunks = _split_recursive(text, SEPARATORS, chunk_size)

    carry_tokens: list[int] = []
    for chunk in base_chunks:
        if carry_tokens:
            yield ENCODING.decode(carry_tokens).lstrip() + " " + chunk
        else:
            yield chunk
        tokens = ENCODING.encode(chunk)
        carry_tokens = _word_aligned_tail(tokens, overlap)


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    raw_files = sorted(RAW_DIR.glob("*.txt"))

    total_chunks = 0
    with open(OUT_PATH, "w", encoding="utf-8") as out_f:
        for path in raw_files:
            doc = parse_raw_file(path)
            cleaned = clean_text(doc["text"])
            if not cleaned:
                continue

            for i, chunk in enumerate(chunk_text(cleaned)):
                record = {
                    "chunk_id": f"{doc.get('source_id', path.stem)}-{i}",
                    "source_id": doc.get("source_id", path.stem),
                    "url": doc.get("url", ""),
                    "description": doc.get("description", ""),
                    "chunk_index": i,
                    "n_tokens": len(ENCODING.encode(chunk)),
                    "text": chunk,
                }
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                total_chunks += 1

    print(f"Wrote {total_chunks} chunks from {len(raw_files)} documents to {OUT_PATH}")


if __name__ == "__main__":
    main()
