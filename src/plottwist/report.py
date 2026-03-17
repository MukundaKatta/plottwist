"""Rich terminal reporting for story state and play sessions."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich import box

from plottwist.models import StoryState, StoryTemplate
from plottwist.story.characters import Character
from plottwist.story.engine import StoryEngine


console = Console()


def print_banner() -> None:
    """Print the PLOTTWIST title banner."""
    banner = Text()
    banner.append("  PLOT", style="bold magenta")
    banner.append("TWIST", style="bold cyan")
    banner.append("  ", style="")
    console.print(Panel(banner, subtitle="Interactive AI Fiction", border_style="magenta", width=42))


def print_template_list(templates: dict[str, StoryTemplate]) -> None:
    """Display available story templates in a table."""
    table = Table(title="Story Templates", box=box.ROUNDED, border_style="cyan")
    table.add_column("Name", style="bold magenta")
    table.add_column("Genre", style="green")
    table.add_column("Tone", style="yellow")
    table.add_column("Description")

    for name, tmpl in templates.items():
        table.add_row(name, tmpl.genre.value, tmpl.tone.value, tmpl.tagline)

    console.print(table)


def print_scene(engine: StoryEngine, narration: str = "") -> None:
    """Display the current scene."""
    scene = engine.current_scene()
    if scene is None:
        console.print("[dim]No active scene.[/dim]")
        return

    title = f"[bold]{scene.title}[/bold]"
    subtitle = f"{scene.scene_type.value} | mood: {scene.mood.value}"
    body = ""
    if scene.data.description:
        body += scene.data.description + "\n"
    if narration:
        body += "\n" + narration

    console.print(Panel(body.strip(), title=title, subtitle=subtitle, border_style="blue", padding=(1, 2)))

    # Characters present
    chars = engine.characters_in_scene()
    if chars:
        names = ", ".join(f"[bold]{c.name}[/bold]" for c in chars)
        console.print(f"  [dim]Present:[/dim] {names}\n")


def print_choices(options: list, prompt: str = "What do you do?") -> None:
    """Display choice options for the player."""
    console.print(f"\n[bold yellow]{prompt}[/bold yellow]\n")
    for i, opt in enumerate(options, 1):
        console.print(f"  [bold cyan]{i}.[/bold cyan] {opt.text}")
    console.print()


def print_dialogue(speaker: str, text: str) -> None:
    """Display a line of dialogue."""
    console.print(f'  [bold green]{speaker}:[/bold green] "{text}"')


def print_conversation(exchanges: list[dict[str, str]]) -> None:
    """Display a multi-turn conversation."""
    for ex in exchanges:
        print_dialogue(ex["speaker"], ex["text"])


def print_consequence(description: str, severity: str = "minor") -> None:
    """Display a consequence notification."""
    colour_map = {
        "minor": "dim",
        "moderate": "yellow",
        "major": "bold red",
        "critical": "bold white on red",
    }
    style = colour_map.get(severity, "dim")
    console.print(f"  [{style}]>> {description}[/{style}]")


def print_narration(text: str) -> None:
    """Print narrative prose."""
    console.print(Panel(text, border_style="dim blue", padding=(1, 2)))


def print_story_report(engine: StoryEngine) -> None:
    """Print a comprehensive report of the story state."""
    state = engine.state
    print_banner()

    # Overview
    overview = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    overview.add_column("Key", style="bold")
    overview.add_column("Value")
    overview.add_row("Template", state.template_name or "custom")
    overview.add_row("Genre", state.genre.value)
    overview.add_row("Tone", state.tone.value)
    overview.add_row("Player", state.player_name)
    overview.add_row("Turns", str(state.turn_count))
    overview.add_row("Scenes visited", str(len(state.scenes)))
    overview.add_row("Choices made", str(len([e for e in state.history if e.event_type == "choice"])))
    console.print(Panel(overview, title="[bold]Story Overview[/bold]", border_style="magenta"))

    # Characters
    if state.characters:
        char_table = Table(title="Characters", box=box.ROUNDED, border_style="green")
        char_table.add_column("Name", style="bold")
        char_table.add_column("Role")
        char_table.add_column("Arc Phase", style="yellow")
        char_table.add_column("Alive", justify="center")
        char_table.add_column("Top Traits")

        for cdata in state.characters.values():
            char = Character(cdata)
            alive_mark = "[green]Yes[/green]" if cdata.alive else "[red]No[/red]"
            traits = ", ".join(char.dominant_traits(2))
            char_table.add_row(cdata.name, cdata.role, cdata.arc_phase.value, alive_mark, traits)

        console.print(char_table)

    # Flags
    if state.flags:
        flag_table = Table(title="Story Flags", box=box.SIMPLE, border_style="cyan")
        flag_table.add_column("Flag", style="bold")
        flag_table.add_column("Value")
        for k, v in state.flags.items():
            flag_table.add_row(k, str(v))
        console.print(flag_table)

    # Recent history
    recent = engine.recent_history(15)
    if recent:
        hist_table = Table(title="Recent Events", box=box.SIMPLE, border_style="dim")
        hist_table.add_column("Type", style="bold")
        hist_table.add_column("Actor")
        hist_table.add_column("Content", max_width=60)
        for ev in recent:
            hist_table.add_row(ev.event_type, ev.actor or "-", ev.content[:120])
        console.print(hist_table)
