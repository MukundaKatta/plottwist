#!/usr/bin/env python3
"""Quick-start example: play through the mystery template offline."""

from plottwist.story.engine import StoryEngine
from plottwist.story.characters import Character
from plottwist.templates import TEMPLATES
from plottwist.report import (
    print_banner,
    print_scene,
    print_choices,
    print_consequence,
    print_story_report,
)


def main() -> None:
    print_banner()

    # Load the mystery template
    template = TEMPLATES["mystery"]
    engine = StoryEngine.from_template(template)
    engine.set_player_name("Detective Quinn")

    # Show the opening scene
    print_scene(engine)

    # Show available choices
    options = engine.available_choices()
    print_choices(options, "The clock strikes one. What is your first move?")

    # Automatically pick the first option
    print(f"\n--- Auto-selecting: '{options[0].text}' ---\n")
    consequences = engine.make_choice(options[0].id)
    for c in consequences:
        print_consequence(c.description, c.severity.value)

    # Inspect a character
    print("\n--- Character Details ---")
    doctor = engine.get_character("doctor")
    if doctor:
        print(doctor.personality_summary())
        print(doctor.to_prompt_context())

    # Show story report
    print("\n")
    print_story_report(engine)


if __name__ == "__main__":
    main()
