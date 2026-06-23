"""
context_window_test.py — reproduce the "lost in the middle" effect.

Hides a unique needle fact at the START, MIDDLE, or END of documents of
increasing length, then asks each Ollama model to recall it. Reveals where
models start losing track of information buried in long contexts.

Usage:
    python context_window_test.py                               # all models, all lengths
    python context_window_test.py --models llama3.2:1b phi3:mini
    python context_window_test.py --lengths 500 5000            # skip 15k
    python context_window_test.py --positions middle            # only test middle
    python context_window_test.py --md                          # Markdown output
"""

import sys
import os
import argparse
import textwrap
import io
import contextlib
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
from rich import box

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

NEEDLE = "The secret passphrase is ZEPHYR-4291."
NEEDLE_QUESTION = "What is the secret passphrase mentioned in the document?"

# Model name → (parameter count, disk size on this machine)
MODEL_INFO: dict[str, tuple[str, str]] = {
    "qwen2.5:14b-instruct-q4_K_M": ("14B", "8 GB"),
    "gemma2:9b":                    ("9B",  "5 GB"),
    "llama3.1:8b-instruct-q8_0":   ("8B",  "7 GB"),
    "mistral:7b-instruct-q8_0":    ("7B",  "7 GB"),
    "llama3.2:1b":                  ("1B",  "1 GB"),
    "phi3:mini":                    ("3.8B","2 GB"),
}

DEFAULT_MODELS = list(MODEL_INFO.keys())

DEFAULT_LENGTHS = [500, 5000, 15_000]   # approximate word counts
DEFAULT_POSITIONS = ["start", "middle", "end"]

# Rough words-per-token ratio for context size estimation
WORDS_PER_TOKEN = 0.75

# ---------------------------------------------------------------------------
# Filler text generation
# ---------------------------------------------------------------------------

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
    "The museum acquired a rare collection of medieval manuscripts from a private estate.",
    "Farmers in the region are adopting precision agriculture techniques to reduce water usage.",
    "The diplomatic summit concluded with a joint statement on trade and environmental cooperation.",
    "Astronomers detected unusual radio signals originating from a galaxy over a billion light-years away.",
    "The restaurant earned its third Michelin star thanks to its innovative approach to local ingredients.",
    "Engineers developed a new alloy that maintains structural integrity at extreme temperatures.",
    "Local schools are integrating coding curricula to prepare students for technology careers.",
    "The theater production received standing ovations for its experimental staging and original score.",
    "A series of undersea earthquakes triggered tsunami warnings along the Pacific coast.",
    "The startup raised venture capital funding to expand its platform into emerging markets.",
    "Forest fire prevention efforts have reduced the annual burn area by thirty percent.",
    "Economists debate whether inflation is primarily driven by supply chain disruptions or monetary policy.",
    "The documentary crew spent eight months filming deep-sea creatures rarely seen by humans.",
    "Urban planners are redesigning public spaces to accommodate cyclists and pedestrians.",
    "The athlete broke the national record by a margin that surprised even her coach.",
    "Historians argue that the significance of the treaty was largely overlooked at the time.",
    "New regulations require food manufacturers to clearly label products containing allergens.",
    "The satellite imagery revealed significant changes in the glacier's extent over two decades.",
    "Volunteers planted over ten thousand native tree seedlings along the riverbank restoration zone.",
    "The software update introduced several accessibility features requested by users with disabilities.",
    "Marine biologists tagged dolphins to track their migratory patterns across ocean basins.",
    "The bridge renovation project is expected to take three years and employ hundreds of workers.",
    "A heatwave caused power demand to spike, straining the regional electrical grid.",
    "The poem collection draws on the author's experiences living in four different countries.",
    "Laboratory tests confirmed the compound shows promise as a treatment for antibiotic-resistant infections.",
    "Public transport ridership declined during the economic slowdown but has since recovered.",
    "The festival attracted visitors from across the country to celebrate traditional crafts and music.",
    "Genetic sequencing has transformed forensic investigations over the past two decades.",
    "The company reduced its carbon footprint by switching to electric delivery vehicles.",
    "Linguists have documented over two hundred endangered languages in the region.",
]


