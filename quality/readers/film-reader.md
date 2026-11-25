# The film reader (spec 163 FR-3)

The prompt the film reader is sent, once per entry's film, through the **Anthropic API with vision**
(`quality/readers.toml` `[film_reader]`, `claude-opus-5-5`, medium; `quality/film_reader.py`). One user message in three
parts, in this order: the text between the two `before-images` markers, then the images, then the text between the two
`after-images` markers. `quality/film_reader.py` fills every `{{name}}`:

- `{{persona}}` -- **the persona card**, the yardstick (FR-1): the entry's `context` (actor, actor_plural, job,
  circumstance, segment, the window, the market's country), its practitioner `roles` (label and about), today's way
  (`current_solution.today` where the entry carries it) and its **problem statement** whole (`statements.problem`: the
  limitations and the cost are inside it).
- `{{lines}}` -- the film's lines in order, one a scene (the served `build.story.scenes[]`), each with its chapter mark
  (`chapter`: who, task, today, shortfall, cost) as keel-web draws it (*Who*, *The task*, *Today*, *Where it falls
  short*, *What it costs them*; carried across the scenes of its chapter), `pain: true` on the pain scene, and the ask
  (the board's line, no picture) last.
- `{{setting}}` -- the build's `pictures.setting` (place, props, garments, time of day) as keel-cloud read it.
- `{{prompts}}` -- the build's `pictures.prompts[]` (the sheet's and each scene's, every attempt), cut to the scene part.
- The images -- each preceded by a one-line label: the fourteen frames (seven scenes, each on the phone 390 x 844 and
  the laptop 1280 x 800, as the founder's player held it, the caption settled), then the seven pictures as keel-cloud
  stored them (`GET /v2/assets/{id}`), then the character sheet where the build has one. Spec 167 FR-3: a frame's
  label names the viewport AND the layout keel-web 263 drew -- *the caption over the picture's lower third* (the
  phone; a laptop around a landscape film) or *the caption beside the picture* (the laptop's words' column beside a
  portrait stage) -- the stage's shape (tall or wide, its size), and a frame left out (`pictureMissing`: the picture
  before held still, or the plain ground).
- `{{rubric}}` -- `quality/FILM-RUBRIC.md` between its `film-problem` markers (or `film-solution` on a solution film):
  the one source of the criteria.
- `{{criteria}}` -- the criterion keys of the kind, for the answer's shape (`f1`..`f8` or `s1`..`s9`).

Nothing above the first marker is sent. A change to these words is a change to the reader: say why in the commit.

<!-- before-images:begin -->
## Who you are judging for -- read this before the film

You are reading the short film Keel made for a study. Strangers see this film before they are asked *Did this happen to
you?*: it must tell them, in drawn pictures and a few spoken lines shown as captions, who the person is, what they are
trying to get done, how they do it today, where that falls short and what it costs them. The founder typed (or said)
the problem below; Keel drew the film from it.

Judge the film from inside the person below, and from what you yourself know of that trade -- where such a person does
this task, what they wear, what is around them, when in the day it happens. The person's trade words are plain to them.

{{persona}}

## The film's lines, in order (each is spoken and shown as its scene's caption)

{{lines}}

## Where Keel was told to draw it (the setting it read for this person)

{{setting}}

## The drawing prompts Keel wrote (code's, from the board; for your reference only -- judge the pictures, not the prompts)

{{prompts}}

## The film -- the frames and the pictures follow
<!-- before-images:end -->

<!-- after-images:begin -->
## The rubric

{{rubric}}

## Your answer

Read the frames for what a stranger sees and reads (the caption on the picture or beside it, as each frame's label
says; the chapter mark; the ask), on the phone and on the laptop; read the pictures for what is drawn (and for any letter, digit, sign or logo inside a picture, which
is a fault). Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence. Every criterion
is scored (`{{criteria}}`); `instead` carries one line for each criterion scored under 2 and none for a 2:

