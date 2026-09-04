"""
Query Interface (stage 5 of the RAG pipeline — the front end for generate.py).

A simple interactive command-line loop: type a question, get a grounded
answer plus its source list, repeat. Run with:

    python3 scripts/cli.py
"""

from generate import DEFAULT_TOP_K, generate_answer, format_response

BANNER = (
    "The Unofficial Guide — Howard Dining\n"
    "Ask about Howard University dining, meal plans, or the Bison One Card.\n"
    "Answers are grounded only in the scraped source documents — type 'quit' or 'exit' to stop.\n"
)


def main():
    print(BANNER)
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            break

        result = generate_answer(question, k=DEFAULT_TOP_K)
        print()
        print(format_response(result))
        print()


if __name__ == "__main__":
    main()