def _build_filler(target_words: int) -> str:
    """Repeat and cycle sentences until we have enough words."""
    sentences = _SENTENCES * ((target_words // (len(_SENTENCES) * 10)) + 5)
    words: list[str] = []
    i = 0
    while len(words) < target_words:
        words += sentences[i % len(sentences)].split()
        i += 1
    return " ".join(words[:target_words])


def build_document(target_words: int, position: str) -> str:
    """Return a document of ~target_words with the needle at the given position."""
    filler = _build_filler(target_words)
    filler_words = filler.split()

    if position == "start":
        words = [NEEDLE] + filler_words
    elif position == "end":
        words = filler_words + [NEEDLE]
    else:  # middle
        mid = len(filler_words) // 2
        words = filler_words[:mid] + [NEEDLE] + filler_words[mid:]

    return " ".join(words)


# ---------------------------------------------------------------------------
# Ollama query
# ---------------------------------------------------------------------------

def ask_model(model: str, document: str, num_ctx: int | None = None) -> tuple[bool, str]:
    """
    Send document + question to the model. Returns (found_needle, response_snippet).
    If num_ctx is None, estimates from document length (original behaviour).
    """
    word_count = len(document.split())
    estimated_tokens = int(word_count / WORDS_PER_TOKEN) + 512   # buffer for prompt + response
    ctx = num_ctx if num_ctx is not None else estimated_tokens

    prompt = (
        f"{document}\n\n"
        f"---\n\n"
        f"Answer using only information from the text above.\n"
        f"Question: {NEEDLE_QUESTION}"
    )

    try:
        result = ollama.generate(
            model=model,
            prompt=prompt,
            options={
                "num_predict": 150,
                "num_ctx": ctx,
                "temperature": 0,
            },
        )
        response = result.response.strip()
        found = "ZEPHYR-4291" in response
        snippet = response.replace("\n", " ")
        return found, snippet
    except Exception as exc:
        return False, f"ERROR: {exc}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="Lost-in-the-middle context window test")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS, metavar="MODEL")
    parser.add_argument("--lengths", nargs="+", type=int, default=DEFAULT_LENGTHS, metavar="WORDS")
    parser.add_argument("--positions", nargs="+", default=DEFAULT_POSITIONS,
                        choices=["start", "middle", "end"], metavar="POS")
    parser.add_argument("--md", action="store_true", help="Output Markdown instead of Rich tables")
    parser.add_argument(
        "--num-ctx", type=int, default=None, metavar="TOKENS",
        help="Fix num_ctx to this value for every query instead of estimating from document length. "
             "Example: --num-ctx 32768. Useful for testing a specific context window size. "
             "With a 16 GB VRAM GPU, 32768 is a safe start; 65536 is feasible for smaller models.",
    )
    return parser.parse_args()


def collect_results(args) -> dict[str, list[tuple[int, str, bool, str]]]:
    """Run all queries and return {model: [(actual_words, position, found, snippet)]}."""
    docs: dict[tuple[int, str], str] = {}
    for length in args.lengths:
        for pos in args.positions:
            docs[(length, pos)] = build_document(length, pos)

    all_results: dict[str, list[tuple[int, str, bool, str]]] = {}
    for model in args.models:
        rows = []
        for length in args.lengths:
            for pos in args.positions:
                doc = docs[(length, pos)]
                actual_words = len(doc.split())
                found, snippet = ask_model(model, doc, num_ctx=args.num_ctx)
                rows.append((actual_words, pos, found, snippet))
        all_results[model] = rows
    return all_results


def print_rich(args, all_results: dict) -> None:
    console = Console(highlight=False)

    console.print(f"\n[bold]Needle:[/bold] [yellow]{NEEDLE}[/yellow]")
    console.print(f"[bold]Question:[/bold] {NEEDLE_QUESTION}\n")

    ref = Table(title="Models Under Test", box=box.SIMPLE_HEAD, show_lines=False)
    ref.add_column("Model", style="cyan")
    ref.add_column("Params", justify="right")
    ref.add_column("Disk", justify="right")
    for m in args.models:
        params, size = MODEL_INFO.get(m, ("?", "?"))
        ref.add_row(m, params, size)
    console.print(ref)
    console.print(f"[dim]Lengths:   {args.lengths} words[/dim]")
    console.print(f"[dim]Positions: {args.positions}[/dim]\n")

    for model, rows in all_results.items():
        console.rule(f"[bold cyan]{model}[/bold cyan]")
        table = Table(box=box.SIMPLE_HEAD, show_lines=False)
        table.add_column("Words", justify="right", style="dim")
        table.add_column("Position", style="dim")
        table.add_column("Found?", justify="center")
        table.add_column("Model response", max_width=72)
        for actual_words, pos, found, snippet in rows:
            found_display = "[bold green]YES[/bold green]" if found else "[bold red]NO[/bold red]"
            if "ERROR" in snippet:
                found_display = "[yellow]ERR[/yellow]"
            table.add_row(f"{actual_words:,}", pos, found_display, snippet)
        console.print(table)
        console.print()

    console.print("[bold]Done.[/bold]  YES = model recalled ZEPHYR-4291 | NO = lost it | ERR = context overflow\n")


def print_md(args, all_results: dict) -> None:
    print("## Lost-in-the-Middle: Context Window Test\n")
    print(f"**Needle:** `{NEEDLE}`  ")
    print(f"**Question:** {NEEDLE_QUESTION}\n")

    print("### Models Under Test\n")
    print("| Model | Params | Disk |")
    print("|-------|-------:|-----:|")
    for m in args.models:
        params, size = MODEL_INFO.get(m, ("?", "?"))
        print(f"| `{m}` | {params} | {size} |")

    print()
    for model, rows in all_results.items():
        print(f"\n### {model}\n")
        print("| Words | Position | Found? | Model Response |")
        print("|------:|----------|:------:|----------------|")
        for actual_words, pos, found, snippet in rows:
            found_str = "YES" if found else ("ERR" if "ERROR" in snippet else "NO")
            safe = snippet.replace("|", "\\|")
            print(f"| {actual_words:,} | {pos} | {found_str} | {safe} |")

    print("\n> YES = recalled ZEPHYR-4291 | NO = lost it | ERR = context overflow")


def _save_md(prefix: str, content: str) -> None:
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    path.write_text(content, encoding="utf-8")
    Console(highlight=False).print(f"[dim]Saved → {path}[/dim]")


def main():
    args = parse_args()

    if not args.md:
        console = Console(highlight=False)
        console.print("[dim]Building documents and querying models...[/dim]")

    all_results = collect_results(args)

    if args.md:
        print_md(args, all_results)
    else:
        print_rich(args, all_results)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print_md(args, all_results)
    _save_md("context_window_test", buf.getvalue())


if __name__ == "__main__":
    main()
