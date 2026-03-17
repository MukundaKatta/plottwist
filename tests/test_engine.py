"""Tests for the StoryEngine."""

import json
import tempfile
from pathlib import Path

from plottwist.models import (
    ArcPhase,
    CharacterData,
    ChoiceNode,
    ChoiceOption,
    Consequence,
    ConsequenceSeverity,
    Genre,
    SceneData,
    SceneType,
    SettingData,
    StoryTemplate,
    Tone,
)
from plottwist.story.engine import StoryEngine


def _make_template() -> StoryTemplate:
    return StoryTemplate(
        name="test_story",
        genre=Genre.MYSTERY,
        tone=Tone.SUSPENSEFUL,
        tagline="A test mystery",
        setting=SettingData(name="Test Manor", description="A spooky house"),
        characters=[
            CharacterData(id="npc1", name="Alice", role="suspect", present_in_scene=True),
            CharacterData(id="npc2", name="Bob", role="ally"),
        ],
        opening_scene=SceneData(
            id="scene1",
            title="The Beginning",
            description="It was a dark and stormy night.",
            characters_present=["npc1"],
        ),
        initial_choice=ChoiceNode(
            id="choice1",
            prompt="What do you do?",
            options=[
                ChoiceOption(
                    id="opt1",
                    text="Investigate",
                    consequences=[
                        Consequence(
                            description="You found a clue",
                            severity=ConsequenceSeverity.MINOR,
                            state_changes={"found_clue": True},
                        )
                    ],
                ),
                ChoiceOption(id="opt2", text="Wait"),
            ],
        ),
        flags={"started": True},
    )


def test_from_template():
    engine = StoryEngine.from_template(_make_template())
    assert engine.state.template_name == "test_story"
    assert engine.state.genre == Genre.MYSTERY
    assert len(engine.state.characters) == 2
    assert engine.state.current_scene_id == "scene1"


def test_player_name():
    engine = StoryEngine.from_template(_make_template())
    engine.set_player_name("Detective")
    assert engine.state.player_name == "Detective"


def test_current_scene():
    engine = StoryEngine.from_template(_make_template())
    scene = engine.current_scene()
    assert scene is not None
    assert scene.title == "The Beginning"


def test_characters_in_scene():
    engine = StoryEngine.from_template(_make_template())
    chars = engine.characters_in_scene()
    assert len(chars) == 1
    assert chars[0].name == "Alice"


def test_all_characters():
    engine = StoryEngine.from_template(_make_template())
    assert len(engine.all_characters()) == 2


def test_available_choices():
    engine = StoryEngine.from_template(_make_template())
    options = engine.available_choices()
    assert len(options) == 2


def test_make_choice():
    engine = StoryEngine.from_template(_make_template())
    consequences = engine.make_choice("opt1")
    assert len(consequences) == 1
    assert engine.state.flags.get("found_clue") is True
    assert engine.state.turn_count == 1
    # Check history recorded
    choice_events = [e for e in engine.state.history if e.event_type == "choice"]
    assert len(choice_events) == 1


def test_make_choice_no_node():
    engine = StoryEngine.from_template(_make_template())
    engine.state.current_scene_id = "nonexistent"
    try:
        engine.make_choice("opt1")
        assert False, "Should raise RuntimeError"
    except RuntimeError:
        pass


def test_transition_to_scene():
    engine = StoryEngine.from_template(_make_template())
    new_scene = SceneData(id="scene2", title="Chapter 2")
    scene = engine.transition_to_scene(new_scene)
    assert scene.title == "Chapter 2"
    assert engine.state.current_scene_id == "scene2"
    assert "scene2" in engine.state.scenes


def test_setting():
    engine = StoryEngine.from_template(_make_template())
    setting = engine.setting()
    assert setting is not None
    assert setting.name == "Test Manor"


def test_history():
    engine = StoryEngine.from_template(_make_template())
    engine.record_narration("The night was cold.")
    engine.record_dialogue("Alice", "Who goes there?")
    recent = engine.recent_history(5)
    assert len(recent) == 2
    text = engine.history_as_text(5)
    assert "narration" in text
    assert "Alice" in text


def test_build_prompt_context():
    engine = StoryEngine.from_template(_make_template())
    ctx = engine.build_prompt_context()
    assert "Test Manor" in ctx
    assert "The Beginning" in ctx


def test_save_and_load():
    engine = StoryEngine.from_template(_make_template())
    engine.set_player_name("Sherlock")
    engine.make_choice("opt1")

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name

    try:
        engine.save(path)
        loaded = StoryEngine.from_save(path)
        assert loaded.state.player_name == "Sherlock"
        assert loaded.state.flags.get("found_clue") is True
        assert loaded.state.turn_count == 1
    finally:
        Path(path).unlink(missing_ok=True)


def test_register_choice_node():
    engine = StoryEngine.from_template(_make_template())
    node = ChoiceNode(id="new_node", prompt="New choice", options=[], scene_id="scene1")
    engine.register_choice_node(node)
    assert "new_node" in engine.state.choice_nodes
