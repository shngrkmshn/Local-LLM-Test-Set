"""
Token_Counter.py — compare tokenization across local Ollama models.

Uses each model's actual tokenizer via the Ollama /api/generate endpoint
(raw mode bypasses chat templates so only the input text is counted).

Usage:
    python Token_Counter.py                         # built-in sample text
    python Token_Counter.py "some text here"        # tokenize a string
    python Token_Counter.py path/to/file.txt        # tokenize a file
"""

import sys
import os

# Force UTF-8 output on Windows so Turkish/non-ASCII chars don't break cp1252
os.environ.setdefault("PYTHONUTF8", "1")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from rich.console import Console
from rich.table import Table

OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS = [
    "qwen2.5:14b-instruct-q4_K_M",
    "gemma2:9b",
    "llama3.1:8b-instruct-q8_0",
    "mistral:7b-instruct-q8_0",
    "llama3.2:1b",
    "phi3:mini",
]

SAMPLE_TEXT = (
    "Tokenizasyon, gereksiz veya 123456 gibi alışılmadık kelimeler için basit değildir. "
    "The quick brown fox jumps over the lazy dog."
)

console = Console(highlight=False)


def count_tokens_ollama(model: str, text: str) -> int:
    """Return the raw token count for text under the given Ollama model."""
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": text,
            "stream": False,
            "raw": True,          # skip chat template — count only input tokens
            "options": {"num_predict": 1},
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["prompt_eval_count"]


def run_all(text: str) -> list[tuple[str, int | str]]:
    """Query all models in parallel; return (model, count_or_error) list."""
    results: dict[str, int | str] = {}

    def query(model: str):
        try:
            return model, count_tokens_ollama(model, text)
        except Exception as exc:
            return model, f"ERROR: {exc}"

    with ThreadPoolExecutor(max_workers=len(MODELS)) as pool:
        futures = {pool.submit(query, m): m for m in MODELS}
        for future in as_completed(futures):
            model, result = future.result()
            results[model] = result

    # Return in original MODELS order
    return [(m, results[m]) for m in MODELS]


def print_table(text: str, results: list[tuple[str, int | str]]) -> None:
    table = Table(title="Token Count per Ollama Model", show_lines=True)
    table.add_column("Model", style="cyan", no_wrap=True)
    table.add_column("Tokens", justify="right", style="bold green")

    for model, count in results:
        if isinstance(count, int):
            table.add_row(model, str(count))
        else:
            table.add_row(model, f"[red]{count}[/red]")

    console.print(table)
    console.print(
        "[dim]Note: counts include the BOS token (off by 1 vs raw subword count).[/dim]\n"
    )


def main() -> None:
    args = sys.argv[1:]

    if args:
        candidate = Path(args[0])
        if candidate.exists():
            text = candidate.read_text(encoding="utf-8")
            source = str(candidate)
        else:
            text = " ".join(args)
            source = "command-line argument"
    else:
        text = SAMPLE_TEXT
        source = "built-in sample"

    console.print(f"\n[bold]Source:[/bold] {source}")
    console.print(f"[bold]Length:[/bold] {len(text)} characters")
    console.print(
        f"[bold]Text:[/bold] {text[:120]}{'...' if len(text) > 120 else ''}\n"
    )

    console.print("[dim]Querying Ollama models in parallel...[/dim]\n")
    results = run_all(text)
    print_table(text, results)


if __name__ == "__main__":
    main()
