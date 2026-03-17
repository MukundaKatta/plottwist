# PLOTTWIST

**Interactive AI Fiction Platform** -- craft branching narratives powered by LLMs, where every choice reshapes the story.

PLOTTWIST combines structured storytelling (characters with arcs, world-building, consequence trees) with AI-generated prose to create deeply interactive fiction experiences.

## Features

- **Branching Narrative Engine** -- stories that diverge, converge, and remember every choice
- **Living Characters** -- NPCs with personality traits, goals, and evolving arcs that respond to player decisions
- **World Simulation** -- settings and scenes that change based on story state
- **AI-Powered Narration** -- LLM-generated prose that adapts tone, pacing, and detail to context
- **Character-Appropriate Dialogue** -- each character speaks with a distinct voice shaped by their personality
- **Consequence Tracking** -- choices ripple forward, unlocking or closing future paths
- **Rich Terminal UI** -- beautiful CLI experience with panels, tables, and styled text
- **Starter Templates** -- three built-in story templates (Mystery, Fantasy, Sci-Fi) to play immediately

## Installation

```bash
pip install -e .
```

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Quick Start

```bash
# List available story templates
plottwist templates

# Start a new story from a template
plottwist play --template mystery

# Resume a saved story
plottwist play --save mysave.json

# Generate a story report
plottwist report --save mysave.json
```

## Starter Templates

| Template | Genre | Description |
|----------|-------|-------------|
| `mystery` | Mystery | A locked-room murder at a remote manor. Interrogate suspects, find clues, unmask the killer. |
| `fantasy` | Fantasy | A dying kingdom, a reluctant hero, and a prophecy that may be a lie. |
| `scifi` | Sci-Fi | First contact goes wrong aboard a generation ship. Diplomacy or survival -- choose wisely. |

## Architecture

```
src/plottwist/
  story/
    engine.py      -- StoryEngine: branching narrative state machine
    characters.py  -- Character model with personality, goals, arc tracking
    world.py       -- Setting and Scene models for world state
    choices.py     -- ChoiceTree with consequence propagation
  generator/
    narrator.py    -- LLM-based narrative generation
    dialogue.py    -- Character-voice dialogue generation
  models.py        -- Pydantic data models
  cli.py           -- Click CLI interface
  report.py        -- Rich terminal reporting
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
