"""Built-in starter story templates for PLOTTWIST."""

from __future__ import annotations

from plottwist.models import (
    ArcPhase,
    CharacterData,
    CharacterGoal,
    CharacterRelationship,
    ChoiceNode,
    ChoiceOption,
    Consequence,
    ConsequenceSeverity,
    Genre,
    PersonalityTraits,
    SceneData,
    SceneType,
    SettingData,
    StoryTemplate,
    Tone,
)


# ---------------------------------------------------------------------------
# MYSTERY -- "The Last Guest"
# ---------------------------------------------------------------------------

_mystery_setting = SettingData(
    name="Ravenhollow Manor",
    description=(
        "A sprawling Victorian manor perched on sea cliffs, cut off from the "
        "mainland by a washed-out bridge.  Rain hammers the slate roof.  "
        "Inside, gas lamps flicker and portraits stare from panelled walls."
    ),
    atmosphere="Claustrophobic, rain-soaked, every shadow hides a secret",
    time_period="1920s England",
    locations=[
        "Grand foyer",
        "Library",
        "Conservatory",
        "Kitchen",
        "East wing bedrooms",
        "Wine cellar",
        "Rooftop terrace",
    ],
    rules=[
        "No one can leave until the bridge is repaired",
        "The telephone line is dead",
        "One of the guests is the murderer",
    ],
)

_mystery_characters = [
    CharacterData(
        id="host",
        name="Lord Alistair Blackwood",
        role="victim",
        backstory="Wealthy eccentric who invited five old acquaintances for a reunion weekend. Found dead in the library.",
        personality=PersonalityTraits(openness=80, conscientiousness=30, extraversion=70, agreeableness=20, neuroticism=60),
        goals=[CharacterGoal(description="Reveal a long-buried secret", priority=5)],
        arc_phase=ArcPhase.INTRODUCTION,
        alive=False,
        speech_style="Pompous, theatrical, fond of literary quotations",
        secrets=["Blackmailed every guest at some point in the past"],
    ),
    CharacterData(
        id="doctor",
        name="Dr. Evelyn Cross",
        role="suspect",
        backstory="Blackwood's personal physician.  Calm under pressure, but her medical bag is missing a scalpel.",
        personality=PersonalityTraits(openness=60, conscientiousness=90, extraversion=30, agreeableness=70, neuroticism=40),
        goals=[CharacterGoal(description="Keep her malpractice secret hidden", priority=4)],
        arc_phase=ArcPhase.INTRODUCTION,
        present_in_scene=True,
        speech_style="Precise, clinical, measured pauses",
        secrets=["Prescribed Blackwood an experimental drug that caused hallucinations"],
    ),
    CharacterData(
        id="colonel",
        name="Colonel Marcus Thorne",
        role="suspect",
        backstory="Retired military man with a stiff upper lip.  Owes Blackwood a large gambling debt.",
        personality=PersonalityTraits(openness=20, conscientiousness=80, extraversion=50, agreeableness=30, neuroticism=50),
        goals=[CharacterGoal(description="Destroy evidence of his debt", priority=4)],
        arc_phase=ArcPhase.INTRODUCTION,
        present_in_scene=True,
        speech_style="Clipped, military jargon, avoids emotion",
        secrets=["Knows the location of a hidden passage in the manor"],
    ),
    CharacterData(
        id="actress",
        name="Vivienne LaRoux",
        role="suspect",
        backstory="Fading stage actress and Blackwood's former lover.  Arrived wearing a fox-fur stole and a brittle smile.",
        personality=PersonalityTraits(openness=90, conscientiousness=30, extraversion=95, agreeableness=50, neuroticism=80),
        goals=[CharacterGoal(description="Reclaim love letters Blackwood kept", priority=3)],
        arc_phase=ArcPhase.INTRODUCTION,
        present_in_scene=True,
        speech_style="Dramatic, breathless, theatrical metaphors",
        secrets=["Was in the library minutes before the body was found"],
    ),
]

_mystery_opening = SceneData(
    id="scene_foyer",
    title="A Scream in the Night",
    description=(
        "A shriek tears through the manor.  You rush from your guest room to "
        "the grand foyer where the remaining guests have gathered, pale-faced.  "
        "Dr. Cross kneels beside the library door.  'He's dead,' she says flatly.  "
        "'Lord Blackwood is dead.'"
    ),
    setting_context="Grand foyer, midnight, storm raging outside",
    scene_type=SceneType.REVELATION,
    characters_present=["doctor", "colonel", "actress"],
    available_actions=["Examine the body", "Question a guest", "Search a room"],
    mood=Tone.SUSPENSEFUL,
)

