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
  stored them (`GET /v2/assets/{id}`), then the character sheet where the build has one.
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

## The film's lines, in order (each is spoken and shown as the caption over its scene)

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

Read the frames for what a stranger sees and reads (the caption on the picture, the chapter mark, the ask), on the phone
and on the laptop; read the pictures for what is drawn (and for any letter, digit, sign or logo inside a picture, which
is a fault). Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence. Every criterion
is scored (`{{criteria}}`); `instead` carries one line for each criterion scored under 2 and none for a 2:

{"scores": {"<criterion>": 0|1|2, ...}, "whys": {"<criterion>": "one sentence", ...},
 "missing": ["each limitation or box of the card the film does not show", ...],
 "instead": {"<criterion under 2>": "one line: what the film should have shown or said instead", ...}}
<!-- after-images:end -->
