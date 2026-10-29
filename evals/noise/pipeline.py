"""Spec 074 FR-3: the noise-capture check, Keel's answer path exactly as the product calls it -- the canon's
`pipeline.py` (keel-cloud `canon/designs/noise-capture-check-2026-10-26/`, the record of 2026-10-26) moved here as a
paid eval command, its alternatives (the direct audio model, RNNoise, spectral gating) left in the canon.

  STT -> classify : `POST /v1/audio/transcriptions`, model `gpt-transcribe`, `response_format=json`, `languages[]` the
                    language, one `keywords[]` per hint (the item's labels and its escape), prompt *A short spoken
                    answer to one survey question.* (keel-cloud `OpenAiTranscriber`); then `claude-haiku-4-5-20251001`,
                    temperature 0, **max_tokens 400** (keel-cloud spec 137), the system prompt the cloud checkout's own
                    `src/main/resources/keel/inference-instructions/classify-answer.md` (`stack.toml`'s `keel_cloud`),
                    the user lines as `KeelsAiClassifier.userPrompt` writes them. The story (FREE) is never classified:
                    the transcript is the answer.
  the read        : `norm_out` restates `Classification.validated()` -- **including keel-cloud 136 FR-1**: a pick-N item
                    reads the picks the model named, whatever it flags.

The keys come from the shell (`KEEL_OPENAI_API_KEY`, `KEEL_ANTHROPIC_API_KEY`) into the request headers alone -- never
logged, echoed or written. **It spends money** (about $2 and twenty minutes for the 1,260 samples): never in `make eval`,
`make unit`, the matrix or a schedule; `make noise-check` on the founder's word. Everything that scores is offline
(`norm_out`, `ok`, `score_story`, `evals.noise.report`), so the unit tests run on the canon's stored rows with no call.

  KEEL_OPENAI_API_KEY=... KEEL_ANTHROPIC_API_KEY=... python -m evals.noise.pipeline [--only <substr>] [--snrs 5,clean]
      [--limit N] [--workers 6] [--resume runs/<stamp>-noise-check]
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from evals.noise.dataset import BEDS, ITEMS, SNRS, UTTERANCES, voices_for

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = REPO_ROOT / "runs"
#: The kept set of 2026-10-26 (1,260 wav + m4a, the beds, the babble), outside every git checkout.
DEFAULT_SAMPLES = Path.home() / "Documents" / "projects" / "keel-noise-check-2026-10-26" / "audio"
SAMPLES_VAR = "KEEL_NOISE_SAMPLES"
OPENAI_KEY_VAR = "KEEL_OPENAI_API_KEY"
ANTHROPIC_KEY_VAR = "KEEL_ANTHROPIC_API_KEY"

#: keel-cloud `OpenAiTranscriber`.
TRANSCRIBE_URL = "https://api.openai.com/v1/audio/transcriptions"
TRANSCRIBE_MODEL = "gpt-transcribe"
TRANSCRIBE_PROMPT = "A short spoken answer to one survey question."
#: gpt-transcribe's list price, $0.0045 a minute.
TRANSCRIBE_USD_A_MINUTE = 0.0045
#: keel-cloud `KeelsAiClassifier`: the light tier's pin, temperature 0, the cap since spec 137.
MESSAGES_URL = "https://api.anthropic.com/v1/messages"
CLASSIFY_MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 400
TEMPERATURE = 0.0
#: Haiku 4.5's list prices, $ a million tokens in and out.
HAIKU_USD_IN, HAIKU_USD_OUT = 1.0, 5.0
#: The instruction, read from the cloud checkout `stack.toml` names.
INSTRUCTION = Path("src") / "main" / "resources" / "keel" / "inference-instructions" / "classify-answer.md"

UTT = {u[0]: u for u in UTTERANCES}


# ------------------------------------------------------------------------------------------------ the samples

def samples_root(env=None) -> Path:
    env = os.environ if env is None else env
    raw = (env.get(SAMPLES_VAR) or "").strip()
    return Path(raw).expanduser() if raw else DEFAULT_SAMPLES


def manifest() -> list[dict]:
    """The 1,260 samples in the canon's `samples.json` order and ids (synth.py's `do_mix`): for each answer and each of
    its two voices, the quiet take, then each bed at 20, 10, 5 and 0 dB. Paths are relative to the samples' root."""
    out = []
    for i, (uid, item, _said, _exp, _tag) in enumerate(UTTERANCES):
        for v in voices_for(i):
            out.append({"id": f"{uid}-{v}-clean", "utterance": uid, "item": item, "voice": v, "bed": "clean",
                        "snr": None, "wav": f"clean/{uid}-{v}.wav", "m4a": f"clean/{uid}-{v}.m4a"})
            for b in BEDS:
                for snr in SNRS:
                    out.append({"id": f"{uid}-{v}-{b}-{snr}", "utterance": uid, "item": item, "voice": v, "bed": b,
                                "snr": snr, "wav": f"mix/{uid}-{v}-{b}-{snr}.wav",
                                "m4a": f"mix/{uid}-{v}-{b}-{snr}.m4a"})
    return out


