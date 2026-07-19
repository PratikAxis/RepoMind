"""
evaluate_rag.py
---------------
Automated evaluation script for the RepoMind RAG system.

Usage:
    python evaluate_rag.py [--input questions.md] [--output rag_responses.md] [--url http://127.0.0.1:8000]

Reads every question from the input Markdown file, sends each one to the
/query endpoint sequentially, and writes all responses to the output file.
"""

import re
import sys
import time
import argparse
import requests

# ─────────────────────────────────────────────────────────────────────────────
# Configuration defaults
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_INPUT_FILE  = "questions.md"
DEFAULT_OUTPUT_FILE = "rag_responses.md"
DEFAULT_API_BASE    = "http://127.0.0.1:8000"
QUERY_ENDPOINT      = "/query"
REQUEST_TIMEOUT     = 120  # seconds per request


# ─────────────────────────────────────────────────────────────────────────────
# Question parsing
# ─────────────────────────────────────────────────────────────────────────────

def parse_questions(filepath: str) -> list[dict]:
    """
    Parse questions from the Markdown evaluation file.

    Supports two formats found in the input file:
      1. Structured blocks starting with 'Q<N>' followed by metadata lines
         and a 'Question:' field  →  the text after 'Question:' is extracted.
      2. Standard Markdown headings (## Question N) with the question text on
         the following lines.

    Returns a list of dicts: [{"label": "Q1", "text": "..."}, ...]
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    questions = []

    # ── Format 1: structured blocks like the provided input ──────────────────
    # Matches:  Q<N>\n...\nQuestion: <text>\nGround Truth: ...
    structured_pattern = re.compile(
        r'^(Q\d+)\s*\n'                      # Q1, Q2, …
        r'(?:.*?\n)*?'                        # optional metadata lines
        r'Question:\s*(.+?)(?=\n(?:Ground Truth|Relevant Files|Reasoning|Q\d+|$))',
        re.MULTILINE | re.DOTALL,
    )

    for match in structured_pattern.finditer(content):
        label = match.group(1).strip()
        text  = match.group(2).strip()
        questions.append({"label": label, "text": text})

    # ── Format 2: standard Markdown headings (fallback) ───────────────────────
    if not questions:
        heading_pattern = re.compile(
            r'^#{1,3}\s+(Question\s+\d+|Q\d+)\s*\n+'   # ## Question 1
            r'((?:(?!^#{1,3}\s).+\n?)+)',               # body until next heading
            re.MULTILINE,
        )
        for match in heading_pattern.finditer(content):
            label = match.group(1).strip()
            text  = match.group(2).strip()
            if text:
                questions.append({"label": label, "text": text})

    return questions


# ─────────────────────────────────────────────────────────────────────────────
# API interaction
# ─────────────────────────────────────────────────────────────────────────────

def query_rag(api_base: str, question: str) -> tuple[str, bool]:
    """
    Send a single question to the RAG /query endpoint.

    Returns:
        (answer_text, success_bool)
    """
    url = api_base.rstrip("/") + QUERY_ENDPOINT
    payload = {"question": question}

    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        answer = data.get("answer", data.get("response", str(data)))
        return answer, True

    except requests.exceptions.Timeout:
        return f"ERROR:\nRequest timed out after {REQUEST_TIMEOUT} seconds.", False

    except requests.exceptions.ConnectionError as exc:
        return f"ERROR:\nCould not connect to the API at {url}.\nDetails: {exc}", False

    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "?"
        body   = exc.response.text[:500] if exc.response is not None else ""
        return f"ERROR:\nHTTP {status}\n{body}", False

    except Exception as exc:
        return f"ERROR:\n{type(exc).__name__}: {exc}", False


# ─────────────────────────────────────────────────────────────────────────────
# Output writer
# ─────────────────────────────────────────────────────────────────────────────

def build_output(results: list[dict]) -> str:
    """
    Render all Q&A pairs into the required Markdown format.

    results: [{"label": "Q1", "text": "...", "answer": "...", "success": True}, ...]
    """
    lines = ["# RAG Evaluation Results\n", "---\n"]

    for idx, item in enumerate(results, start=1):
        lines.append(f"## {item['label']}\n")
        lines.append(f"**Question**\n")
        lines.append(f"{item['text']}\n")
        lines.append(f"**Response**\n")
        lines.append(f"{item['answer']}\n")
        lines.append("---\n")

    return "\n".join(lines)


def write_output(filepath: str, content: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


# ─────────────────────────────────────────────────────────────────────────────
# Main driver
# ─────────────────────────────────────────────────────────────────────────────

def run_evaluation(input_file: str, output_file: str, api_base: str) -> None:
    # 1. Parse questions
    print(f"\n📂  Reading questions from: {input_file}")
    questions = parse_questions(input_file)

    if not questions:
        print("❌  No questions found in the input file. Aborting.")
        sys.exit(1)

    total = len(questions)
    print(f"✅  Found {total} question(s).\n")

    results      = []
    success_count = 0
    fail_count    = 0

    # 2. Query each question sequentially
    for idx, q in enumerate(questions, start=1):
        print(f"Processing {q['label']} ({idx}/{total})...")

        answer, ok = query_rag(api_base, q["text"])

        if ok:
            success_count += 1
            print("  ✓ Completed\n")
        else:
            fail_count += 1
            # Print first line of error for quick visibility
            first_line = answer.splitlines()[1] if len(answer.splitlines()) > 1 else answer
            print(f"  ✗ Failed — {first_line}\n")

        results.append({
            "label":   q["label"],
            "text":    q["text"],
            "answer":  answer,
            "success": ok,
        })

        # Small courtesy delay between requests (avoids hammering a slow model)
        if idx < total:
            time.sleep(0.5)

    # 3. Write output file
    md_content = build_output(results)
    write_output(output_file, md_content)

    # 4. Summary
    print("=" * 50)
    print(f"Total Questions Processed : {total}")
    print(f"Successful Requests       : {success_count}")
    print(f"Failed Requests           : {fail_count}")
    print(f"Output File               : {output_file}")
    print("=" * 50)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Automated RAG evaluation — sends questions to the /query endpoint and saves responses.",
    )
    parser.add_argument(
        "--input",  default=DEFAULT_INPUT_FILE,
        help=f"Path to the Markdown file containing questions (default: {DEFAULT_INPUT_FILE})",
    )
    parser.add_argument(
        "--output", default=DEFAULT_OUTPUT_FILE,
        help=f"Path for the output Markdown file (default: {DEFAULT_OUTPUT_FILE})",
    )
    parser.add_argument(
        "--url",    default=DEFAULT_API_BASE,
        help=f"Base URL of the RAG API (default: {DEFAULT_API_BASE})",
    )
    args = parser.parse_args()

    run_evaluation(
        input_file  = args.input,
        output_file = args.output,
        api_base    = args.url,
    )


if __name__ == "__main__":
    main()
