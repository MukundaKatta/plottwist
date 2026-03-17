#!/usr/bin/env python3
"""Demo: bootstrap every built-in template and show their opening state."""

from plottwist.story.engine import StoryEngine
from plottwist.templates import TEMPLATES
from plottwist.report import console, print_banner, print_scene, print_choices


def main() -> None:
    print_banner()

    for name, template in TEMPLATES.items():
        console.rule(f"[bold magenta]{name.upper()}[/bold magenta] -- {template.tagline}")
        engine = StoryEngine.from_template(template)
        print_scene(engine)
        options = engine.available_choices()
        node = engine.choice_tree.current_node()
        prompt = node.prompt if node else "What do you do?"
        print_choices(options, prompt)

    console.print("[dim]Run 'plottwist play --template <name>' to begin an interactive session.[/dim]")


if __name__ == "__main__":
    main()