def select(samples: list[dict], *, only: str | None = None, snrs: str | None = None) -> list[dict]:
    """`--only <substr>` (an id substring) and `--snrs 20,5,clean` (`clean` the quiet room), as the canon's pipeline."""
    if only:
        samples = [s for s in samples if only in s["id"]]
    if snrs:
        want = {x.strip() for x in snrs.split(",") if x.strip()}
        samples = [s for s in samples if (("clean" in want) if s["snr"] is None else (str(s["snr"]) in want))]
    return samples


def missing(root: Path, samples: list[dict]) -> list[str]:
    return [s["m4a"] for s in samples if not (root / s["m4a"]).is_file()]


# ------------------------------------------------------------------------------------ the product's two calls

def hints(item: dict) -> list[str]:
    """`OpenAiTranscriber`'s `keywords[]`: the item's labels and its escape (the unit words only on amount-or-hours)."""
    return list(item["options"]) + ([item["escape"]] if item.get("escape") else [])


def transcribe(audio: Path, item: dict, key: str, *, lang: str = "en", mime: str = "audio/mp4") -> tuple:
    """The recording written down: `(text, ms, audio_seconds, status)`. Three tries on a 429, a 5xx or a broken
    connection, as the canon did."""
    import requests                                                           # noqa: PLC0415

    data = [("model", TRANSCRIBE_MODEL), ("response_format", "json"), ("languages[]", lang)]
    data += [("keywords[]", h) for h in hints(item)] + [("prompt", TRANSCRIBE_PROMPT)]
    started = time.time()
    response = None
    for _ in range(3):
        try:
            response = requests.post(TRANSCRIBE_URL, headers={"Authorization": "Bearer " + key}, data=data,
                                     files={"file": ("answer.mp4", audio.read_bytes(), mime)}, timeout=30)
        except requests.RequestException:
            time.sleep(1.0)
            continue
        if response.status_code == 429 or response.status_code >= 500:
            time.sleep(0.5)
            continue
        break
    ms = int((time.time() - started) * 1000)
    if response is None:
        return "", ms, 0.0, 0
    if response.status_code != 200:
        return "", ms, 0.0, response.status_code
    body = response.json()
    return (body.get("text") or "").strip(), ms, float((body.get("usage") or {}).get("seconds", 0) or 0), 200


def describe(item: dict) -> str:
    """`KeelsAiClassifier.describe`."""
    k = item["kind"]
    if k == "gate":
        return "yes or no"
    if k == "number":
        return f"a whole number from {item['range'][0]} to {item['range'][1]}"
    if k == "single":
        return "exactly one of the options"
    if k == "multi":
        return f"exactly {item['pick']} of the options" if item.get("pick") else "any number of the options"
    return "free"


def user_prompt(item: dict, heard: str) -> str:
    """`KeelsAiClassifier.userPrompt`: the kind, the numbered options, the escape, what they said."""
    lines = [f"Answer kind: {describe(item)}."]
    if item["options"]:
        lines.append("Options:")
        lines += [f"  {i + 1}. {o}" for i, o in enumerate(item["options"])]
    if item.get("escape"):
        lines.append(f'Escape option, only when they say they cannot answer: "{item["escape"]}"')
    lines.append(f'They said: "{(heard or "").strip()}"')
    return "\n".join(lines)


def instruction(keel_cloud: Path) -> str:
    path = Path(keel_cloud) / INSTRUCTION
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit(f"noise-check refuses: {path} is blank")
    return text


