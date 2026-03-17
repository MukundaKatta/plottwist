"""LLM-powered narrative generation using the Anthropic API."""

from __future__ import annotations

import json
import os
from typing import Any

import anthropic

from plottwist.models import ChoiceNode, ChoiceOption, Consequence, ConsequenceSeverity, SceneData, SceneType, Tone
from plottwist.story.engine import StoryEngine

_DEFAULT_MODEL = "claude-sonnet-4-20250514"

_SYSTEM_PROMPT = """\
You are the narrator of an interactive fiction story called PLOTTWIST.
Your job is to write immersive, vivid, second-person prose that draws the reader
into the world.  Keep paragraphs punchy (2-4 sentences).  Vary sentence length
for rhythm.  Never break the fourth wall.  Honour the genre, tone, and world
rules provided in the context.

When asked to generate choices, produce exactly the number requested.  Each
choice should feel meaningfully different and have plausible consequences.
Always respond in the requested JSON schema when asked for structured output.
"""


class Narrator:
    """Generates narrative prose and dynamic choices via the Anthropic API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = _DEFAULT_MODEL,
    ) -> None:
        self.model = model
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY", ""),
        )

    # -- narrative generation --------------------------------------------------

    def narrate_scene(self, engine: StoryEngine, extra_instruction: str = "") -> str:
        """Generate narrative prose for the current scene."""
        context = engine.build_prompt_context()
        user_msg = (
            f"Write 2-3 paragraphs of narrative prose for the current scene.\n\n"
            f"CONTEXT:\n{context}"
        )
        if extra_instruction:
            user_msg += f"\n\nADDITIONAL INSTRUCTION: {extra_instruction}"

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = response.content[0].text
        engine.record_narration(text)
        return text

    def narrate_consequence(self, engine: StoryEngine, choice_text: str, consequences: list[Consequence]) -> str:
        """Generate prose describing the aftermath of a player choice."""
        context = engine.build_prompt_context()
        consequence_desc = "; ".join(c.description for c in consequences if c.description)
        user_msg = (
            f"The player chose: \"{choice_text}\"\n"
            f"Consequences: {consequence_desc}\n\n"
            f"Write 1-2 paragraphs showing the immediate result of this choice.\n\n"
            f"CONTEXT:\n{context}"
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=768,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = response.content[0].text
        engine.record_narration(text)
        return text

    # -- dynamic choice generation ---------------------------------------------

    def generate_choices(
        self,
        engine: StoryEngine,
        num_choices: int = 3,
        scene_id: str | None = None,
    ) -> ChoiceNode:
        """Ask the LLM to produce a new set of choices for the current scene."""
        context = engine.build_prompt_context()
        flags = json.dumps(dict(engine.state.flags))
        user_msg = (
            f"Generate exactly {num_choices} choices for the player.\n\n"
            f"Current flags: {flags}\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"Respond with ONLY valid JSON matching this schema:\n"
            f'{{"prompt": "<question to the player>", '
            f'"options": [{{"text": "<option text>", "consequence_description": "<what happens>", '
            f'"severity": "minor|moderate|major|critical", "state_changes": {{}}}}]}}'
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = response.content[0].text.strip()
        # Extract JSON from possible markdown fences
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        data = json.loads(raw)

        options: list[ChoiceOption] = []
        for opt_raw in data.get("options", []):
            consequence = Consequence(
                description=opt_raw.get("consequence_description", ""),
                severity=ConsequenceSeverity(opt_raw.get("severity", "minor")),
                state_changes=opt_raw.get("state_changes", {}),
            )
            options.append(
                ChoiceOption(
                    text=opt_raw["text"],
                    consequences=[consequence],
                )
            )

        node = ChoiceNode(
            prompt=data.get("prompt", "What do you do?"),
            options=options,
            scene_id=scene_id or engine.state.current_scene_id,
        )
        engine.register_choice_node(node)
        return node

    # -- scene generation ------------------------------------------------------

    def generate_next_scene(
        self,
        engine: StoryEngine,
        transition_hint: str = "",
    ) -> SceneData:
        """Ask the LLM to create the next scene after a choice."""
        context = engine.build_prompt_context()
        user_msg = (
            f"Generate the next scene in the story.\n"
            f"Transition hint: {transition_hint}\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"Respond with ONLY valid JSON:\n"
            f'{{"title": "...", "description": "...", "setting_context": "...", '
            f'"scene_type": "exploration|dialogue|action|puzzle|revelation|choice", '
            f'"mood": "dark|light|suspenseful|humorous|epic|intimate", '
            f'"characters_present": ["<character_ids>"], '
            f'"available_actions": ["<actions>"]}}'
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=768,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        data = json.loads(raw)

        scene = SceneData(
            title=data.get("title", "Untitled Scene"),
            description=data.get("description", ""),
            setting_context=data.get("setting_context", ""),
            scene_type=SceneType(data.get("scene_type", "exploration")),
            mood=Tone(data.get("mood", "suspenseful")),
            characters_present=data.get("characters_present", []),
            available_actions=data.get("available_actions", []),
        )
        engine.transition_to_scene(scene)
        return scene
