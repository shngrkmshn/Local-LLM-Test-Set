"""
truncation_test.py — detect whether Ollama silently truncates prompts.

Sends a document that is clearly larger than Ollama's default context window
(4 096 tokens) WITHOUT setting num_ctx, then compares
prompt_eval_count (tokens Ollama actually processed) against our estimate.
A big gap means Ollama truncated the prompt silently.

Usage:
    python truncation_test.py                        # test all models, ~6 000-word doc
    python truncation_test.py --models llama3.2:1b   # single model
    python truncation_test.py --words 10000          # larger doc
"""

import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import ollama
from rich.console import Console
from rich.table import Table
from rich import box

WORDS_PER_TOKEN = 0.75

MODEL_INFO: dict[str, tuple[str, str]] = {
    "qwen2.5:14b-instruct-q4_K_M": ("14B", "8 GB"),
    "gemma2:9b":                    ("9B",  "5 GB"),
    "llama3.1:8b-instruct-q8_0":   ("8B",  "7 GB"),
    "mistral:7b-instruct-q8_0":    ("7B",  "7 GB"),
    "llama3.2:1b":                  ("1B",  "1 GB"),
    "phi3:mini":                    ("3.8B","2 GB"),
}

_SENTENCES = [
    "The annual report showed a moderate increase in operational efficiency across all departments.",
    "Researchers discovered that migratory birds use magnetic fields to navigate during long journeys.",
    "The city council voted to approve the new zoning regulations for the downtown area.",
    "Cloud computing has dramatically changed how companies store and process large datasets.",
    "The archaeological dig revealed pottery fragments dating back over three thousand years.",
    "Scientists are investigating the role of gut microbiome diversity in immune system function.",
    "Renewable energy investments reached a record high for the third consecutive year.",
    "The novel explores themes of identity and belonging through the eyes of three generations.",
    "Traffic congestion in major metropolitan areas continues to worsen despite infrastructure spending.",
    "A new study links regular physical activity to improved cognitive performance in older adults.",
]

NEEDLE = "The secret passphrase is ZEPHYR-4291."
QUESTION = "What is the secret passphrase mentioned in the document?"