def classify(item: dict, heard: str, key: str, system: str) -> tuple:
    """One Messages call as `KeelsAiClassifier` makes it (one retry when the reply is not the JSON asked for):
    `(parsed or None, ms, (input, output), text, stop_reason)`."""
    import requests                                                           # noqa: PLC0415

    body = {"model": CLASSIFY_MODEL, "max_tokens": MAX_TOKENS, "temperature": TEMPERATURE, "system": system,
            "messages": [{"role": "user", "content": user_prompt(item, heard)}]}
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    started = time.time()
    out, text, usage, stop = None, "", (0, 0), None
    for _ in range(2):
        try:
            response = requests.post(MESSAGES_URL, headers=headers, json=body, timeout=30)
        except requests.RequestException:
            time.sleep(1.0)
            continue
        if response.status_code == 429 or response.status_code >= 500:
            time.sleep(1.0)
            continue
        if response.status_code != 200:
            text = f"HTTP {response.status_code}"
            break
        got = response.json()
        text = "".join(b.get("text", "") for b in got.get("content") or [] if b.get("type") == "text")
        u = got.get("usage") or {}
        usage = (usage[0] + int(u.get("input_tokens") or 0), usage[1] + int(u.get("output_tokens") or 0))
        stop = got.get("stop_reason")
        out = parse(text)
        if out is not None:
            break
    return out, int((time.time() - started) * 1000), usage, text, stop


def parse(text: str | None) -> dict | None:
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        j = json.loads(m.group())
    except ValueError:
        return None
    return j if isinstance(j, dict) else None


# ---------------------------------------------------------------------------------- the read: validated()

def _option(item: dict, raw) -> int | None:
    """`KeelsAiClassifier.option`: an option number (1-based; a number or its digits as text), else None."""
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)) and float(raw).is_integer():
        n = int(raw)
    elif isinstance(raw, str) and raw.strip().isdigit():
        n = int(raw.strip())
    else:
        return None
    return n if 1 <= n <= len(item["options"]) else None


def norm_out(item: dict, out, *, partial_pick: bool = True) -> dict:
    """What the page would be served, in the dataset's expected shapes (`{"picks": [n..]}` 1-based and sorted,
    `{"escape": True}`, `{"value": v}`, `{"unclear": True}`): keel-cloud `Classification.validated()` restated over the
    model's JSON, after `KeelsAiClassifier.parse` (a pick that is not one of the item's option numbers is dropped there).

    - `unclear` clears everything -- **except on a pick-N item whose picks name at least one of its labels** (keel-cloud
      136 FR-1, `partial_pick`; off restates the read before 136): the picks are read as below.
    - `escape` clears the picks and the value on an item that has an escape; on one with none (the gate) it is dropped.
    - gate, single, multi: none left is unclear; a single (or the gate) with two keeps the first; a pick-N with more
      than N keeps the first N; fewer is the partial read (the interviewer asks *And one more?*, keel-cloud 158).
    - number: no value is unclear; out of range is unclear.
    `_err` marks a reply that was not the JSON asked for (the product: *unclear*, reason *vendor*)."""
    if not isinstance(out, dict):
        return {"unclear": True, "_err": True}
    picks = []
    for raw in out.get("picks") or []:
        n = _option(item, raw)
        if n is not None and n not in picks:
            picks.append(n)
    kind = item["kind"]
    partial = partial_pick and kind == "multi" and int(item.get("pick") or 0) > 0 and bool(picks)
    if out.get("unclear") is True and not partial:
        return {"unclear": True}
    if kind == "free":
        return {"unclear": True}
    if out.get("escape") is True and item.get("escape"):
        return {"escape": True}
    if kind == "number":
        value = out.get("value")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return {"unclear": True}
        low, high = item["range"]
        if not (low <= value <= high):
            return {"unclear": True}
        return {"value": int(value) if float(value).is_integer() else value}
    if not picks:
        return {"unclear": True}
    if kind in ("gate", "single") and len(picks) > 1:
        picks = picks[:1]
    if kind == "multi" and int(item.get("pick") or 0) > 0 and len(picks) > int(item["pick"]):
        picks = picks[:int(item["pick"])]
    return {"picks": sorted(picks)}


def ok(expected: dict, got: dict) -> bool:
    if "any" in expected:
        return any(ok(e, got) for e in expected["any"])
    g = {k: v for k, v in got.items() if not k.startswith("_")}
    if "value" in expected:
        return g.get("value") == expected["value"]
    return g == expected


