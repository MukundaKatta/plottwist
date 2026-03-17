"""PLOTTWIST CLI -- powered by Click and Rich."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from plottwist import __version__
from plottwist.report import (
    console,
    print_banner,
    print_choices,
    print_consequence,
    print_narration,
    print_scene,
    print_story_report,
    print_template_list,
)
from plottwist.templates import TEMPLATES


@click.group()
@click.version_option(version=__version__, prog_name="plottwist")
def cli() -> None:
    """PLOTTWIST -- Interactive AI Fiction Platform."""
    pass


@cli.command()
def templates() -> None:
    """List available story templates."""
    print_banner()
    print_template_list(TEMPLATES)


@cli.command()
@click.option("--template", "-t", type=click.Choice(list(TEMPLATES.keys())), help="Story template to use")
@click.option("--save", "-s", type=click.Path(), default=None, help="Path to a saved game to resume")
@click.option("--player", "-p", type=str, default=None, help="Player name")
@click.option("--offline", is_flag=True, help="Play without LLM generation (template content only)")
def play(template: str | None, save: str | None, player: str | None, offline: bool) -> None:
    """Start or resume an interactive story."""
    from plottwist.story.engine import StoryEngine

    print_banner()

    # Load or create engine
    if save and Path(save).exists():
        console.print(f"[dim]Resuming from save: {save}[/dim]\n")
        engine = StoryEngine.from_save(save)
    elif template:
        tmpl = TEMPLATES[template]
        engine = StoryEngine.from_template(tmpl)
        console.print(f"[dim]Starting story: {tmpl.tagline}[/dim]\n")
    else:
        console.print("[red]Provide --template or --save to begin.[/red]")
        raise SystemExit(1)

    if player:
        engine.set_player_name(player)

    # Optional LLM narrator
    narrator = None
    dialogue_gen = None
    if not offline:
        try:
            from plottwist.generator.narrator import Narrator
            from plottwist.generator.dialogue import DialogueGenerator

            narrator = Narrator()
            dialogue_gen = DialogueGenerator()
        except Exception as exc:
            console.print(f"[yellow]LLM unavailable ({exc}). Running in offline mode.[/yellow]\n")

    # -- game loop -------------------------------------------------------------

    save_path = save or f"plottwist_save_{engine.state.template_name}.json"

    _play_loop(engine, narrator, dialogue_gen, save_path)


def _play_loop(engine, narrator, dialogue_gen, save_path: str) -> None:
    """Main interactive game loop."""
    from plottwist.story.choices import ChoiceTree

    # Show opening scene
    scene = engine.current_scene()
    if scene is None:
        console.print("[red]No scene to display.[/red]")
        return

    narration = ""
    if narrator:
        try:
            narration = narrator.narrate_scene(engine)
        except Exception as exc:
            console.print(f"[yellow]Narration error: {exc}[/yellow]")

    print_scene(engine, narration)

    while True:
        # Get choices
        options = engine.available_choices()

        if not options and narrator:
            try:
                console.print("[dim]Generating new choices...[/dim]")
                node = narrator.generate_choices(engine)
                options = engine.available_choices()
            except Exception as exc:
                console.print(f"[yellow]Choice generation error: {exc}[/yellow]")

        if not options:
            console.print("\n[bold]The story has reached a pause. No choices available.[/bold]")
            console.print(f"[dim]Game saved to {save_path}[/dim]")
            engine.save(save_path)
            return

        # Display choices
        node = engine.choice_tree.current_node()
        prompt = node.prompt if node else "What do you do?"
        print_choices(options, prompt)

        # Player input
        try:
            raw = console.input("[bold cyan]> [/bold cyan]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Saving and exiting...[/dim]")
            engine.save(save_path)
            return

        if raw.lower() in ("quit", "exit", "q"):
            engine.save(save_path)
            console.print(f"\n[dim]Game saved to {save_path}. Goodbye![/dim]")
            return
        if raw.lower() in ("save",):
            engine.save(save_path)
            console.print(f"[green]Saved to {save_path}[/green]")
            continue
        if raw.lower() in ("status", "report"):
            print_story_report(engine)
            continue

        # Parse choice
        try:
            idx = int(raw) - 1
            if idx < 0 or idx >= len(options):
                raise ValueError
        except ValueError:
            console.print("[red]Enter a number corresponding to a choice, or 'quit'.[/red]")
            continue

        selected = options[idx]

        # Apply choice
        try:
            consequences = engine.make_choice(selected.id)
        except Exception as exc:
            console.print(f"[red]Error: {exc}[/red]")
            continue

        # Show consequences
        for c in consequences:
            print_consequence(c.description, c.severity.value)

        # Narrate aftermath
        if narrator:
            try:
                aftermath = narrator.narrate_consequence(engine, selected.text, consequences)
                print_narration(aftermath)
            except Exception as exc:
                console.print(f"[yellow]Narration error: {exc}[/yellow]")

        # Generate next scene
        if narrator:
            try:
                console.print("[dim]The story continues...[/dim]\n")
                new_scene = narrator.generate_next_scene(
                    engine, transition_hint=selected.text
                )
                scene_narration = narrator.narrate_scene(engine)
                print_scene(engine, scene_narration)

                # Generate dialogue if characters are present
                chars = engine.characters_in_scene()
                if chars and dialogue_gen:
                    try:
                        line = dialogue_gen.generate_line(
                            chars[0], engine, situation="reacting to what just happened"
                        )
                        from plottwist.report import print_dialogue
                        print_dialogue(chars[0].name, line)
                    except Exception:
                        pass

            except Exception as exc:
                console.print(f"[yellow]Scene generation error: {exc}[/yellow]")
        else:
            console.print("\n[dim](Offline mode -- no new scene generated)[/dim]\n")

        # Auto-save
        engine.save(save_path)


@cli.command()
@click.option("--save", "-s", type=click.Path(exists=True), required=True, help="Path to saved game")
def report(save: str) -> None:
    """Generate a report for a saved story."""
    from plottwist.story.engine import StoryEngine

    engine = StoryEngine.from_save(save)
    print_story_report(engine)


if __name__ == "__main__":
    cli()
