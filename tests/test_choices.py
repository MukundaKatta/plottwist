"""Tests for the ChoiceTree."""

from plottwist.models import (
    ChoiceNode,
    ChoiceOption,
    Consequence,
    ConsequenceSeverity,
    StoryState,
)
from plottwist.story.choices import ChoiceTree


def _make_state_with_node() -> tuple[StoryState, ChoiceNode]:
    state = StoryState(current_scene_id="s1")
    opt_a = ChoiceOption(
        id="opt_a",
        text="Go left",
        consequences=[
            Consequence(
                description="You find a key",
                severity=ConsequenceSeverity.MINOR,
                state_changes={"has_key": True},
                unlocks=["door_open"],
            )
        ],
    )
    opt_b = ChoiceOption(
        id="opt_b",
        text="Go right",
        requires=["has_key"],
    )
    opt_hidden = ChoiceOption(
        id="opt_h",
        text="Secret path",
        hidden=True,
    )
    node = ChoiceNode(
        id="node1",
        prompt="Which way?",
        options=[opt_a, opt_b, opt_hidden],
        scene_id="s1",
    )
    state.choice_nodes[node.id] = node
    return state, node


def test_visible_options_filters():
    state, node = _make_state_with_node()
    tree = ChoiceTree(state)
    visible = tree.visible_options(node)
    # opt_b requires has_key (not set), opt_h is hidden
    assert len(visible) == 1
    assert visible[0].id == "opt_a"


def test_visible_after_unlock():
    state, node = _make_state_with_node()
    state.flags["has_key"] = True
    tree = ChoiceTree(state)
    visible = tree.visible_options(node)
    assert len(visible) == 2
    ids = {o.id for o in visible}
    assert "opt_a" in ids
    assert "opt_b" in ids


def test_select_option_applies_consequences():
    state, node = _make_state_with_node()
    tree = ChoiceTree(state)
    consequences = tree.select_option(node, "opt_a")
    assert len(consequences) == 1
    assert state.flags.get("has_key") is True
    assert state.flags.get("door_open") is True


def test_select_invalid_option():
    state, node = _make_state_with_node()
    tree = ChoiceTree(state)
    try:
        tree.select_option(node, "nonexistent")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_current_node():
    state, node = _make_state_with_node()
    tree = ChoiceTree(state)
    found = tree.current_node()
    assert found is not None
    assert found.id == "node1"


def test_build_node_factory():
    node = ChoiceTree.build_node(
        prompt="What now?",
        options=[
            {
                "text": "Fight",
                "consequences": [
                    {"description": "You win", "severity": "major", "unlocks": ["victory"]},
                ],
            },
            {"text": "Flee"},
        ],
        scene_id="s2",
    )
    assert node.prompt == "What now?"
    assert len(node.options) == 2
    assert node.options[0].consequences[0].severity == ConsequenceSeverity.MAJOR


def test_consequence_locks():
    state = StoryState(flags={"path_a": True, "path_b": True})
    tree = ChoiceTree(state)
    c = Consequence(description="Locked", locks=["path_b"])
    tree._apply_consequence(c)
    assert state.flags["path_a"] is True
    assert state.flags["path_b"] is False


def test_consequence_affects_characters():
    from plottwist.models import CharacterData

    char = CharacterData(id="npc1", name="NPC")
    state = StoryState(characters={"npc1": char})
    tree = ChoiceTree(state)
    c = Consequence(description="NPC is upset", affects_characters=["npc1"])
    tree._apply_consequence(c)
    assert "NPC is upset" in char.notes.get("consequence_log", [])
