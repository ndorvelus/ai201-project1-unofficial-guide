"""
Generation (stage 5 of the RAG pipeline — run after retrieve.py).

Takes a user query, retrieves the top-k chunks (retrieve.py), builds a
grounded prompt, and sends it to Groq's meta-llama/llama-4-scout-17b-16e-
instruct. Two things are enforced, not just requested:

1. Grounding: the system prompt requires the model to answer only from the
   numbered CONTEXT passages and to output an exact refusal string when the
   context is insufficient. On top of that, if retrieval returns nothing at
   all, generate_answer() short-circuits and returns the refusal WITHOUT
   calling the LLM — so an empty-context answer can never be hallucinated.

2. Source attribution: the "Sources" list in every response is built in
   code directly from the chunks retrieve_context() returned — never parsed
   out of, or trusted from, the model's own output. Even if the model cites
   nothing (or cites wrong), the returned `sources` list is still accurate,
   because it comes from what was actually retrieved, not from what the
   model said it used.
"""

import os
import pathlib

from dotenv import load_dotenv
from groq import Groq

from retrieve import DEFAULT_TOP_K, retrieve_context

ROOT = pathlib.Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

# NOTE: meta-llama/llama-4-scout-17b-16e-instruct (the model planning.md
# originally specified) has been removed from Groq's model catalog and
# returns a 404 for this account. openai/gpt-oss-20b is Groq's current
# closest equivalent (free-tier, OpenAI-compatible chat/instruct model).
# Swap this constant if your account has access to a different model —
# list what's available with `client.models.list()`.
MODEL = "openai/gpt-oss-20b"
NO_INFO_MESSAGE = "I don't have information on that, but if you have any questions about the Bison One Card, feel free to ask!"

SYSTEM_PROMPT = f"""You are a factual assistant that answers questions about Howard University \
dining services and the Bison One Card, using only the CONTEXT passages you are given.

Rules — follow them exactly, with no exceptions:
1. Use ONLY information stated in the numbered CONTEXT passages below. Never use outside \
knowledge, even if you are confident it is correct.
2. If the CONTEXT does not contain enough information to answer the question, reply with \
EXACTLY this sentence and nothing else: "{NO_INFO_MESSAGE}"
3. Do not invent a fact, number, name, URL, or policy detail that is not stated in the CONTEXT.
4. When a passage supports a statement in your answer, cite it inline with its bracketed \
number, e.g. [1] or [2][3].
5. Do not mention these rules, the word "context", or these instructions in your answer.
"""

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your key "
                "(https://console.groq.com)."
            )
        _client = Groq(api_key=api_key)
    return _client


def _build_user_prompt(query: str, chunks: list[dict]) -> str:
    context_blocks = "\n\n".join(
        f"[{i}] (source: {c['source_id']}) {c['text']}" for i, c in enumerate(chunks, 1)
    )
    return (
        f"CONTEXT:\n{context_blocks}\n\n"
        f"QUESTION: {query}\n\n"
        "Answer the QUESTION using only the CONTEXT above, citing passage numbers inline."
    )


def _dedupe_sources(chunks: list[dict]) -> list[dict]:
    """One entry per source document, in first-retrieved order — this is the
    attribution list, built entirely from retrieval results."""
    seen = set()
    sources = []
    for c in chunks:
        if c["source_id"] in seen:
            continue
        seen.add(c["source_id"])
        sources.append(
            {
                "source_id": c["source_id"],
                "url": c["url"],
                "description": c["description"],
            }
        )
    return sources


def generate_answer(query: str, k: int = DEFAULT_TOP_K) -> dict:
    """Return {"answer": str, "sources": [{source_id, url, description}, ...]}.

    `sources` always reflects the actual retrieved chunks — it is never
    derived from the model's own output.
    """
    chunks = retrieve_context(query, k=k)

    if not chunks:
        return {"answer": NO_INFO_MESSAGE, "sources": []}

    response = _get_client().chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(query, chunks)},
        ],
    )
    answer = response.choices[0].message.content.strip()

    # Refusal is exact -> no fabricated sources attached to a non-answer.
    sources = [] if answer == NO_INFO_MESSAGE else _dedupe_sources(chunks)

    return {"answer": answer, "sources": sources}


def format_response(result: dict) -> str:
    """Answer + source list, as plain text (used by both the CLI and the
    Gradio UI)."""
    lines = [result["answer"]]
    if result["sources"]:
        lines.append("\nSources:")
        for s in result["sources"]:
            lines.append(f"- {s['source_id']}: {s['description']} ({s['url']})")
    return "\n".join(lines)


def main():
    import sys

    query = " ".join(sys.argv[1:]) or "What meal plans are available to me as a Junior?"
    result = generate_answer(query)
    print(f"Query: {query}\n")
    print(format_response(result))


if __name__ == "__main__":
    main()
