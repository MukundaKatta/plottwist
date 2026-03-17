"""StoryEngine -- the central state machine driving a branching narrative."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from plottwist.models import (
    ChoiceNode,
    SceneData,
    StoryEvent,
    StoryState,
    StoryTemplate,
)
from plottwist.story.characters import Character
from plottwist.story.choices import ChoiceTree
from plottwist.story.world import Scene, Setting


class StoryEngine:
    """Orchestrates story state, character management, scene transitions,
    and the choice tree for a single play-through.

    Usage::

        engine = StoryEngine.from_template(mystery_template)
        engine.set_player_name("Ada")
        scene = engine.current_scene()
        choices = engine.available_choices()
        consequences = engine.make_choice(choices[0].id)
    """

    def __init__(self, state: StoryState) -> None:
        self.state = state
        self.choice_tree = ChoiceTree(state)
        # Wrap character data in Character helpers
        self._characters: dict[str, Character] = {
            cid: Character(cdata) for cid, cdata in state.characters.items()
        }

    # -- factory ---------------------------------------------------------------

    @classmethod
    def from_template(cls, template: StoryTemplate) -> "StoryEngine":
        """Bootstrap an engine from a StoryTemplate blueprint."""
        state = StoryState(
            template_name=template.name,
            genre=template.genre,
            tone=template.tone,
            setting=template.setting,
            flags=dict(template.flags),
        )

        # Register characters
        for char_data in template.characters:
            state.characters[char_data.id] = char_data

        # Register opening scene
        scene = template.opening_scene
        state.scenes[scene.id] = scene
        state.current_scene_id = scene.id

        # Register initial choice
        initial = template.initial_choice
        initial.scene_id = scene.id
        state.choice_nodes[initial.id] = initial

        return cls(state)

    @classmethod
    def from_save(cls, path: str | Path) -> "StoryEngine":
        """Load a saved game from a JSON file."""
        raw = Path(path).read_text()
        state = StoryState.model_validate_json(raw)
        return cls(state)

    # -- persistence -----------------------------------------------------------

    def save(self, path: str | Path) -> Path:
        p = Path(path)
        p.write_text(self.state.model_dump_json(indent=2))
        return p

    # -- player ----------------------------------------------------------------

    def set_player_name(self, name: str) -> None:
        self.state.player_name = name

    # -- characters ------------------------------------------------------------

    def get_character(self, character_id: str) -> Character | None:
        return self._characters.get(character_id)

    def characters_in_scene(self) -> list[Character]:
        scene = self.current_scene()
        if scene is None:
            return []
        return [
            self._characters[cid]
            for cid in scene.data.characters_present
            if cid in self._characters
        ]

    def all_characters(self) -> list[Character]:
        return list(self._characters.values())

    # -- scenes ----------------------------------------------------------------

    def current_scene(self) -> Scene | None:
        sd = self.state.current_scene
        return Scene(sd) if sd else None

    def transition_to_scene(self, scene: SceneData) -> Scene:
        """Register a new scene and make it the current one."""
        self.state.scenes[scene.id] = scene
        self.state.current_scene_id = scene.id
        self.state.turn_count += 1
        self._record_event(scene.id, "scene_transition", f"Entered: {scene.title}")
        return Scene(scene)

    # -- choices ---------------------------------------------------------------

    def available_choices(self) -> list[Any]:
        """Return visible choice options for the current scene."""
        node = self.choice_tree.current_node()
        if node is None:
            return []
        return self.choice_tree.visible_options(node)

    def make_choice(self, option_id: str) -> list[Any]:
        """Select a choice option, apply consequences, record the event."""
        node = self.choice_tree.current_node()
        if node is None:
            raise RuntimeError("No active choice node for current scene")
        consequences = self.choice_tree.select_option(node, option_id)
        # Find option text for history
        opt_text = ""
        for opt in node.options:
            if opt.id == option_id:
                opt_text = opt.text
                break
        self._record_event(
            self.state.current_scene_id or "",
            "choice",
            opt_text,
            metadata={"option_id": option_id, "consequences": len(consequences)},
        )
        self.state.turn_count += 1
        return consequences

    def register_choice_node(self, node: ChoiceNode) -> None:
        """Add a dynamically-generated choice node to the tree."""
        self.choice_tree.add_node(node)

    # -- setting ---------------------------------------------------------------

    def setting(self) -> Setting | None:
        if self.state.setting:
            return Setting(self.state.setting)
        return None

    # -- history / context -----------------------------------------------------

    def recent_history(self, n: int = 10) -> list[StoryEvent]:
        return self.state.history[-n:]

    def history_as_text(self, n: int = 10) -> str:
        events = self.recent_history(n)
        lines: list[str] = []
        for ev in events:
            prefix = f"[{ev.event_type}]"
            if ev.actor:
                prefix += f" ({ev.actor})"
            lines.append(f"{prefix} {ev.content}")
        return "\n".join(lines)

    def build_prompt_context(self) -> str:
        """Assemble a context block for LLM prompts."""
        parts: list[str] = []
        setting = self.setting()
        if setting:
            parts.append(setting.to_prompt_context())
        scene = self.current_scene()
        if scene:
            parts.append(scene.to_prompt_context())
        chars = self.characters_in_scene()
        if chars:
            parts.append("--- Characters in scene ---")
            for c in chars:
                parts.append(c.to_prompt_context())
        history_text = self.history_as_text(8)
        if history_text:
            parts.append("--- Recent events ---")
            parts.append(history_text)
        parts.append(f"Player name: {self.state.player_name}")
        parts.append(f"Turn: {self.state.turn_count}")
        return "\n\n".join(parts)

    # -- internal --------------------------------------------------------------

    def _record_event(
        self,
        scene_id: str,
        event_type: str,
        content: str,
        actor: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> StoryEvent:
        event = StoryEvent(
            scene_id=scene_id,
            event_type=event_type,
            content=content,
            actor=actor,
            metadata=metadata or {},
        )
        self.state.history.append(event)
        return event

    def record_narration(self, text: str) -> StoryEvent:
        return self._record_event(
            self.state.current_scene_id or "", "narration", text
        )

    def record_dialogue(self, speaker: str, text: str) -> StoryEvent:
        return self._record_event(
            self.state.current_scene_id or "", "dialogue", text, actor=speaker
        )

    def __repr__(self) -> str:
        scene = self.current_scene()
        scene_label = scene.title if scene else "none"
        return f"<StoryEngine template={self.state.template_name!r} scene={scene_label!r} turn={self.state.turn_count}>"
