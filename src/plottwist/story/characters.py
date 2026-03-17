"""Character management -- personality, goals, arc tracking."""

from __future__ import annotations

from plottwist.models import (
    ArcPhase,
    CharacterData,
    CharacterGoal,
    CharacterRelationship,
    PersonalityTraits,
)

# Arc progression order
_ARC_ORDER: list[ArcPhase] = [
    ArcPhase.INTRODUCTION,
    ArcPhase.RISING,
    ArcPhase.CRISIS,
    ArcPhase.CLIMAX,
    ArcPhase.RESOLUTION,
]


class Character:
    """Wraps a CharacterData model with behaviour helpers."""

    def __init__(self, data: CharacterData) -> None:
        self.data = data

    # -- convenience properties ------------------------------------------------

    @property
    def id(self) -> str:
        return self.data.id

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def personality(self) -> PersonalityTraits:
        return self.data.personality

    @property
    def arc_phase(self) -> ArcPhase:
        return self.data.arc_phase

    @property
    def is_alive(self) -> bool:
        return self.data.alive

    # -- personality helpers ---------------------------------------------------

    def dominant_traits(self, top_n: int = 2) -> list[str]:
        """Return the *top_n* highest-scoring personality trait names."""
        scores = self.personality.model_dump()
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        return [name for name, _ in ranked[:top_n]]

    def personality_summary(self) -> str:
        """One-line human-readable personality sketch."""
        dom = self.dominant_traits(3)
        return f"{self.name}: {', '.join(dom)} (arc: {self.arc_phase.value})"

    # -- goal management -------------------------------------------------------

    def add_goal(self, description: str, priority: int = 1) -> CharacterGoal:
        goal = CharacterGoal(description=description, priority=priority)
        self.data.goals.append(goal)
        return goal

    def achieve_goal(self, description: str) -> bool:
        for g in self.data.goals:
            if g.description == description and not g.achieved:
                g.achieved = True
                return True
        return False

    def active_goals(self) -> list[CharacterGoal]:
        return [g for g in self.data.goals if not g.achieved]

    # -- relationship management -----------------------------------------------

    def set_relationship(
        self, target_id: str, target_name: str, disposition: int, tags: list[str] | None = None
    ) -> CharacterRelationship:
        for rel in self.data.relationships:
            if rel.target_id == target_id:
                rel.disposition = max(-100, min(100, disposition))
                if tags is not None:
                    rel.tags = tags
                return rel
        rel = CharacterRelationship(
            target_id=target_id,
            target_name=target_name,
            disposition=max(-100, min(100, disposition)),
            tags=tags or [],
        )
        self.data.relationships.append(rel)
        return rel

    def adjust_disposition(self, target_id: str, delta: int) -> int | None:
        for rel in self.data.relationships:
            if rel.target_id == target_id:
                rel.disposition = max(-100, min(100, rel.disposition + delta))
                return rel.disposition
        return None

    def relationship_with(self, target_id: str) -> CharacterRelationship | None:
        for rel in self.data.relationships:
            if rel.target_id == target_id:
                return rel
        return None

    # -- arc progression -------------------------------------------------------

    def advance_arc(self) -> ArcPhase:
        """Move the character to the next arc phase if possible."""
        idx = _ARC_ORDER.index(self.data.arc_phase)
        if idx < len(_ARC_ORDER) - 1:
            self.data.arc_phase = _ARC_ORDER[idx + 1]
        return self.data.arc_phase

    def set_arc_phase(self, phase: ArcPhase) -> None:
        self.data.arc_phase = phase

    # -- inventory / secrets ---------------------------------------------------

    def give_item(self, item: str) -> None:
        if item not in self.data.inventory:
            self.data.inventory.append(item)

    def remove_item(self, item: str) -> bool:
        if item in self.data.inventory:
            self.data.inventory.remove(item)
            return True
        return False

    def has_item(self, item: str) -> bool:
        return item in self.data.inventory

    def add_secret(self, secret: str) -> None:
        if secret not in self.data.secrets:
            self.data.secrets.append(secret)

    # -- serialisation ---------------------------------------------------------

    def to_prompt_context(self) -> str:
        """Produce a compact text block suitable for injecting into LLM prompts."""
        lines = [
            f"Name: {self.name}",
            f"Role: {self.data.role}",
            f"Arc phase: {self.arc_phase.value}",
            f"Personality: {', '.join(self.dominant_traits(3))}",
        ]
        if self.data.speech_style:
            lines.append(f"Speech style: {self.data.speech_style}")
        if self.data.backstory:
            lines.append(f"Backstory: {self.data.backstory}")
        active = self.active_goals()
        if active:
            lines.append("Active goals: " + "; ".join(g.description for g in active))
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"<Character {self.name!r} ({self.arc_phase.value})>"