def build_doc(target_words: int) -> str:
    sentences = _SENTENCES * ((target_words // (len(_SENTENCES) * 8)) + 5)
    words: list[str] = []
    i = 0
    while len(words) < target_words:
        words += sentences[i % len(_SENTENCES)].split()
        i += 1
    filler = " ".join(words[:target_words])
    # Needle at the START — Ollama truncates from the beginning of the prompt,
    # so a needle here is the first thing dropped when context overflows.
    return NEEDLE + " " + filler


def run_check(model: str, doc: str) -> dict:
    estimated_tokens = int(len(doc.split()) / WORDS_PER_TOKEN) + 64
    prompt = f"{doc}\n\n---\n\nAnswer using only information from the text above.\nQuestion: {QUESTION}"

    try:
        result = ollama.generate(
            model=model,
            prompt=prompt,
            options={"num_predict": 80, "temperature": 0},
            # intentionally NO num_ctx
        )
        evaluated = getattr(result, "prompt_eval_count", None)
        found = "ZEPHYR-4291" in result.response
        snippet = result.response.strip().replace("\n", " ")[:160]
        return {
            "estimated_tokens": estimated_tokens,
            "evaluated_tokens": evaluated,
            "found": found,
            "snippet": snippet,
            "error": None,
        }
    except Exception as exc:
        return {
            "estimated_tokens": estimated_tokens,
            "evaluated_tokens": None,
            "found": False,
            "snippet": "",
            "error": str(exc),
        }


def parse_args():
    parser = argparse.ArgumentParser(description="Ollama silent-truncation detector")
    parser.add_argument("--models", nargs="+", default=list(MODEL_INFO.keys()), metavar="MODEL")
    parser.add_argument(
        "--words", type=int, default=6_000, metavar="N",
        help="Approximate word count of the test document (default: 6 000, ~8 000 tokens)",
    )
    return parser.parse_args()


def collect_results(models: list[str], doc: str) -> list[dict]:
    rows = []
    console = Console(highlight=False)
    for model in models:
        console.print(f"[dim]Querying {model}...[/dim]")
        r = run_check(model, doc)
        r["model"] = model
        if r["evaluated_tokens"] is not None and not r["error"]:
            r["ratio"] = r["evaluated_tokens"] / r["estimated_tokens"]
        else:
            r["ratio"] = None
        rows.append(r)
    return rows


def print_rich(actual_words: int, estimated_tokens: int, rows: list[dict]) -> None:
    console = Console(highlight=False)
    console.print(f"\n[bold]Truncation test[/bold] — no num_ctx set, needle at START of document")
    console.print(f"[dim]Doc: ~{actual_words:,} words | ~{estimated_tokens:,} estimated tokens[/dim]")
    console.print(f"[dim]Ollama default context is typically 2 048–4 096 tokens.[/dim]\n")

    ref = Table(title="Models Under Test", box=box.SIMPLE_HEAD, show_lines=False)
    ref.add_column("Model", style="cyan")
    ref.add_column("Params", justify="right")
    ref.add_column("Disk", justify="right")
    for r in rows:
        params, size = MODEL_INFO.get(r["model"], ("?", "?"))
        ref.add_row(r["model"], params, size)
    console.print(ref)
    console.print()

    table = Table(box=box.SIMPLE_HEAD, show_lines=False)
    table.add_column("Model", style="cyan")
    table.add_column("Est. tokens", justify="right", style="dim")
    table.add_column("Evaluated", justify="right")
    table.add_column("Coverage", justify="right")
    table.add_column("Truncated?", justify="center")
    table.add_column("Needle found?", justify="center")
    table.add_column("Response snippet", max_width=50)

    for r in rows:
        if r["error"]:
            table.add_row(r["model"], str(r["estimated_tokens"]), "—", "—",
                          "[yellow]ERR[/yellow]", "[yellow]ERR[/yellow]", r["error"][:60])
            continue
        ev = r["evaluated_tokens"]
        ratio = r["ratio"]
        if ev is not None:
            coverage = f"{ratio:.0%}"
            truncated = "[bold red]YES[/bold red]" if ratio < 0.85 else "[bold green]NO[/bold green]"
            ev_str = f"[red]{ev:,}[/red]" if ratio < 0.85 else f"[green]{ev:,}[/green]"
        else:
            coverage, truncated, ev_str = "?", "[yellow]N/A[/yellow]", "[yellow]N/A[/yellow]"
        found_display = "[bold green]YES[/bold green]" if r["found"] else "[bold red]NO[/bold red]"
        table.add_row(r["model"], f"{r['estimated_tokens']:,}", ev_str, coverage,
                      truncated, found_display, r["snippet"])

    console.print(table)
    console.print(
        "\n[dim]Coverage = evaluated / estimated. "
        "Below ~85% → Ollama likely truncated the prompt. "
        "N/A = prompt_eval_count not returned (older Ollama).[/dim]\n"
    )


def to_md(actual_words: int, estimated_tokens: int, rows: list[dict]) -> str:
    lines = [
        "## Truncation Test\n",
        f"**Doc:** ~{actual_words:,} words | ~{estimated_tokens:,} estimated tokens  ",
        "**Setup:** No `num_ctx` set — needle at START of document  ",
        "**Ollama default context:** typically 2 048–4 096 tokens\n",
        "### Models Under Test\n",
        "| Model | Params | Disk |",
        "|-------|-------:|-----:|",
    ]
    for r in rows:
        params, size = MODEL_INFO.get(r["model"], ("?", "?"))
        lines.append(f"| `{r['model']}` | {params} | {size} |")
    lines += [
        "\n### Results\n",
        "| Model | Params | Est. tokens | Evaluated | Coverage | Truncated? | Needle found? | Response snippet |",
        "|-------|-------:|------------:|----------:|---------:|:----------:|:-------------:|-----------------|",
    ]
    for r in rows:
        if r["error"]:
            params, _ = MODEL_INFO.get(r["model"], ("?", "?"))
            lines.append(f"| `{r['model']}` | {params} | {r['estimated_tokens']:,} | — | — | ERR | ERR | {r['error'][:80]} |")
            continue
        ev = r["evaluated_tokens"]
        ratio = r["ratio"]
        coverage = f"{ratio:.0%}" if ratio is not None else "?"
        truncated = ("YES" if ratio is not None and ratio < 0.85 else
                     ("NO" if ratio is not None else "N/A"))
        found = "YES" if r["found"] else "NO"
        ev_str = f"{ev:,}" if ev is not None else "N/A"
        snippet = r["snippet"].replace("|", "\\|")[:120]
        params, _ = MODEL_INFO.get(r["model"], ("?", "?"))
        lines.append(f"| `{r['model']}` | {params} | {r['estimated_tokens']:,} | {ev_str} | {coverage} | {truncated} | {found} | {snippet} |")
    lines.append("\n> Coverage = evaluated / estimated. Below ~85% → truncated. N/A = prompt_eval_count not returned.")
    return "\n".join(lines) + "\n"


def main():
    args = parse_args()

    doc = build_doc(args.words)
    actual_words = len(doc.split())
    estimated_tokens = int(actual_words / WORDS_PER_TOKEN) + 64

    rows = collect_results(args.models, doc)
    print_rich(actual_words, estimated_tokens, rows)

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"truncation_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    path.write_text(to_md(actual_words, estimated_tokens, rows), encoding="utf-8")
    Console(highlight=False).print(f"[dim]Saved → {path}[/dim]")


if __name__ == "__main__":
    main()
