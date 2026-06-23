"""
Token_Counter.py — compare tokenization across local Ollama models.

Uses each model's actual tokenizer via the Ollama /api/generate endpoint
(raw mode bypasses chat templates so only the input text is counted).

Usage:
    python Token_Counter.py                         # built-in sample text
    python Token_Counter.py "some text here"        # tokenize a string
    python Token_Counter.py path/to/file.txt        # tokenize a file
    python Token_Counter.py "text" --md             # output Markdown table
"""

import sys
import os
import io
import contextlib
from datetime import datetime
from pathlib import Path

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

MODEL_INFO: dict[str, tuple[str, str]] = {
    "qwen2.5:14b-instruct-q4_K_M": ("14B", "8 GB"),
    "gemma2:9b":                    ("9B",  "5 GB"),
    "llama3.1:8b-instruct-q8_0":   ("8B",  "7 GB"),
    "mistral:7b-instruct-q8_0":    ("7B",  "7 GB"),
    "llama3.2:1b":                  ("1B",  "1 GB"),
    "phi3:mini":                    ("3.8B","2 GB"),
}

MODELS = list(MODEL_INFO.keys())

SAMPLE_TEXT = (
    "Tokenizasyon, gereksiz veya 123456 gibi alışılmadık kelimeler için basit değildir. "
    "The quick brown fox jumps over the lazy dog."
)

console = Console(highlight=False)


def count_tokens_ollama(model: str, text: str) -> int:
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": text,
            "stream": False,
            "raw": True,
            "options": {"num_predict": 1},
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["prompt_eval_count"]


def run_all(text: str) -> list[tuple[str, int | str]]:
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

    return [(m, results[m]) for m in MODELS]


def print_rich(text: str, source: str, results: list[tuple[str, int | str]]) -> None:
    console.print(f"\n[bold]Source:[/bold] {source}")
    console.print(f"[bold]Length:[/bold] {len(text)} characters")
    console.print(f"[bold]Text:[/bold] {text[:120]}{'...' if len(text) > 120 else ''}\n")

    ref = Table(title="Models Under Test", show_lines=False)
    ref.add_column("Model", style="cyan", no_wrap=True)
    ref.add_column("Params", justify="right")
    ref.add_column("Disk", justify="right")
    for model, _ in results:
        params, size = MODEL_INFO.get(model, ("?", "?"))
        ref.add_row(model, params, size)
    console.print(ref)

    table = Table(title="Token Count per Ollama Model", show_lines=True)
    table.add_column("Model", style="cyan", no_wrap=True)
    table.add_column("Params", justify="right")
    table.add_column("Tokens", justify="right", style="bold green")

    for model, count in results:
        params, _ = MODEL_INFO.get(model, ("?", "?"))
        if isinstance(count, int):
            table.add_row(model, params, str(count))
        else:
            table.add_row(model, params, f"[red]{count}[/red]")

    console.print(table)
    console.print("[dim]Note: counts include the BOS token (off by 1 vs raw subword count).[/dim]\n")


def print_md(text: str, source: str, results: list[tuple[str, int | str]]) -> None:
    print(f"## Token Count Results\n")
    print(f"**Source:** {source}  ")
    print(f"**Length:** {len(text)} characters  ")
    print(f"**Text:** `{text[:120]}{'...' if len(text) > 120 else ''}`\n")
    print("### Models Under Test\n")
    print("| Model | Params | Disk |")
    print("|-------|-------:|-----:|")
    for model, _ in results:
        params, size = MODEL_INFO.get(model, ("?", "?"))
        print(f"| `{model}` | {params} | {size} |")
    print()
    print("### Results\n")
    print("| Model | Params | Tokens |")
    print("|-------|-------:|-------:|")
    for model, count in results:
        params, _ = MODEL_INFO.get(model, ("?", "?"))
        print(f"| `{model}` | {params} | {count} |")
    print("\n> Note: counts include the BOS token (off by 1 vs raw subword count).")


def main() -> None:
    args = sys.argv[1:]
    md = "--md" in args
    args = [a for a in args if a != "--md"]

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

    if not md:
        console.print("[dim]Querying Ollama models in parallel...[/dim]")

    results = run_all(text)

    if md:
        print_md(text, source, results)
    else:
        print_rich(text, source, results)

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"token_counter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print_md(text, source, results)
    path.write_text(buf.getvalue(), encoding="utf-8")
    console.print(f"[dim]Saved → {path}[/dim]")


if __name__ == "__main__":
    main()
