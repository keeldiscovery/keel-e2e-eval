# The film adviser (spec 163 FR-6)

The prompt `make film-advise` sends once per weak criterion of a film table (the weak rule of `quality/FILM-RUBRIC.md`),
through the `claude` CLI as `make quality-advise` (`quality/cycle.toml` `[film]` `adviser_model` / `adviser_effort`). It
proposes; it never applies. `quality/film_advise.py` fills every `{{name}}`: `{{criterion}}` the weak criterion with its
anchors, `{{failing}}` every entry's score, why and instead line on it (the entries named by their number alone, as
*entry 1, entry 2*: the adviser never sees an entry's name, so it cannot write a case), `{{current}}` the current text of
the three places a film rule lives in keel-cloud (`picture-setting.md`, `PicturePrompts`' fixed rules, `story-draft.md`),
read from the keel-cloud checkout at the bundle's sha where it has them. Nothing above the first marker is sent.

<!-- advise:begin -->
## Your task

Keel draws a short film for strangers from a founder's spoken problem: a setting read for the person's trade, a
character sheet, one picture a scene, one line a scene. A reader graded the films of several studies and one criterion
came out weak across them. Propose ONE change to ONE of the three places below that would lift it **for every study**:
a rule, never a case. Never name a trade, a company, a product, a title or a person; never write *if the person is a
...*; the persona-aware rule holds -- the person's own words and the model's own knowledge of a trade are handed in, a
rule never names one.

## The weak criterion

{{criterion}}

## How each film scored on it

{{failing}}

## The current text

{{current}}

## Your answer

Reply with ONE JSON object and nothing else:

{"where": "picture-setting.md" | "PicturePrompts" | "story-draft.md", "change": "the new text, whole, for the part you
change", "why": "three sentences at most", "rung": "words" | "effort" | "split"}
<!-- advise:end -->
