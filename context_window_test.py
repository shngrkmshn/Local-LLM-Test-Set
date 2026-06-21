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
"""

import sys
import os
import argparse
import textwrap

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

DEFAULT_MODELS = [
    "qwen2.5:14b-instruct-q4_K_M",
    "gemma2:9b",
    "llama3.1:8b-instruct-q8_0",
    "mistral:7b-instruct-q8_0",
    "llama3.2:1b",
    "phi3:mini",
]

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

def ask_model(model: str, document: str) -> tuple[bool, str]:
    """
    Send document + question to the model. Returns (found_needle, response_snippet).
    Sets num_ctx dynamically based on estimated token count.
    """
    word_count = len(document.split())
    estimated_tokens = int(word_count / WORDS_PER_TOKEN) + 512   # buffer for prompt + response

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
                "num_predict": 80,
                "num_ctx": estimated_tokens,
                "temperature": 0,
            },
        )
        response = result.response.strip()
        found = "ZEPHYR-4291" in response
        snippet = response[:120].replace("\n", " ")
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
    return parser.parse_args()


def main():
    args = parse_args()
    console = Console(highlight=False)

    console.print(f"\n[bold]Needle:[/bold] [yellow]{NEEDLE}[/yellow]")
    console.print(f"[bold]Question:[/bold] {NEEDLE_QUESTION}\n")
    console.print(f"[dim]Models:    {', '.join(args.models)}[/dim]")
    console.print(f"[dim]Lengths:   {args.lengths} words[/dim]")
    console.print(f"[dim]Positions: {args.positions}[/dim]\n")

    # Pre-build all documents so we don't rebuild per model
    docs: dict[tuple[int, str], str] = {}
    for length in args.lengths:
        for pos in args.positions:
            docs[(length, pos)] = build_document(length, pos)

    for model in args.models:
        console.rule(f"[bold cyan]{model}[/bold cyan]")

        table = Table(box=box.SIMPLE_HEAD, show_lines=False)
        table.add_column("Words", justify="right", style="dim")
        table.add_column("Position", style="dim")
        table.add_column("Found?", justify="center")
        table.add_column("Model response (truncated)")

        for length in args.lengths:
            for pos in args.positions:
                doc = docs[(length, pos)]
                actual_words = len(doc.split())

                console.print(
                    f"  [dim]Testing {actual_words:,} words, needle at {pos}...[/dim]",
                    end="\r",
                )

                found, snippet = ask_model(model, doc)

                found_display = "[bold green]YES[/bold green]" if found else "[bold red]NO[/bold red]"
                if "ERROR" in snippet:
                    found_display = "[yellow]ERR[/yellow]"

                table.add_row(f"{actual_words:,}", pos, found_display, snippet)

        console.print(" " * 60, end="\r")   # clear progress line
        console.print(table)
        console.print()

    console.print("[bold]Done.[/bold]  YES = model recalled ZEPHYR-4291 | NO = lost it | ERR = context overflow\n")


if __name__ == "__main__":
    main()
