"""
prompt_sensitivity.py — test how prompt wording affects model responses.

Sends every prompt to every Ollama model and compares outputs side by side.
Useful for observing rephrasing effects, instruction sensitivity, tone, and
how strongly a model follows format instructions.

Usage:
    python prompt_sensitivity.py                        # built-in prompt set
    python prompt_sensitivity.py --file prompts.txt     # load prompts from file
    python prompt_sensitivity.py --md                   # Markdown output
    python prompt_sensitivity.py --models llama3.2:1b phi3:mini
    python prompt_sensitivity.py --full                 # show full responses (no truncation)

Prompt file format (prompts.txt):
    One prompt per line. Blank lines and lines starting with # are ignored.
"""

import sys
import os
import argparse
import io
import contextlib
from concurrent.futures import ThreadPoolExecutor, as_completed
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

# Built-in prompt set — same underlying question, five different phrasings.
# Edit freely or replace with --file.
DEFAULT_PROMPTS = [
    "What causes climate change?",
    "Could you please explain what causes climate change?",
    "As a climate scientist, briefly explain what causes climate change.",
    "In exactly one sentence, what causes climate change?",
    "Some people say climate change isn't real. What does the science actually say causes it?",
]

RESPONSE_PREVIEW = 220   # chars shown per response in non-full mode

# ---------------------------------------------------------------------------
# Ollama query
# ---------------------------------------------------------------------------

def ask(model: str, prompt: str, num_predict: int = 300, num_ctx: int | None = None) -> str:
    try:
        options: dict = {"num_predict": num_predict, "temperature": 0.7}
        if num_ctx is not None:
            options["num_ctx"] = num_ctx
        result = ollama.generate(model=model, prompt=prompt, options=options)
        return result.response.strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def query_all_models(prompt: str, models: list[str],
                     num_predict: int = 300, num_ctx: int | None = None) -> dict[str, str]:
    """Ask all models the same prompt in parallel."""
    results: dict[str, str] = {}

    def task(model):
        return model, ask(model, prompt, num_predict=num_predict, num_ctx=num_ctx)

    with ThreadPoolExecutor(max_workers=len(models)) as pool:
        for model, response in pool.map(task, models):
            results[model] = response

    return {m: results[m] for m in models}   # preserve order


# ---------------------------------------------------------------------------
# Output: Rich
# ---------------------------------------------------------------------------

def print_rich(prompts: list[str], models: list[str],
               data: list[dict[str, str]], full: bool) -> None:
    console = Console(highlight=False)

    # Models reference header
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
        table.add_column("Response", max_width=80)

        for model in models:
            response = responses[model]
            display = response if full else response[:RESPONSE_PREVIEW]
            if not full and len(response) > RESPONSE_PREVIEW:
                display += "..."
            display = display.replace("\n", " ")
            table.add_row(model, display)

        console.print(table)
        console.print()

    if not full:
        console.print(f"[dim]Responses truncated to {RESPONSE_PREVIEW} chars. Use --full to see complete output.[/dim]\n")


# ---------------------------------------------------------------------------
# Output: Markdown
# ---------------------------------------------------------------------------

def print_md(prompts: list[str], models: list[str],
             data: list[dict[str, str]], full: bool) -> None:
    print("## Prompt Sensitivity Test\n")

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
    parser = argparse.ArgumentParser(description="Prompt sensitivity tester")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS, metavar="MODEL")
    parser.add_argument("--file", type=Path, metavar="FILE",
                        help="Text file with one prompt per line")
    parser.add_argument("--md", action="store_true", help="Markdown output")
    parser.add_argument("--full", action="store_true", help="Show full responses — sets num_predict=-1 so the model generates until it naturally stops")
    parser.add_argument("--max-tokens", type=int, default=None, metavar="N",
                        help="Max tokens to generate per response (default: 300, or 1024 with --full)")
    parser.add_argument("--num-ctx", type=int, default=None, metavar="TOKENS",
                        help="Context window size passed to Ollama (default: model default, ~4096)")
    return parser.parse_args()


def main():
    args = parse_args()

    prompts = load_prompts_from_file(args.file) if args.file else DEFAULT_PROMPTS

    if not prompts:
        print("No prompts found.", file=sys.stderr)
        sys.exit(1)

    # -1 = unlimited (model stops naturally); used for --full so nothing gets cut off
    num_predict = args.max_tokens if args.max_tokens is not None else (-1 if args.full else 300)

    if not args.md:
        console = Console(highlight=False)
        console.print(f"[dim]Running {len(prompts)} prompt(s) x {len(args.models)} model(s) "
                      f"(max_tokens={num_predict})...[/dim]\n")

    data: list[dict[str, str]] = []
    for i, prompt in enumerate(prompts, 1):
        if not args.md:
            Console(highlight=False).print(
                f"  [dim]Prompt {i}/{len(prompts)}: {prompt[:60]}{'...' if len(prompt) > 60 else ''}[/dim]",
                end="\r",
            )
        responses = query_all_models(prompt, args.models, num_predict=num_predict, num_ctx=args.num_ctx)
        data.append(responses)

    if not args.md:
        Console(highlight=False).print(" " * 80, end="\r")

    if args.md:
        print_md(prompts, args.models, data, args.full)
    else:
        print_rich(prompts, args.models, data, args.full)

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"prompt_sensitivity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print_md(prompts, args.models, data, args.full)
    path.write_text(buf.getvalue(), encoding="utf-8")
    Console(highlight=False).print(f"[dim]Saved → {path}[/dim]")


if __name__ == "__main__":
    main()
