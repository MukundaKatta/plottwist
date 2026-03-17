"""Tests for Setting and Scene wrappers."""

from plottwist.models import SceneData, SceneType, SettingData, Tone
from plottwist.story.world import Scene, Setting


def test_setting_locations():
    s = Setting(SettingData(name="Forest", description="Dark woods"))
    s.add_location("Clearing")
    s.add_location("Cave")
    s.add_location("Clearing")  # duplicate
    assert len(s.data.locations) == 2


def test_setting_rules():
    s = Setting(SettingData(name="Castle", description="A grand castle"))
    s.add_rule("No magic allowed")
    s.add_rule("No magic allowed")  # duplicate
    assert len(s.data.rules) == 1


def test_setting_prompt_context():
    s = Setting(SettingData(
        name="Dungeon",
        description="A dank dungeon",
        atmosphere="Oppressive",
        time_period="Medieval",
        locations=["Cell", "Corridor"],
        rules=["Torch required"],
    ))
    ctx = s.to_prompt_context()
    assert "Dungeon" in ctx
    assert "Oppressive" in ctx
    assert "Medieval" in ctx
    assert "Cell" in ctx
    assert "Torch required" in ctx


def test_scene_character_management():
    sc = Scene(SceneData(title="Battle"))
    sc.add_character("hero")
    sc.add_character("villain")
    assert sc.has_character("hero")
    sc.remove_character("hero")
    assert not sc.has_character("hero")


def test_scene_actions():
    sc = Scene(SceneData(title="Explore"))
    sc.add_action("Look around")
    sc.add_action("Open door")
    sc.remove_action("Look around")
    assert "Look around" not in sc.data.available_actions
    assert "Open door" in sc.data.available_actions


def test_scene_clues():
    sc = Scene(SceneData(title="Library"))
    sc.discover_clue("Torn letter")
    sc.discover_clue("Torn letter")  # duplicate
    assert len(sc.data.discovered_clues) == 1


def test_scene_prompt_context():
    sc = Scene(SceneData(
        title="The Arrival",
        description="You step into the hall",
        setting_context="Grand hall at dusk",
        scene_type=SceneType.DIALOGUE,
        mood=Tone.DARK,
        characters_present=["npc1"],
        discovered_clues=["A bloody glove"],
    ))
    ctx = sc.to_prompt_context()
    assert "The Arrival" in ctx
    assert "dialogue" in ctx
    assert "dark" in ctx
    assert "npc1" in ctx
    assert "bloody glove" in ctx
