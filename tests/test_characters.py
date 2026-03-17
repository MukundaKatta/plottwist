"""Tests for the Character wrapper class."""

from plottwist.models import ArcPhase, CharacterData, PersonalityTraits
from plottwist.story.characters import Character


def _make_char(**kwargs) -> Character:
    defaults = dict(name="Test Char", role="protagonist")
    defaults.update(kwargs)
    return Character(CharacterData(**defaults))


def test_dominant_traits():
    char = _make_char(
        personality=PersonalityTraits(
            openness=90, conscientiousness=10, extraversion=70, agreeableness=30, neuroticism=50
        )
    )
    top2 = char.dominant_traits(2)
    assert top2 == ["openness", "extraversion"]


def test_personality_summary():
    char = _make_char(name="Alice")
    summary = char.personality_summary()
    assert "Alice" in summary
    assert "introduction" in summary


def test_add_and_achieve_goal():
    char = _make_char()
    char.add_goal("Save the world", priority=5)
    assert len(char.active_goals()) == 1
    assert char.achieve_goal("Save the world") is True
    assert len(char.active_goals()) == 0


def test_achieve_nonexistent_goal():
    char = _make_char()
    assert char.achieve_goal("Nope") is False


def test_set_and_adjust_relationship():
    char = _make_char()
    rel = char.set_relationship("npc1", "Bob", 50, tags=["ally"])
    assert rel.disposition == 50
    assert "ally" in rel.tags

    # Adjust
    new_disp = char.adjust_disposition("npc1", -30)
    assert new_disp == 20

    # Update existing
    char.set_relationship("npc1", "Bob", -80)
    assert char.relationship_with("npc1").disposition == -80


def test_adjust_disposition_clamps():
    char = _make_char()
    char.set_relationship("x", "X", 95)
    char.adjust_disposition("x", 50)
    assert char.relationship_with("x").disposition == 100

    char.adjust_disposition("x", -300)
    assert char.relationship_with("x").disposition == -100


def test_adjust_disposition_missing():
    char = _make_char()
    assert char.adjust_disposition("nobody", 10) is None


def test_arc_advancement():
    char = _make_char()
    assert char.arc_phase == ArcPhase.INTRODUCTION
    char.advance_arc()
    assert char.arc_phase == ArcPhase.RISING
    char.advance_arc()
    assert char.arc_phase == ArcPhase.CRISIS
    char.advance_arc()
    assert char.arc_phase == ArcPhase.CLIMAX
    char.advance_arc()
    assert char.arc_phase == ArcPhase.RESOLUTION
    # Should stay at resolution
    char.advance_arc()
    assert char.arc_phase == ArcPhase.RESOLUTION


def test_inventory():
    char = _make_char()
    char.give_item("Sword")
    assert char.has_item("Sword")
    char.give_item("Sword")  # duplicate
    assert len(char.data.inventory) == 1

    assert char.remove_item("Sword") is True
    assert not char.has_item("Sword")
    assert char.remove_item("Sword") is False


def test_secrets():
    char = _make_char()
    char.add_secret("hidden past")
    char.add_secret("hidden past")  # duplicate
    assert len(char.data.secrets) == 1


def test_to_prompt_context():
    char = _make_char(
        name="Hero",
        role="protagonist",
        speech_style="Gruff and direct",
        backstory="A wandering knight",
    )
    char.add_goal("Defeat the dragon")
    ctx = char.to_prompt_context()
    assert "Hero" in ctx
    assert "protagonist" in ctx
    assert "Gruff and direct" in ctx
    assert "Defeat the dragon" in ctx
