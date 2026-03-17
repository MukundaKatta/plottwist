"""Tests that all built-in templates are valid and can bootstrap an engine."""

from plottwist.models import Genre, Tone
from plottwist.story.engine import StoryEngine
from plottwist.templates import TEMPLATES


def test_all_templates_present():
    assert "mystery" in TEMPLATES
    assert "fantasy" in TEMPLATES
    assert "scifi" in TEMPLATES


def test_mystery_template():
    tmpl = TEMPLATES["mystery"]
    assert tmpl.genre == Genre.MYSTERY
    assert tmpl.tone == Tone.SUSPENSEFUL
    engine = StoryEngine.from_template(tmpl)
    assert engine.current_scene() is not None
    assert len(engine.available_choices()) == 3
    assert len(engine.all_characters()) == 4


def test_fantasy_template():
    tmpl = TEMPLATES["fantasy"]
    assert tmpl.genre == Genre.FANTASY
    engine = StoryEngine.from_template(tmpl)
    assert engine.current_scene() is not None
    assert len(engine.available_choices()) == 3


def test_scifi_template():
    tmpl = TEMPLATES["scifi"]
    assert tmpl.genre == Genre.SCIFI
    engine = StoryEngine.from_template(tmpl)
    assert engine.current_scene() is not None
    assert len(engine.available_choices()) == 3
    chars = engine.all_characters()
    names = {c.name for c in chars}
    assert "Captain Yara Osei" in names
    assert "Dr. Kenji Tanaka" in names


def test_template_engines_have_settings():
    for name, tmpl in TEMPLATES.items():
        engine = StoryEngine.from_template(tmpl)
        setting = engine.setting()
        assert setting is not None, f"Template {name!r} has no setting"
        assert setting.name, f"Template {name!r} setting has no name"


def test_template_initial_choices_have_consequences():
    for name, tmpl in TEMPLATES.items():
        for opt in tmpl.initial_choice.options:
            assert len(opt.consequences) > 0, (
                f"Template {name!r} option {opt.text!r} has no consequences"
            )