# ------------------------------------------------------------------------------------------- the story

ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
        "seventeen eighteen nineteen").split()
TENS = "zero ten twenty thirty forty fifty sixty seventy eighty ninety".split()


def words(n: int) -> str:
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000:
        return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + words(n % 100))
    return str(n)


def norm_text(s: str | None) -> str:
    """The canon's: lower case, currency and digits as words, hyphens as spaces, fillers dropped."""
    s = (s or "").lower().replace("’", "'")
    s = re.sub(r"\$\s?(\d[\d,]*)", r"\1 dollars", s)
    s = re.sub(r"€\s?(\d[\d,]*)", r"\1 euros", s)
    s = re.sub(r"(\d[\d,]*)\s?€", r"\1 euros", s)
    s = s.replace(",", "").replace("-", " ")
    s = re.sub(r"\d+", lambda m: words(int(m.group())), s)
    s = re.sub(r"[^a-z' ]", " ", s)
    s = re.sub(r"\b(um|uh|hmm|mm|er|ah)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def wer(ref: str, hyp: str) -> float:
    """Word error rate, a word-level edit distance over the reference's length (the canon's `jiwer.wer`)."""
    r, h = ref.split(), hyp.split()
    if not r:
        return 1.0 if h else 0.0
    prev = list(range(len(h) + 1))
    for i, rw in enumerate(r, 1):
        cur = [i] + [0] * len(h)
        for j, hw in enumerate(h, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (rw != hw))
        prev = cur
    return prev[-1] / len(r)


def score_story(expected: dict, hyp: str) -> dict:
    """A story keeps its meaning when every critical token (negations, numbers, who did it) is in the transcript."""
    ref, h = norm_text(expected["text"]), norm_text(hyp)
    crit = list(expected["critical"])
    kept = [norm_text(c) in h for c in crit]
    return {"wer": round(wer(ref, h), 3), "critical": crit, "critical_kept": kept, "meaning_kept": all(kept),
            "ref": ref, "hyp": h}


def rescore(row: dict, *, partial_pick: bool = True) -> dict:
    """A stored row read again offline: a closed answer's `got` from its `raw` through `norm_out`, then `ok`, `definite`
    and `false_support`; a story's from its transcript. No call."""
    _uid, item_key, _said, expected, _tag = UTT[row["utterance"]]
    item = ITEMS[item_key]
    out = dict(row)
    if item["kind"] == "free":
        out.update(score_story(expected, row.get("heard") or ""))
        out["ok"] = out["meaning_kept"]
        return out
    raw = row.get("raw")
    if not (row.get("heard") or "").strip():
        raw = {"unclear": True, "reason": "silence"}
    got = norm_out(item, raw, partial_pick=partial_pick)
    out.update(got=got, ok=ok(expected, got))
    out["definite"] = not (got.get("unclear") or got.get("escape"))
    out["false_support"] = bool(out["definite"] and not out["ok"])
    return out


# --------------------------------------------------------------------------------------------- the run

def one(sample: dict, root: Path, keys: dict, system: str) -> dict:
    uid, item_key, _said, expected, tag = UTT[sample["utterance"]]
    item = ITEMS[item_key]
    row = {"id": sample["id"], "utterance": uid, "item": item_key, "control": item["control"], "tag": tag,
           "voice": sample["voice"], "bed": sample["bed"], "snr": sample["snr"], "pipeline": "stt", "suppress": "none",
           "expected": expected}
    heard, t_ms, secs, status = transcribe(root / sample["m4a"], item, keys["openai"])
    row.update(heard=heard, transcribe_ms=t_ms, audio_seconds=secs, transcribe_status=status,
               cost_usd=round(secs * TRANSCRIBE_USD_A_MINUTE / 60, 6))
    if item["kind"] == "free":
        row.update(score_story(expected, heard))
        row.update(ok=row["meaning_kept"], classify_ms=0)
    else:
        if heard:
            out, c_ms, (ti, to), raw_text, stop = classify(item, heard, keys["anthropic"], system)
        else:
            out, c_ms, (ti, to), raw_text, stop = {"unclear": True, "reason": "silence"}, 0, (0, 0), "", None
        got = norm_out(item, out)
        row.update(raw=out, got=got, classify_ms=c_ms, ok=ok(expected, got), stop_reason=stop,
                   cut=stop == "max_tokens" and out is None,
                   cost_usd=round(row["cost_usd"] + (ti * HAIKU_USD_IN + to * HAIKU_USD_OUT) / 1e6, 6))
        if out is None:
            row["raw_text"] = raw_text[:300]
        row["definite"] = not (got.get("unclear") or got.get("escape"))
        row["false_support"] = bool(row["definite"] and not row["ok"])
        row["confidence"] = out.get("confidence") if isinstance(out, dict) else None
    row["latency_ms"] = row.get("transcribe_ms", 0) + row.get("classify_ms", 0)
    return row


def keys_from(env=None) -> dict:
    """The two keys from the shell, or a refusal that names the variable -- never the value."""
    env = os.environ if env is None else env
    keys = {"openai": (env.get(OPENAI_KEY_VAR) or "").strip(), "anthropic": (env.get(ANTHROPIC_KEY_VAR) or "").strip()}
    absent = [name for name, value in ((OPENAI_KEY_VAR, keys["openai"]), (ANTHROPIC_KEY_VAR, keys["anthropic"]))
              if not value]
    if absent:
        raise SystemExit("noise-check refuses: " + " and ".join(absent) + " not set in this shell -- the check calls "
                         "OpenAI's gpt-transcribe and Anthropic's Haiku as the product does (about $2); the keys are "
                         "read into the request headers alone, never logged, echoed or written")
    return keys


def run(argv: list[str] | None = None) -> int:
    from evals.noise import report                                           # noqa: PLC0415
    from stack.config import load_config                                     # noqa: PLC0415

    ap = argparse.ArgumentParser(prog="make noise-check", description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", default=None, help="an id substring (e.g. c5-, cafe-5)")
    ap.add_argument("--snrs", default=None, help="comma list of 20,10,5,0 and/or clean")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--resume", default=None, help="a runs/<stamp>-noise-check folder to finish")
    a = ap.parse_args(argv)
    keys = keys_from()
    keel_cloud = load_config(validate=False).keel_cloud
    system = instruction(keel_cloud)
    root = samples_root()
    samples = select(manifest(), only=a.only, snrs=a.snrs)
    absent = missing(root, samples)
    if absent:
        from evals.noise import synth                                        # noqa: PLC0415
        print(f"noise-check: {len(absent)} of {len(samples)} samples absent under {root}; synthesizing them there",
              flush=True)
        synth.synthesize(root, keys["openai"])
        absent = missing(root, samples)
        if absent:
            raise SystemExit(f"noise-check refuses: still absent after synthesis: {absent[:5]}")
    out_dir = Path(a.resume) if a.resume else RUNS_DIR / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-noise-check")
    out_dir.mkdir(parents=True, exist_ok=True)
    results = out_dir / report.RESULTS
    done = set()
    if results.exists():
        done = {json.loads(line)["id"] for line in results.read_text(encoding="utf-8").splitlines() if line.strip()}
    todo = [s for s in samples if s["id"] not in done]
    if a.limit:
        todo = todo[:a.limit]
    (out_dir / "run.json").write_text(json.dumps({
        "spec": "074", "started": datetime.now(timezone.utc).isoformat(), "samples": str(root),
        "selection": {"only": a.only, "snrs": a.snrs, "limit": a.limit}, "n": len(samples),
        "transcribe": {"model": TRANSCRIBE_MODEL, "prompt": TRANSCRIBE_PROMPT},
        "classify": {"model": CLASSIFY_MODEL, "max_tokens": MAX_TOKENS, "temperature": TEMPERATURE,
                     "instruction": str(Path(keel_cloud) / INSTRUCTION), "keel_cloud": report.git_sha(keel_cloud)},
    }, indent=1), encoding="utf-8")
    print(f"noise-check: {len(done)} done, {len(todo)} to run -> {out_dir}", flush=True)
    lock = threading.Lock()
    n = n_ok = 0
    with cf.ThreadPoolExecutor(a.workers) as ex, results.open("a", encoding="utf-8") as f:
        for row in ex.map(lambda s: one(s, root, keys, system), todo):
            with lock:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                f.flush()
                n += 1
                n_ok += bool(row.get("ok"))
                if n % 50 == 0 or n == len(todo):
                    print(f"  {n}/{len(todo)} ok={n_ok}", flush=True)
    cert = report.write(out_dir, root=root, selection={"only": a.only, "snrs": a.snrs, "limit": a.limit})
    print(cert["line"])
    return 0 if cert["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(run())
