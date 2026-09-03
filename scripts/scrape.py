"""
Document Ingestion (stage 1 of the RAG pipeline).

Reads data/sources.csv and fetches each row with the strategy in its
`fetch` column, saving cleaned text to data/raw/<id>.txt with a metadata
header:

  - "requests"  : plain HTTP GET + BeautifulSoup text extraction. Fine for
                  server-rendered pages (auxiliary.howard.edu,
                  studentaffairs.howard.edu).
  - "playwright": headless Chromium render, then extract visible text. Needed
                  for howard.mydininghub.com, which is a client-side-rendered
                  SPA — a plain GET only returns an empty shell.
  - "reddit"    : Reddit's public .rss feed for the subreddit (no API key
                  required). www.reddit.com blocks unauthenticated JSON API
                  requests from server IPs (redirects to a login wall), but
                  the Atom/RSS feed at /r/<sub>/.rss is still open and
                  returns the latest ~25 posts with title + body HTML. Each
                  post becomes its own raw file (id "<source_id>-<post_id>")
                  so it chunks independently.
"""

import csv
import html
import pathlib
import re
import sys
import time
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).parent.parent
SOURCES_CSV = ROOT / "documents" / "sources.csv"
RAW_DIR = ROOT / "documents" / "raw"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

STRIP_TAGS = ["script", "style", "noscript", "svg", "header", "footer", "nav"]

ATOM_NS = {"a": "http://www.w3.org/2005/Atom"}


def html_to_text(markup: str) -> str:
    soup = BeautifulSoup(markup, "html.parser")
    for tag in soup.find_all(STRIP_TAGS):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def fetch_requests(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return html_to_text(resp.text)


def fetch_playwright(url: str) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=HEADERS["User-Agent"])
        page.goto(url, wait_until="networkidle", timeout=30000)
        # Give client-side rendering a moment to finish painting content.
        page.wait_for_timeout(1500)
        rendered_html = page.content()
        browser.close()
    return html_to_text(rendered_html)


def fetch_reddit_posts(subreddit_url: str) -> list[dict]:
    """Return [{post_id, title, text}, ...] from a subreddit's .rss feed."""
    rss_url = subreddit_url.rstrip("/") + "/.rss"
    resp = requests.get(rss_url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)

    posts = []
    for entry in root.findall("a:entry", ATOM_NS):
        title = entry.find("a:title", ATOM_NS).text or ""
        link_el = entry.find("a:link", ATOM_NS)
        link = link_el.get("href") if link_el is not None else ""
        content_el = entry.find("a:content", ATOM_NS)
        body_html = content_el.text or "" if content_el is not None else ""
        body_text = html_to_text(html.unescape(body_html))
        post_id = link.rstrip("/").split("/")[-1] if link else title[:20]
        posts.append({"post_id": post_id, "title": title, "url": link, "text": body_text})
    return posts


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with open(SOURCES_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        doc_id, url, desc, strategy = row["id"], row["url"], row["description"], row["fetch"]
        print(f"[{doc_id}] fetching ({strategy}) {url} ...", file=sys.stderr)

        try:
            if strategy == "requests":
                text = fetch_requests(url)
                write_doc(doc_id, url, desc, text)

            elif strategy == "playwright":
                text = fetch_playwright(url)
                write_doc(doc_id, url, desc, text)

            elif strategy == "reddit":
                posts = fetch_reddit_posts(url)
                print(f"[{doc_id}] got {len(posts)} posts from subreddit feed", file=sys.stderr)
                for post in posts:
                    body = f"{post['title']}\n\n{post['text']}".strip()
                    write_doc(f"{doc_id}-{post['post_id']}", post["url"] or url, desc, body)

            else:
                print(f"[{doc_id}] SKIPPED: unknown fetch strategy '{strategy}'", file=sys.stderr)
                continue

        except Exception as exc:
            print(f"[{doc_id}] FAILED: {exc}", file=sys.stderr)
            continue

        time.sleep(1)  # be polite to the server


def write_doc(doc_id: str, url: str, desc: str, text: str):
    if len(text) < 200:
        print(
            f"[{doc_id}] WARNING: only {len(text)} chars extracted — check manually",
            file=sys.stderr,
        )
    out_path = RAW_DIR / f"{doc_id}.txt"
    header = f"SOURCE_ID: {doc_id}\nURL: {url}\nDESCRIPTION: {desc}\n---\n"
    out_path.write_text(header + text, encoding="utf-8")


if __name__ == "__main__":
    main()
