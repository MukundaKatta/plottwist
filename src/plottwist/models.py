"""Core Pydantic data models for PLOTTWIST."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Genre(str, Enum):
    MYSTERY = "mystery"
    FANTASY = "fantasy"
    SCIFI = "scifi"
    HORROR = "horror"
    ROMANCE = "romance"
    CUSTOM = "custom"


class Tone(str, Enum):
    DARK = "dark"
    LIGHT = "light"
    SUSPENSEFUL = "suspenseful"
    HUMOROUS = "humorous"
    EPIC = "epic"
    INTIMATE = "intimate"


class ArcPhase(str, Enum):
    """Tracks where a character sits on their narrative arc."""
    INTRODUCTION = "introduction"
    RISING = "rising"
    CRISIS = "crisis"
    CLIMAX = "climax"
    RESOLUTION = "resolution"


class SceneType(str, Enum):
    EXPLORATION = "exploration"
    DIALOGUE = "dialogue"
    ACTION = "action"
    PUZZLE = "puzzle"
    REVELATION = "revelation"
    CHOICE = "choice"


class ConsequenceSeverity(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Character models
# ---------------------------------------------------------------------------

class PersonalityTraits(BaseModel):
    """Big-five-inspired personality axes, each 0-100."""
    openness: int = Field(default=50, ge=0, le=100)
    conscientiousness: int = Field(default=50, ge=0, le=100)
    extraversion: int = Field(default=50, ge=0, le=100)
    agreeableness: int = Field(default=50, ge=0, le=100)
    neuroticism: int = Field(default=50, ge=0, le=100)


class CharacterGoal(BaseModel):
    description: str
    priority: int = Field(default=1, ge=1, le=5)
    achieved: bool = False
    blocked_by: list[str] = Field(default_factory=list)


class CharacterRelationship(BaseModel):
    target_id: str
    target_name: str
    disposition: int = Field(default=0, ge=-100, le=100)
    tags: list[str] = Field(default_factory=list)


class CharacterData(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str
    role: str = "supporting"
    backstory: str = ""
    personality: PersonalityTraits = Field(default_factory=PersonalityTraits)
    goals: list[CharacterGoal] = Field(default_factory=list)
    relationships: list[CharacterRelationship] = Field(default_factory=list)
    arc_phase: ArcPhase = ArcPhase.INTRODUCTION
    alive: bool = True
    present_in_scene: bool = False
    speech_style: str = ""
    inventory: list[str] = Field(default_factory=list)
    secrets: list[str] = Field(default_factory=list)
    notes: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# World models
# ---------------------------------------------------------------------------

class SettingData(BaseModel):
    name: str
    description: str
    atmosphere: str = ""
    time_period: str = ""
    locations: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)


class SceneData(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str
    description: str = ""
    setting_context: str = ""
    scene_type: SceneType = SceneType.EXPLORATION
    characters_present: list[str] = Field(default_factory=list)
    available_actions: list[str] = Field(default_factory=list)
    mood: Tone = Tone.SUSPENSEFUL
    discovered_clues: list[str] = Field(default_factory=list)
    notes: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Choice / consequence models
# ---------------------------------------------------------------------------

class Consequence(BaseModel):
    description: str
    severity: ConsequenceSeverity = ConsequenceSeverity.MINOR
    affects_characters: list[str] = Field(default_factory=list)
    state_changes: dict[str, Any] = Field(default_factory=dict)
    unlocks: list[str] = Field(default_factory=list)
    locks: list[str] = Field(default_factory=list)


class ChoiceOption(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    text: str
    requires: list[str] = Field(default_factory=list)
    consequences: list[Consequence] = Field(default_factory=list)
    leads_to: str | None = None
    hidden: bool = False


class ChoiceNode(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    prompt: str
    context: str = ""
    options: list[ChoiceOption] = Field(default_factory=list)
    parent_id: str | None = None
    scene_id: str | None = None


# ---------------------------------------------------------------------------
# Story-level models
# ---------------------------------------------------------------------------

class StoryEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    scene_id: str
    event_type: str  # "narration", "dialogue", "choice", "consequence"
    content: str
    actor: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class StoryState(BaseModel):
    """Top-level mutable state of a running story."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    template_name: str = ""
    genre: Genre = Genre.CUSTOM
    tone: Tone = Tone.SUSPENSEFUL
    setting: SettingData | None = None
    characters: dict[str, CharacterData] = Field(default_factory=dict)
    scenes: dict[str, SceneData] = Field(default_factory=dict)
    current_scene_id: str | None = None
    choice_nodes: dict[str, ChoiceNode] = Field(default_factory=dict)
    history: list[StoryEvent] = Field(default_factory=list)
    flags: dict[str, Any] = Field(default_factory=dict)
    turn_count: int = 0
    player_name: str = "Traveler"

    @property
    def current_scene(self) -> SceneData | None:
        if self.current_scene_id and self.current_scene_id in self.scenes:
            return self.scenes[self.current_scene_id]
        return None


class StoryTemplate(BaseModel):
    """Blueprint for initialising a new story."""
    name: str
    genre: Genre
    tone: Tone
    tagline: str = ""
    setting: SettingData
    characters: list[CharacterData]
    opening_scene: SceneData
    initial_choice: ChoiceNode
    flags: dict[str, Any] = Field(default_factory=dict)