_mystery_initial_choice = ChoiceNode(
    prompt="The clock strikes one.  The body lies cold in the library.  What is your first move?",
    options=[
        ChoiceOption(
            text="Examine the body and the crime scene in the library",
            consequences=[
                Consequence(
                    description="You discover a torn envelope clutched in Blackwood's hand",
                    severity=ConsequenceSeverity.MODERATE,
                    state_changes={"found_envelope": True},
                    unlocks=["clue_envelope"],
                ),
            ],
            leads_to=None,
        ),
        ChoiceOption(
            text="Confront Dr. Cross about her missing scalpel",
            consequences=[
                Consequence(
                    description="Dr. Cross becomes defensive and reveals she last saw the scalpel in the conservatory",
                    severity=ConsequenceSeverity.MINOR,
                    affects_characters=["doctor"],
                    state_changes={"questioned_doctor": True},
                    unlocks=["clue_scalpel_location"],
                ),
            ],
            leads_to=None,
        ),
        ChoiceOption(
            text="Follow Colonel Thorne, who is slipping away toward the east wing",
            consequences=[
                Consequence(
                    description="You catch the Colonel trying to open a hidden panel behind a portrait",
                    severity=ConsequenceSeverity.MAJOR,
                    affects_characters=["colonel"],
                    state_changes={"caught_colonel": True},
                    unlocks=["clue_hidden_passage"],
                ),
            ],
            leads_to=None,
        ),
    ],
)

MYSTERY_TEMPLATE = StoryTemplate(
    name="mystery",
    genre=Genre.MYSTERY,
    tone=Tone.SUSPENSEFUL,
    tagline="A locked-room murder at a remote manor. Interrogate suspects, find clues, unmask the killer.",
    setting=_mystery_setting,
    characters=_mystery_characters,
    opening_scene=_mystery_opening,
    initial_choice=_mystery_initial_choice,
    flags={"murder_solved": False, "suspects_remaining": 3},
)


# ---------------------------------------------------------------------------
# FANTASY -- "The Hollow Crown"
# ---------------------------------------------------------------------------

_fantasy_setting = SettingData(
    name="The Kingdom of Aldenmere",
    description=(
        "A once-great kingdom where the Heartwood -- an ancient tree at the "
        "centre of the capital -- is dying.  As its roots wither, magic fades "
        "from the land.  The king is bedridden and the court whispers of a "
        "prophecy: 'When the last leaf falls, a new sovereign shall rise -- or "
        "the realm shall crumble to dust.'"
    ),
    atmosphere="Autumnal decay, fading magic, uneasy hope",
    time_period="Medieval fantasy",
    locations=[
        "Thornhaven (capital city)",
        "The Heartwood grove",
        "Castle Aldenmere",
        "The Whispering Marshes",
        "Ironforge District",
        "The Oracle's Spire",
    ],
    rules=[
        "Magic is drawn from the Heartwood and is weakening",
        "The prophecy may be genuine or a political fabrication",
        "Three factions vie for the throne",
    ],
)

_fantasy_characters = [
    CharacterData(
        id="sage",
        name="Maren Ashveil",
        role="mentor",
        backstory="Keeper of the Heartwood and last true mage.  She believes the player is the one the prophecy speaks of -- but she may be wrong.",
        personality=PersonalityTraits(openness=95, conscientiousness=70, extraversion=30, agreeableness=60, neuroticism=50),
        goals=[CharacterGoal(description="Save the Heartwood at any cost", priority=5)],
        arc_phase=ArcPhase.RISING,
        present_in_scene=True,
        speech_style="Measured, poetic, speaks in metaphors drawn from nature",
        secrets=["Has been siphoning her own life force into the tree"],
    ),
    CharacterData(
        id="knight",
        name="Ser Dorian Hale",
        role="ally",
        backstory="Captain of the dying king's guard.  Loyal to a fault, haunted by a battlefield betrayal.",
        personality=PersonalityTraits(openness=30, conscientiousness=95, extraversion=50, agreeableness=70, neuroticism=60),
        goals=[CharacterGoal(description="Protect the rightful heir", priority=5)],
        arc_phase=ArcPhase.INTRODUCTION,
        present_in_scene=True,
        speech_style="Formal, chivalric, uncomfortable with deception",
        secrets=["Left a comrade to die during the Northern Campaign"],
    ),
    CharacterData(
        id="trickster",
        name="Pip Duskmantle",
        role="wildcard",
        backstory="Street urchin turned information broker.  Knows every secret passage in Thornhaven and sells loyalty to the highest bidder.",
        personality=PersonalityTraits(openness=80, conscientiousness=20, extraversion=85, agreeableness=40, neuroticism=30),
        goals=[CharacterGoal(description="Survive and profit from the coming chaos", priority=3)],
        arc_phase=ArcPhase.INTRODUCTION,
        present_in_scene=False,
        speech_style="Fast-talking, irreverent, cockney-inflected slang",
        secrets=["Actually the king's illegitimate child"],
    ),
]

