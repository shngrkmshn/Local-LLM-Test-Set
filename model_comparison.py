"""
model_comparison.py — compare how different models answer the same prompts.

Sends every prompt to every selected model and displays responses side by side.
Useful for seeing how model size and architecture affect answer quality, depth,
and style.

Usage:
    python model_comparison.py                              # uses prompts.txt by default
    python model_comparison.py --file other.txt
    python model_comparison.py --models llama3.2:1b phi3:mini qwen2.5:14b-instruct-q4_K_M
    python model_comparison.py --md
    python model_comparison.py --full

Prompt file format (prompts.txt):
    One prompt per line. Blank lines and lines starting with # are ignored.
"""

import sys
import os
import argparse
import io
import contextlib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import ollama
from rich.console import Console
from rich.table import Table
from rich.padding import Padding
from rich import box

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_INFO: dict[str, tuple[str, str]] = {
    "qwen2.5:14b-instruct-q4_K_M": ("14B", "8 GB"),
    "gemma2:9b":                    ("9B",  "5 GB"),
    "llama3.1:8b-instruct-q8_0":   ("8B",  "7 GB"),
    "mistral:7b-instruct-q8_0":    ("7B",  "7 GB"),
    "llama3.2:1b":                  ("1B",  "1 GB"),
    "phi3:mini":                    ("3.8B","2 GB"),
}

DEFAULT_MODELS = list(MODEL_INFO.keys())
DEFAULT_PROMPT_FILE = Path("prompts.txt")
RESPONSE_PREVIEW = 300

# ---------------------------------------------------------------------------
# Ollama query
# ---------------------------------------------------------------------------

def ask(model: str, prompt: str, num_predict: int = 300, temperature: float = 0.7,
        num_ctx: int | None = None) -> str:
    try:
        options: dict = {"num_predict": num_predict, "temperature": temperature}
        if num_ctx is not None:
            options["num_ctx"] = num_ctx
        result = ollama.generate(
            model=model,
            prompt=prompt,
            options=options,
        )
        return result.response.strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def query_all_models(prompt: str, models: list[str], num_predict: int, temperature: float,
                     num_ctx: int | None = None) -> dict[str, str]:
    results: dict[str, str] = {}

    def task(model):
        return model, ask(model, prompt, num_predict, temperature, num_ctx)

    with ThreadPoolExecutor(max_workers=len(models)) as pool:
        for model, response in pool.map(task, models):
            results[model] = response

    return {m: results[m] for m in models}


# ---------------------------------------------------------------------------
# Output: Rich
# ---------------------------------------------------------------------------

def print_rich(
    prompts: list[str],
    models: list[str],
    data: list[dict[str, str]],
    full: bool,
) -> None:
    console = Console(highlight=False)

    ref = Table(title="Models Under Test", box=box.SIMPLE_HEAD, show_lines=False)
    ref.add_column("Model", style="cyan")
    ref.add_column("Params", justify="right")
    ref.add_column("Disk", justify="right")
    for m in models:
        params, size = MODEL_INFO.get(m, ("?", "?"))
        ref.add_row(m, params, size)
    console.print(ref)
    console.print()

    for i, (prompt, responses) in enumerate(zip(prompts, data), 1):
        console.rule(f"[bold]Prompt {i}[/bold]")
        console.print(Padding(f"[yellow]{prompt}[/yellow]", (0, 2)))
        console.print()

        table = Table(box=box.SIMPLE_HEAD, show_lines=True)
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Response", max_width=90)

        for model in models:
            response = responses[model]
            display = response if full else response[:RESPONSE_PREVIEW]
            if not full and len(response) > RESPONSE_PREVIEW:
                display += "..."
            table.add_row(model, display.replace("\n", " "))

        console.print(table)
        console.print()

    if not full:
        console.print(
            f"[dim]Responses truncated to {RESPONSE_PREVIEW} chars. Use --full to see complete output.[/dim]\n"
        )


# ---------------------------------------------------------------------------
# Output: Markdown
# ---------------------------------------------------------------------------

def print_md(
    prompts: list[str],
    models: list[str],
    data: list[dict[str, str]],
    full: bool,
) -> None:
    print("## Model Comparison\n")

    print("### Models Under Test\n")
    print("| Model | Params | Disk |")
    print("|-------|-------:|-----:|")
    for m in models:
        params, size = MODEL_INFO.get(m, ("?", "?"))
        print(f"| `{m}` | {params} | {size} |")
    print()

    for i, (prompt, responses) in enumerate(zip(prompts, data), 1):
        print(f"### Prompt {i}\n")
        print(f"> {prompt}\n")
        print("| Model | Response |")
        print("|-------|----------|")
        for model in models:
            response = responses[model]
            display = response if full else response[:RESPONSE_PREVIEW]
            if not full and len(response) > RESPONSE_PREVIEW:
                display += "..."
            safe = display.replace("\n", " ").replace("|", "\\|")
            print(f"| `{model}` | {safe} |")
        print()

    if not full:
        print(f"> Responses truncated to {RESPONSE_PREVIEW} chars. Use `--full` to see complete output.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_prompts_from_file(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]


def parse_args():
    parser = argparse.ArgumentParser(description="Model comparison tester")
    parser.add_argument(
        "--file", type=Path, default=DEFAULT_PROMPT_FILE, metavar="FILE",
        help=f"Prompt file (default: {DEFAULT_PROMPT_FILE})",
    )
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS, metavar="MODEL")
    parser.add_argument(
        "--temperature", type=float, default=0.7, metavar="T",
        help="Temperature for all models (default: 0.7)",
    )
    parser.add_argument("--md", action="store_true", help="Markdown output")
    parser.add_argument(
        "--full", action="store_true",
        help="Show full responses — sets num_predict=-1",
    )
    parser.add_argument(
        "--max-tokens", type=int, default=None, metavar="N",
        help="Max tokens per response (default: 300, or -1 with --full)",
    )
    parser.add_argument(
        "--num-ctx", type=int, default=None, metavar="TOKENS",
        help="Context window size passed to Ollama (default: model default, ~4096)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not args.file.exists():
        print(f"Prompt file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    prompts = load_prompts_from_file(args.file)
    if not prompts:
        print("No prompts found in file.", file=sys.stderr)
        sys.exit(1)

    num_predict = args.max_tokens if args.max_tokens is not None else (-1 if args.full else 300)

    if not args.md:
        console = Console(highlight=False)
        console.print(
            f"[dim]Running {len(prompts)} prompt(s) × {len(args.models)} model(s) "
            f"(temp={args.temperature}, max_tokens={num_predict})...[/dim]\n"
        )

    data: list[dict[str, str]] = []
    for i, prompt in enumerate(prompts, 1):
        if not args.md:
            Console(highlight=False).print(
                f"  [dim]Prompt {i}/{len(prompts)}: {prompt[:60]}{'...' if len(prompt) > 60 else ''}[/dim]",
                end="\r",
            )
        responses = query_all_models(prompt, args.models, num_predict, args.temperature, args.num_ctx)
        data.append(responses)

    if not args.md:
        Console(highlight=False).print(" " * 80, end="\r")

    if args.md:
        print_md(prompts, args.models, data, args.full)
    else:
        print_rich(prompts, args.models, data, args.full)

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"model_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print_md(prompts, args.models, data, args.full)
    path.write_text(buf.getvalue(), encoding="utf-8")
    Console(highlight=False).print(f"[dim]Saved → {path}[/dim]")


if __name__ == "__main__":
    main()
