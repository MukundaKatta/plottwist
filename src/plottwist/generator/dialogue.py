"""Character-appropriate dialogue generation via the Anthropic API."""

from __future__ import annotations

import os
from typing import Any

import anthropic

from plottwist.story.characters import Character
from plottwist.story.engine import StoryEngine

_DEFAULT_MODEL = "claude-sonnet-4-20250514"

_DIALOGUE_SYSTEM = """\
You are a dialogue writer for an interactive fiction story called PLOTTWIST.
When given a character profile and story context, write dialogue that:
- Matches the character's speech style and personality traits
- Reflects their current emotional state and arc phase
- Advances their goals or reveals their nature
- Feels natural and distinct from other characters
- Uses appropriate register (formal, casual, archaic, etc.)

Write ONLY the character's spoken words, with no narration or stage
directions. Keep responses to 1-3 sentences unless a monologue is requested.
"""


class DialogueGenerator:
    """Generates character-voiced dialogue using the Anthropic API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = _DEFAULT_MODEL,
    ) -> None:
        self.model = model
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY", ""),
        )

    def generate_line(
        self,
        character: Character,
        engine: StoryEngine,
        situation: str = "",
        responding_to: str = "",
    ) -> str:
        """Generate a single dialogue line for a character."""
        char_ctx = character.to_prompt_context()
        story_ctx = engine.build_prompt_context()

        user_msg = (
            f"CHARACTER PROFILE:\n{char_ctx}\n\n"
            f"STORY CONTEXT:\n{story_ctx}\n\n"
        )
        if responding_to:
            user_msg += f"RESPONDING TO: \"{responding_to}\"\n\n"
        if situation:
            user_msg += f"SITUATION: {situation}\n\n"
        user_msg += (
            f"Write a dialogue line for {character.name}. "
            f"Return ONLY their spoken words, no quotation marks or attribution."
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=256,
            system=_DIALOGUE_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        line = response.content[0].text.strip().strip('"').strip("'")
        engine.record_dialogue(character.name, line)
        return line

    def generate_conversation(
        self,
        characters: list[Character],
        engine: StoryEngine,
        topic: str,
        num_exchanges: int = 3,
    ) -> list[dict[str, str]]:
        """Generate a multi-turn conversation between characters."""
        char_profiles = "\n---\n".join(c.to_prompt_context() for c in characters)
        char_names = [c.name for c in characters]
        story_ctx = engine.build_prompt_context()

        user_msg = (
            f"CHARACTER PROFILES:\n{char_profiles}\n\n"
            f"STORY CONTEXT:\n{story_ctx}\n\n"
            f"TOPIC: {topic}\n\n"
            f"Write a conversation with exactly {num_exchanges} exchanges "
            f"between: {', '.join(char_names)}.\n"
            f"Each character should speak at least once.\n"
            f"Format each line as: CHARACTER_NAME: dialogue text\n"
            f"Write ONLY the dialogue lines, nothing else."
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=_DIALOGUE_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = response.content[0].text.strip()

        exchanges: list[dict[str, str]] = []
        for line in raw.split("\n"):
            line = line.strip()
            if not line or ":" not in line:
                continue
            speaker, _, text = line.partition(":")
            speaker = speaker.strip()
            text = text.strip().strip('"').strip("'")
            if text:
                exchanges.append({"speaker": speaker, "text": text})
                # Find matching character to record
                for c in characters:
                    if c.name.lower() == speaker.lower():
                        engine.record_dialogue(c.name, text)
                        break

        return exchanges

    def generate_inner_thought(
        self,
        character: Character,
        engine: StoryEngine,
        trigger: str = "",
    ) -> str:
        """Generate a character's internal monologue or thought."""
        char_ctx = character.to_prompt_context()
        story_ctx = engine.build_prompt_context()

        user_msg = (
            f"CHARACTER PROFILE:\n{char_ctx}\n\n"
            f"STORY CONTEXT:\n{story_ctx}\n\n"
        )
        if trigger:
            user_msg += f"TRIGGERED BY: {trigger}\n\n"
        user_msg += (
            f"Write 1-2 sentences of {character.name}'s inner thought. "
            f"Use italicized style (no actual markdown). "
            f"Reflect their personality and current concerns."
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=256,
            system=_DIALOGUE_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        return response.content[0].text.strip()
