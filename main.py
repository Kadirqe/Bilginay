import sys, io, time
# Windows terminali UTF-8 emoji karakterlerini desteklemiyorsa düzeltelim
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Prompt
from rich.markdown import Markdown

from core.engine import AIEngine, ChatStrategy, TrainStrategy
from core.turkish_nlp import TurkishNLP
from core.reasoning_engine import KNOWLEDGE_BASE

console = Console()

COMMANDS_HELP = """
[bold cyan]Kullanılabilir Komutlar:[/bold cyan]
  [green]konular[/green]         — Bilginay'ın bildiği tüm konuları listeler
  [green]modeli eğit[/green]     — NanoLLM modellerini PyTorch ile eğitir
  [green]çıkış / exit[/green]    — Programı kapatır
"""

def show_banner():
    console.print(Panel.fit(
        "[bold cyan]Bilginay[/bold cyan] [white]— Çok Uzman Akıl Yürütme Sistemi[/white]\n"
        "[dim]Türkçe & İngilizce · Chain-of-Thought · MoE Mimarisi[/dim]",
        border_style="bright_blue"
    ))
    console.print(COMMANDS_HELP)

def list_topics():
    console.print("\n[bold yellow]📚 Bilgi Tabanındaki Konular:[/bold yellow]")
    for i, (key, val) in enumerate(KNOWLEDGE_BASE.items(), 1):
        kws = ", ".join(val.get("keywords", [])[:4])
        console.print(f"  [cyan]{i:>2}.[/cyan] [bold]{key}[/bold]  [dim]({kws}...)[/dim]")
    console.print()

def run_training():
    from core.trainer import NanoTrainer
    engine = AIEngine(TrainStrategy())
    console.print(engine.process("data/dialogues.txt"))
    trainer = NanoTrainer("data/dialogues.txt")
    trainer.train_expert("primary", iterations=3000)
    trainer.train_expert("middle",  iterations=3000)
    trainer.train_expert("high",    iterations=3000)
    console.print("[bold green]Tüm uzmanların eğitimi tamamlandı![/bold green]\n")

def main():
    show_banner()
    nlp    = TurkishNLP()
    engine = AIEngine(ChatStrategy())

    while True:
        try:
            command = Prompt.ask("[bold magenta]Bilginay[/bold magenta]").strip()

            if not command:
                continue

            low = command.lower()

            if low in ("çıkış", "exit", "quit", "q"):
                console.print("[red]Görüşmek üzere![/red]")
                break

            if low == "konular":
                list_topics()
                continue

            if any(w in low for w in ("eğit", "train", "öğren")):
                run_training()
                continue

            # ── Sohbet akışı ──────────────────────────────────────────
            response = engine.process(command)

            # Rich Markdown render → kalın/emoji düzgün görünür
            console.print(Panel(
                Markdown(response),
                border_style="bright_blue",
                padding=(1, 2)
            ))

        except KeyboardInterrupt:
            console.print("\n[red]Çıkış yapılıyor...[/red]")
            break

if __name__ == "__main__":
    main()

