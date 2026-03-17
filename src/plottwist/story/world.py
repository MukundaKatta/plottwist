"""World state -- Setting and Scene management."""

from __future__ import annotations

from plottwist.models import SceneData, SceneType, SettingData, Tone


class Setting:
    """Wraps a SettingData model with helper methods."""

    def __init__(self, data: SettingData) -> None:
        self.data = data

    @property
    def name(self) -> str:
        return self.data.name

    def add_location(self, location: str) -> None:
        if location not in self.data.locations:
            self.data.locations.append(location)

    def add_rule(self, rule: str) -> None:
        if rule not in self.data.rules:
            self.data.rules.append(rule)

    def to_prompt_context(self) -> str:
        lines = [
            f"Setting: {self.data.name}",
            f"Description: {self.data.description}",
        ]
        if self.data.atmosphere:
            lines.append(f"Atmosphere: {self.data.atmosphere}")
        if self.data.time_period:
            lines.append(f"Time period: {self.data.time_period}")
        if self.data.locations:
            lines.append(f"Known locations: {', '.join(self.data.locations)}")
        if self.data.rules:
            lines.append("World rules: " + "; ".join(self.data.rules))
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"<Setting {self.name!r}>"


class Scene:
    """Wraps a SceneData model with helpers for scene lifecycle."""

    def __init__(self, data: SceneData) -> None:
        self.data = data

    @property
    def id(self) -> str:
        return self.data.id

    @property
    def title(self) -> str:
        return self.data.title

    @property
    def scene_type(self) -> SceneType:
        return self.data.scene_type

    @property
    def mood(self) -> Tone:
        return self.data.mood

    # -- character presence ----------------------------------------------------

    def add_character(self, character_id: str) -> None:
        if character_id not in self.data.characters_present:
            self.data.characters_present.append(character_id)

    def remove_character(self, character_id: str) -> None:
        if character_id in self.data.characters_present:
            self.data.characters_present.remove(character_id)

    def has_character(self, character_id: str) -> bool:
        return character_id in self.data.characters_present

    # -- actions & clues -------------------------------------------------------

    def add_action(self, action: str) -> None:
        if action not in self.data.available_actions:
            self.data.available_actions.append(action)

    def remove_action(self, action: str) -> None:
        if action in self.data.available_actions:
            self.data.available_actions.remove(action)

    def discover_clue(self, clue: str) -> None:
        if clue not in self.data.discovered_clues:
            self.data.discovered_clues.append(clue)

    # -- prompt context --------------------------------------------------------

    def to_prompt_context(self) -> str:
        lines = [
            f"Scene: {self.title}",
            f"Type: {self.scene_type.value}",
            f"Mood: {self.mood.value}",
        ]
        if self.data.description:
            lines.append(f"Description: {self.data.description}")
        if self.data.setting_context:
            lines.append(f"Location detail: {self.data.setting_context}")
        if self.data.characters_present:
            lines.append(f"Characters present: {', '.join(self.data.characters_present)}")
        if self.data.discovered_clues:
            lines.append(f"Clues found: {', '.join(self.data.discovered_clues)}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"<Scene {self.title!r} ({self.scene_type.value})>"
