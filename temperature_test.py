"""
temperature_test.py — test how temperature affects model responses.

Sends every prompt to every model at every temperature, repeated N times per
combination so you can see how consistent (or random) each temperature setting
actually is. Rows = models, columns = temperatures, runs stacked in each cell.

Usage:
    python temperature_test.py                              # uses prompts.txt by default
    python temperature_test.py --file other.txt
    python temperature_test.py --temps 0.0 0.5 1.0 1.5
    python temperature_test.py --runs 5
    python temperature_test.py --models llama3.2:1b phi3:mini
    python temperature_test.py --md
    python temperature_test.py --full

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
DEFAULT_TEMPS = [0.0, 0.5, 1.0, 1.5]
DEFAULT_PROMPT_FILE = Path("prompts.txt")

RESPONSE_PREVIEW = 160   # chars shown per cell in non-full mode

# ---------------------------------------------------------------------------
# Ollama query
# ---------------------------------------------------------------------------

def ask(model: str, prompt: str, temperature: float, num_predict: int = 300) -> str:
    try:
        result = ollama.generate(
            model=model,
            prompt=prompt,
            options={"num_predict": num_predict, "temperature": temperature},
        )
        return result.response.strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def query_all(
    prompt: str,
    models: list[str],
    temps: list[float],
    num_predict: int,
    runs: int,
) -> dict[tuple[str, float], list[str]]:
    """Query all (model, temperature, run) combinations in parallel."""
    jobs = [(m, t, r) for m in models for t in temps for r in range(runs)]
    raw: dict[tuple[str, float, int], str] = {}

    def task(job):
        m, t, r = job
        return job, ask(m, prompt, t, num_predict)

    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        for job, response in pool.map(task, jobs):
            raw[job] = response

    results: dict[tuple[str, float], list[str]] = {}
    for m in models:
        for t in temps:
            results[(m, t)] = [raw[(m, t, r)] for r in range(runs)]
    return results


# ---------------------------------------------------------------------------
# Output: Rich
# ---------------------------------------------------------------------------

def _clip(text: str, full: bool) -> str:
    if full or len(text) <= RESPONSE_PREVIEW:
        return text
    return text[:RESPONSE_PREVIEW] + "..."


def print_rich(
    prompts: list[str],
    models: list[str],
    temps: list[float],
    data: list[dict[tuple[str, float], list[str]]],
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
        for t in temps:
            table.add_column(f"temp={t}", max_width=40)

        for model in models:
            cells = []
            for t in temps:
                runs = responses[(model, t)]
                lines = [f"[{r+1}] {_clip(resp, full).replace(chr(10), ' ')}"
                         for r, resp in enumerate(runs)]
                cells.append("\n".join(lines))
            table.add_row(model, *cells)

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
    temps: list[float],
    data: list[dict[tuple[str, float], list[str]]],
    full: bool,
) -> None:
    print("# Temperature Test\n")

    print("## Models Under Test\n")
    print("| Model | Params | Disk |")
    print("|-------|-------:|-----:|")
    for m in models:
        params, size = MODEL_INFO.get(m, ("?", "?"))
        print(f"| `{m}` | {params} | {size} |")
    print()

    if not full:
        print(f"> Responses truncated to {RESPONSE_PREVIEW} chars. Use `--full` to see complete output.\n")

    for i, (prompt, responses) in enumerate(zip(prompts, data), 1):
        print(f"---\n")
        print(f"## Prompt {i}\n")
        print(f"> {prompt}\n")

        for model in models:
            params, size = MODEL_INFO.get(model, ("?", "?"))
            print(f"### {model} ({params})\n")

            for t in temps:
                print(f"#### temp={t}\n")
                runs = responses[(model, t)]
                for r, resp in enumerate(runs):
                    print(f"##### Run {r + 1}\n")
                    print(_clip(resp, full))
                    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_prompts_from_file(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]


def parse_args():
    parser = argparse.ArgumentParser(description="Temperature sensitivity tester")
    parser.add_argument(
        "--file", type=Path, default=DEFAULT_PROMPT_FILE, metavar="FILE",
        help=f"Prompt file (default: {DEFAULT_PROMPT_FILE})",
    )
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS, metavar="MODEL")
    parser.add_argument(
        "--temps", nargs="+", type=float, default=DEFAULT_TEMPS, metavar="T",
        help="Temperatures to test (default: 0.0 0.5 1.0 1.5)",
    )
    parser.add_argument(
        "--runs", type=int, default=3, metavar="N",
        help="Number of times to run each (model, temperature) combination (default: 3)",
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

    temps = sorted(set(args.temps))
    num_predict = args.max_tokens if args.max_tokens is not None else (-1 if args.full else 300)
    total = len(prompts) * len(args.models) * len(temps) * args.runs

    if not args.md:
        console = Console(highlight=False)
        console.print(
            f"[dim]Running {len(prompts)} prompt(s) × {len(args.models)} model(s) × "
            f"{len(temps)} temperature(s) × {args.runs} run(s) = {total} calls "
            f"(max_tokens={num_predict})...[/dim]\n"
        )

    data: list[dict[tuple[str, float], list[str]]] = []
    for i, prompt in enumerate(prompts, 1):
        if not args.md:
            Console(highlight=False).print(
                f"  [dim]Prompt {i}/{len(prompts)}: {prompt[:60]}{'...' if len(prompt) > 60 else ''}[/dim]",
                end="\r",
            )
        responses = query_all(prompt, args.models, temps, num_predict, args.runs)
        data.append(responses)

    if not args.md:
        Console(highlight=False).print(" " * 80, end="\r")

    if args.md:
        print_md(prompts, args.models, temps, data, args.full)
    else:
        print_rich(prompts, args.models, temps, data, args.full)

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"temperature_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print_md(prompts, args.models, temps, data, args.full)
    path.write_text(buf.getvalue(), encoding="utf-8")
    Console(highlight=False).print(f"[dim]Saved → {path}[/dim]")


if __name__ == "__main__":
    main()