_fantasy_opening = SceneData(
    id="scene_grove",
    title="The Last Leaf Trembles",
    description=(
        "You stand before the Heartwood.  Its trunk, wider than a castle tower, "
        "is streaked with grey rot.  A single golden leaf clings to the lowest "
        "branch, shivering in a wind that smells of ash.  Maren Ashveil presses "
        "a weathered hand to the bark and closes her eyes.  'It remembers you,' "
        "she whispers.  Beside her, Ser Dorian grips his sword hilt, scanning "
        "the treeline for enemies only he seems to expect."
    ),
    setting_context="The Heartwood grove at dawn, mist rising from dead roots",
    scene_type=SceneType.REVELATION,
    characters_present=["sage", "knight"],
    available_actions=["Touch the Heartwood", "Ask Maren about the prophecy", "Scout the perimeter with Dorian"],
    mood=Tone.EPIC,
)

_fantasy_initial_choice = ChoiceNode(
    prompt="The Heartwood pulses faintly, as if waiting.  Maren watches you with ancient eyes.  What do you do?",
    options=[
        ChoiceOption(
            text="Place your hand on the Heartwood and open your mind to it",
            consequences=[
                Consequence(
                    description="A vision floods your mind: three paths, three crowns, three prices.  The tree marks your palm with a glowing sigil.",
                    severity=ConsequenceSeverity.MAJOR,
                    state_changes={"heartwood_bond": True, "has_sigil": True},
                    unlocks=["path_of_the_heartwood"],
                ),
            ],
        ),
        ChoiceOption(
            text="Ask Maren to tell you the full prophecy -- all of it, including the parts she is hiding",
            consequences=[
                Consequence(
                    description="Maren hesitates, then reveals the prophecy has a second verse: 'The sovereign must feed the roots with what they love most.'",
                    severity=ConsequenceSeverity.MODERATE,
                    affects_characters=["sage"],
                    state_changes={"knows_full_prophecy": True},
                    unlocks=["prophecy_second_verse"],
                ),
            ],
        ),
        ChoiceOption(
            text="Tell them both you want nothing to do with prophecies and head for the city gates",
            consequences=[
                Consequence(
                    description="Ser Dorian blocks your path.  'The city gates are sealed.  By order of Regent Voss.'  You are trapped in Thornhaven.",
                    severity=ConsequenceSeverity.MODERATE,
                    affects_characters=["knight"],
                    state_changes={"rejected_prophecy": True, "knows_gates_sealed": True},
                ),
            ],
        ),
    ],
)

FANTASY_TEMPLATE = StoryTemplate(
    name="fantasy",
    genre=Genre.FANTASY,
    tone=Tone.EPIC,
    tagline="A dying kingdom, a reluctant hero, and a prophecy that may be a lie.",
    setting=_fantasy_setting,
    characters=_fantasy_characters,
    opening_scene=_fantasy_opening,
    initial_choice=_fantasy_initial_choice,
    flags={"heartwood_health": 3, "faction_alliance": "none"},
)


# ---------------------------------------------------------------------------
# SCI-FI -- "Signal Lost"
# ---------------------------------------------------------------------------

_scifi_setting = SettingData(
    name="GSV Meridian (Generation Ship)",
    description=(
        "The GSV Meridian has carried 12,000 souls through deep space for 200 "
        "years.  Now, 40 light-years from Earth and 60 from the target colony, "
        "the ship has received an alien signal -- and something has answered.  "
        "Hull sensors detect an object matching pace with the ship.  It is "
        "not human."
    ),
    atmosphere="Sterile corridors, humming reactors, the vast silence of space outside every viewport",
    time_period="2340 CE",
    locations=[
        "Command Bridge",
        "Habitation Ring Alpha",
        "Xenology Lab",
        "Reactor Core",
        "Observation Dome",
        "Cargo Bay 7 (sealed)",
    ],
    rules=[
        "FTL communication does not exist -- Earth cannot help",
        "The ship's AI (ORACLE) has final authority over life support",
        "The alien object has not responded to standard hails",
    ],
)