{"scores": {"<criterion>": 0|1|2, ...}, "whys": {"<criterion>": "one sentence", ...},
 "missing": ["each limitation or box of the card the film does not show", ...],
 "instead": {"<criterion under 2>": "one line: what the film should have shown or said instead", ...}}
<!-- after-images:end -->

## The solution film (spec 166 FR-4)

The same reader on a solution film (`kind: solution`, `film/<entry>/solution/`): the text between the two
`solution-before-images` markers, then the images, then the text between the two `solution-after-images` markers.
`quality/film_reader.py` fills, besides `{{persona}}`, `{{rubric}}` (`FILM-RUBRIC.md` between its `film-solution`
markers) and `{{criteria}}` (`s1`..`s9`):

- `{{problem}}` -- **the problem's limitations and cost**, as the problem film's served story holds them (the
  yardstick of S4 and S6: each limitation must be shown solved or not; the joy is the cost's opposite).
- `{{board}}` -- **the founder's idea board** (`idea.json`, the served `IdeaView`): the brand and its tagline, the
  product, the setup (or none), the steps with who does each, the limitations with their marks, the advantage, what
  they get.
- `{{lines}}` -- the film's lines in order, each with its chapter mark (*Before*, *The task*, *What it solves*,
  *Better*, *What they get*), the marks on the limitations scene, the joy scene, a scene whose picture was dropped.
- `{{plate}}` -- the brand plate's words (the name and the tagline), shown alone before scene 1.
- `{{setting}}` and `{{plan}}` -- the build's setting and its frame plan (what each frame was to contain).
- `{{prompts}}` -- as on the problem film.
- `{{dropped}}` -- what was left out to keep the request under its ceiling (the laptop frames first), or nothing.
- The images -- the plate frame (phone, laptop), each scene's frames, the pictures, the character sheet (the problem
  film's own, reused: S1's same person).

<!-- solution-before-images:begin -->
## Who you are judging for -- read this before the film

You are reading the short film Keel made of a founder's solution. Strangers see it after the problem's film and
before they are asked whether it would fit how they work, whether it is better, and whether they could start without
trouble. It must show them the same person as the problem film, now doing the same task with the product: the setup
(only where the founder named one), the steps, each limitation of the problem solved (a tick) or not (a cross), what it
does better, and what the person gets back -- the opposite of the problem's cost. The brand (its colour, its mark) is
on the screen wherever the product appears. The founder said the solution; Keel drew the film from it.

Judge the film from inside the person below, and from what you yourself know of that trade.

{{persona}}

## The problem this solution answers (the problem film's own story)

{{problem}}

## The founder's idea board (what the film must show)

{{board}}

## The film's lines, in order (each is spoken and shown as its scene's caption)

{{lines}}

## The brand plate (shown alone before scene 1)

{{plate}}

## Where Keel was told to draw it, and the frame plan

{{setting}}

{{plan}}

## The drawing prompts Keel wrote (code's; for your reference only -- judge the pictures, not the prompts)

{{prompts}}

{{dropped}}

## The film -- the frames and the pictures follow
<!-- solution-before-images:end -->

<!-- solution-after-images:begin -->
## The rubric

{{rubric}}

## Your answer

Read the frames for what a stranger sees and reads (the plate; the caption on the picture or beside it, as each frame's
label says; the chapter mark; the ticks and crosses), on the phone and on the laptop; read the pictures for what is drawn (the same person as the
character sheet, the brand on the screen, and any letter, digit, sign or logo inside a picture, which is a fault).
Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence. Every criterion is scored
(`{{criteria}}`); `instead` carries one line for each criterion scored under 2 and none for a 2:

{"scores": {"<criterion>": 0|1|2, ...}, "whys": {"<criterion>": "one sentence", ...},
 "missing": ["each limitation with no mark, or box of the idea board the film does not show", ...],
 "instead": {"<criterion under 2>": "one line: what the film should have shown or said instead", ...}}
<!-- solution-after-images:end -->
