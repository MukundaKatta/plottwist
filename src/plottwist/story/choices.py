"""Choice tree -- branching decisions with consequence propagation."""

from __future__ import annotations

from typing import Any

from plottwist.models import (
    ChoiceNode,
    ChoiceOption,
    Consequence,
    ConsequenceSeverity,
    StoryState,
)


class ChoiceTree:
    """Manages the directed graph of choices within a story.

    Each node holds a prompt shown to the player plus several options.
    When the player picks an option its consequences are applied to the
    StoryState and the tree advances to the next node.
    """

    def __init__(self, state: StoryState) -> None:
        self.state = state

    # -- node CRUD -------------------------------------------------------------

    def add_node(self, node: ChoiceNode) -> None:
        self.state.choice_nodes[node.id] = node

    def get_node(self, node_id: str) -> ChoiceNode | None:
        return self.state.choice_nodes.get(node_id)

    def current_node(self) -> ChoiceNode | None:
        """Return the choice node attached to the current scene, if any."""
        for node in self.state.choice_nodes.values():
            if node.scene_id == self.state.current_scene_id:
                return node
        return None

    # -- filtering visible options ---------------------------------------------

    def visible_options(self, node: ChoiceNode) -> list[ChoiceOption]:
        """Return only options whose requirements are satisfied."""
        result: list[ChoiceOption] = []
        for opt in node.options:
            if opt.hidden:
                continue
            if opt.requires and not all(
                self.state.flags.get(req) for req in opt.requires
            ):
                continue
            result.append(opt)
        return result

    # -- selecting an option ---------------------------------------------------

    def select_option(self, node: ChoiceNode, option_id: str) -> list[Consequence]:
        """Select an option by id, apply its consequences, return them."""
        option: ChoiceOption | None = None
        for opt in node.options:
            if opt.id == option_id:
                option = opt
                break
        if option is None:
            raise ValueError(f"Option {option_id!r} not found in node {node.id!r}")

        applied: list[Consequence] = []
        for consequence in option.consequences:
            self._apply_consequence(consequence)
            applied.append(consequence)

        # Advance to linked node / scene if specified
        if option.leads_to and option.leads_to in self.state.scenes:
            self.state.current_scene_id = option.leads_to

        return applied

    # -- consequence application -----------------------------------------------

    def _apply_consequence(self, consequence: Consequence) -> None:
        """Mutate story state according to a single consequence."""
        # Apply state_changes as flag updates
        for key, value in consequence.state_changes.items():
            self.state.flags[key] = value

        # Unlock / lock flags
        for flag in consequence.unlocks:
            self.state.flags[flag] = True
        for flag in consequence.locks:
            self.state.flags[flag] = False

        # Character effects (mark affected characters in notes)
        for char_id in consequence.affects_characters:
            char = self.state.characters.get(char_id)
            if char:
                events: list[str] = char.notes.get("consequence_log", [])
                events.append(consequence.description)
                char.notes["consequence_log"] = events

    # -- building choices dynamically ------------------------------------------

    @staticmethod
    def build_node(
        prompt: str,
        options: list[dict[str, Any]],
        scene_id: str | None = None,
        parent_id: str | None = None,
    ) -> ChoiceNode:
        """Convenience factory to create a ChoiceNode from plain dicts.

        Each dict in *options* should have at least ``text``; it may also
        include ``requires``, ``leads_to``, ``consequences`` (list of dicts),
        and ``hidden``.
        """
        parsed_options: list[ChoiceOption] = []
        for raw in options:
            consequences = []
            for c in raw.get("consequences", []):
                consequences.append(
                    Consequence(
                        description=c.get("description", ""),
                        severity=ConsequenceSeverity(c.get("severity", "minor")),
                        affects_characters=c.get("affects_characters", []),
                        state_changes=c.get("state_changes", {}),
                        unlocks=c.get("unlocks", []),
                        locks=c.get("locks", []),
                    )
                )
            parsed_options.append(
                ChoiceOption(
                    text=raw["text"],
                    requires=raw.get("requires", []),
                    leads_to=raw.get("leads_to"),
                    consequences=consequences,
                    hidden=raw.get("hidden", False),
                )
            )
        return ChoiceNode(
            prompt=prompt,
            options=parsed_options,
            scene_id=scene_id,
            parent_id=parent_id,
        )

    # -- summary ---------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        return {
            "total_nodes": len(self.state.choice_nodes),
            "flags": dict(self.state.flags),
        }
