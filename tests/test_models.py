"""Tests for core Pydantic models."""

import json

from plottwist.models import (
    ArcPhase,
    CharacterData,
    CharacterGoal,
    ChoiceNode,
    ChoiceOption,
    Consequence,
    ConsequenceSeverity,
    Genre,
    PersonalityTraits,
    SceneData,
    SceneType,
    SettingData,
    StoryState,
    StoryTemplate,
    Tone,
)


def test_personality_traits_defaults():
    traits = PersonalityTraits()
    assert traits.openness == 50
    assert traits.neuroticism == 50


def test_personality_traits_bounds():
    traits = PersonalityTraits(openness=100, neuroticism=0)
    assert traits.openness == 100
    assert traits.neuroticism == 0


def test_character_data_creation():
    char = CharacterData(name="Alice", role="protagonist")
    assert char.name == "Alice"
    assert char.alive is True
    assert char.arc_phase == ArcPhase.INTRODUCTION
    assert len(char.id) == 12


def test_character_data_with_goals():
    goal = CharacterGoal(description="Find the treasure", priority=3)
    char = CharacterData(name="Bob", goals=[goal])
    assert len(char.goals) == 1
    assert char.goals[0].priority == 3
    assert char.goals[0].achieved is False


def test_setting_data():
    setting = SettingData(
        name="Dark Forest",
        description="A foreboding woodland",
        locations=["Clearing", "Cave"],
    )
    assert setting.name == "Dark Forest"
    assert len(setting.locations) == 2


def test_scene_data_defaults():
    scene = SceneData(title="Opening")
    assert scene.scene_type == SceneType.EXPLORATION
    assert scene.mood == Tone.SUSPENSEFUL


def test_consequence_model():
    c = Consequence(
        description="The door locks behind you",
        severity=ConsequenceSeverity.MAJOR,
        unlocks=["secret_room"],
        locks=["main_hall"],
    )
    assert c.severity == ConsequenceSeverity.MAJOR
    assert "secret_room" in c.unlocks
    assert "main_hall" in c.locks


def test_choice_node_with_options():
    opt = ChoiceOption(text="Go left", leads_to="scene_2")
    node = ChoiceNode(prompt="Which way?", options=[opt])
    assert len(node.options) == 1
    assert node.options[0].text == "Go left"


def test_story_state_serialization():
    state = StoryState(
        template_name="test",
        genre=Genre.MYSTERY,
        player_name="Tester",
    )
    json_str = state.model_dump_json()
    loaded = StoryState.model_validate_json(json_str)
    assert loaded.player_name == "Tester"
    assert loaded.genre == Genre.MYSTERY


def test_story_state_current_scene_property():
    scene = SceneData(id="s1", title="Start")
    state = StoryState(
        scenes={"s1": scene},
        current_scene_id="s1",
    )
    assert state.current_scene is not None
    assert state.current_scene.title == "Start"


def test_story_state_current_scene_none():
    state = StoryState()
    assert state.current_scene is None


def test_story_template():
    tmpl = StoryTemplate(
        name="test",
        genre=Genre.FANTASY,
        tone=Tone.EPIC,
        setting=SettingData(name="Realm", description="A magical realm"),
        characters=[CharacterData(name="Hero")],
        opening_scene=SceneData(id="s1", title="Begin"),
        initial_choice=ChoiceNode(prompt="Choose", options=[]),
    )
    assert tmpl.genre == Genre.FANTASY
    assert tmpl.characters[0].name == "Hero"