_scifi_characters = [
    CharacterData(
        id="captain",
        name="Captain Yara Osei",
        role="authority",
        backstory="Third-generation ship-born.  Rose through the ranks on competence, not politics.  Carries the weight of 12,000 lives.",
        personality=PersonalityTraits(openness=60, conscientiousness=90, extraversion=40, agreeableness=50, neuroticism=55),
        goals=[CharacterGoal(description="Ensure the safety of the colony mission", priority=5)],
        arc_phase=ArcPhase.RISING,
        present_in_scene=True,
        speech_style="Concise, authoritative, occasional dry humour under stress",
        secrets=["Knows ORACLE has been behaving erratically for months"],
    ),
    CharacterData(
        id="xenologist",
        name="Dr. Kenji Tanaka",
        role="specialist",
        backstory="Theoretical xenologist who never expected to use his degree.  Thrilled and terrified in equal measure.",
        personality=PersonalityTraits(openness=95, conscientiousness=60, extraversion=70, agreeableness=80, neuroticism=70),
        goals=[CharacterGoal(description="Make peaceful first contact", priority=5)],
        arc_phase=ArcPhase.INTRODUCTION,
        present_in_scene=True,
        speech_style="Enthusiastic, prone to tangents, peppers speech with scientific terms",
        secrets=["Has been receiving fragments of the alien signal in his dreams"],
    ),
    CharacterData(
        id="engineer",
        name="Chief Engineer Ayo Bankole",
        role="pragmatist",
        backstory="Keeps the Meridian alive with spit, wire, and stubbornness.  Trusts machines more than people.",
        personality=PersonalityTraits(openness=40, conscientiousness=85, extraversion=30, agreeableness=35, neuroticism=40),
        goals=[CharacterGoal(description="Protect the ship's systems from alien interference", priority=5)],
        arc_phase=ArcPhase.INTRODUCTION,
        present_in_scene=True,
        speech_style="Blunt, technical, speaks in problems-and-solutions",
        secrets=["Discovered that Cargo Bay 7 was sealed by ORACLE, not by crew"],
    ),
]

_scifi_opening = SceneData(
    id="scene_bridge",
    title="First Light",
    description=(
        "The bridge is silent except for the low thrum of the reactor.  On the "
        "main viewport, stars drift -- and among them, something new.  A shape "
        "that doesn't belong.  It pulses with a faint bioluminescence, matching "
        "the Meridian's speed precisely.  Captain Osei stands at the command "
        "rail, jaw tight.  Dr. Tanaka's hands tremble over his console.  "
        "Chief Bankole mutters, 'It's drawing power from our wake field.'"
    ),
    setting_context="Command Bridge, 0347 ship-time, red alert lighting",
    scene_type=SceneType.REVELATION,
    characters_present=["captain", "xenologist", "engineer"],
    available_actions=["Hail the object", "Run a deep scan", "Consult ORACLE", "Seal the outer hull"],
    mood=Tone.SUSPENSEFUL,
)

_scifi_initial_choice = ChoiceNode(
    prompt="The alien object drifts closer.  Captain Osei looks to you -- the ship's First Contact Officer.  'Your call.'",
    options=[
        ChoiceOption(
            text="Broadcast a mathematical greeting sequence on all frequencies",
            consequences=[
                Consequence(
                    description="The object responds: it mirrors your sequence, then adds a new pattern.  Dr. Tanaka gasps -- 'It's... counting primes.'",
                    severity=ConsequenceSeverity.MAJOR,
                    affects_characters=["xenologist"],
                    state_changes={"contact_initiated": True, "alien_response": "primes"},
                    unlocks=["diplomatic_channel"],
                ),
            ],
        ),
        ChoiceOption(
            text="Order Chief Bankole to run a full-spectrum scan before any communication",
            consequences=[
                Consequence(
                    description="The scan reveals the object is partially organic.  It also shows micro-tendrils extending toward the hull.  Bankole swears.",
                    severity=ConsequenceSeverity.MODERATE,
                    affects_characters=["engineer"],
                    state_changes={"scan_complete": True, "tendrils_detected": True},
                    unlocks=["hull_analysis"],
                ),
            ],
        ),
        ChoiceOption(
            text="Ask ORACLE for a threat assessment and recommended protocols",
            consequences=[
                Consequence(
                    description="ORACLE pauses for 4.7 seconds -- an eternity for an AI.  Then: 'Threat level: INDETERMINATE.  Recommendation: allow contact.'  The captain frowns.  That pause was not normal.",
                    severity=ConsequenceSeverity.MODERATE,
                    state_changes={"consulted_oracle": True, "oracle_suspicious": True},
                    unlocks=["oracle_investigation"],
                ),
            ],
        ),
    ],
)

SCIFI_TEMPLATE = StoryTemplate(
    name="scifi",
    genre=Genre.SCIFI,
    tone=Tone.SUSPENSEFUL,
    tagline="First contact goes wrong aboard a generation ship. Diplomacy or survival -- choose wisely.",
    setting=_scifi_setting,
    characters=_scifi_characters,
    opening_scene=_scifi_opening,
    initial_choice=_scifi_initial_choice,
    flags={"alien_hostility": 0, "oracle_trust": 5, "crew_morale": 7},
)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TEMPLATES: dict[str, StoryTemplate] = {
    "mystery": MYSTERY_TEMPLATE,
    "fantasy": FANTASY_TEMPLATE,
    "scifi": SCIFI_TEMPLATE,
}
