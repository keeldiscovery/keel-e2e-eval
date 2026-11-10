"""Spec 151 FR-4: rendering, two tracks on one timeline. Each script becomes `founder.wav` and `them.wav` (24 kHz mono
16-bit PCM, so the stacks cut turns with the standard library) and `turns.json`, the rendered turn boundaries (start,
end per turn) that are the truth's clocks.

The voices are `evals.noise.synth.tts` (gpt-4o-mini-tts): the founder's turns with an instruction for a person reading
from a card and digressing, the respondent's with the noise check's own. One voice pair by default (`VOICES=founder:them`
overrides). A turn starts at its script time or once the turn before has ended and its silence passed, whichever is
later; a turn that follows one talked over (`interrupted`) starts a beat before that turn ends. The respondent's track
may carry one of the noise check's beds at a signal-to-noise ratio (`SNRS=`, on at most a tenth of R3 by
`NOISE_SHARE`), mixed as `evals.noise.synth.do_mix` does (speech RMS over its active frames against the bed's).

**It spends money** (the voices, about $0.015 a minute) and needs numpy and soundfile (the noise synth's own); the
timeline is pure Python and unit-tested without either.
"""

from __future__ import annotations

import json
import os
import random
import wave
from pathlib import Path

SR = 24_000
DEFAULT_VOICES = ("onyx", "nova")
FOUNDER_TTS = ("You are a founder on a video call, reading a question from a card and then putting it in your own "
               "words. Speak at a natural conversational pace. Keep every preface, restart, filler and pause exactly as "
               "written.")
NOISE_BEDS = ("cafe", "traffic")
NOISE_SHARE_DEFAULT = 0.1
OVERLAP_S = 0.6
#: gpt-4o-mini-tts, about $0.015 a minute of speech (the methodology page's budget line).
TTS_USD_A_MINUTE = 0.015


def voices(raw: str | None = None) -> tuple[str, str]:
    raw = raw if raw is not None else os.environ.get("VOICES", "")
    if raw and ":" in raw:
        f, t = (x.strip() for x in raw.split(":", 1))
        if f and t:
            return f, t
    return DEFAULT_VOICES


def timeline(turns: list[dict], durations: list[float]) -> list[dict]:
    """The rendered clocks: `[{"turn", "who", "start", "end"}]`."""
    out, prev_end, prev_gap, prev_kind = [], None, 0.0, None
    for i, (turn, dur) in enumerate(zip(turns, durations)):
        start = float(turn["t"])
        if prev_end is not None:
            if prev_kind == "interrupted":
                start = max(out[-1]["start"], prev_end - min(OVERLAP_S, (prev_end - out[-1]["start"]) / 2))
            else:
                start = max(start, prev_end + prev_gap)
        end = start + float(dur)
        out.append({"turn": i, "who": turn["who"], "start": round(start, 3), "end": round(end, 3)})
        prev_end, prev_gap, prev_kind = end, float(turn.get("silence_after") or 0), turn.get("kind")
    return out


def noise_plan(scripts: list[dict], *, round_: int, snrs: str | None, share: float | None = None,
               seed: int = 151) -> dict:
    """Which scripts' respondent track carries a bed: `{script id: {"bed", "snr"}}` -- R3 only, at most `share` of
    them, the beds two of the noise check's."""
    if round_ != 3 or not snrs:
        return {}
    levels = [int(x) for x in str(snrs).split(",") if x.strip().lstrip("-").isdigit()]
    if not levels:
        return {}
    share = NOISE_SHARE_DEFAULT if share is None else min(float(share), NOISE_SHARE_DEFAULT)
    rng = random.Random(seed)
    picked = rng.sample([s["id"] for s in scripts], int(len(scripts) * share))
    return {sid: {"bed": NOISE_BEDS[i % len(NOISE_BEDS)], "snr": levels[i % len(levels)]}
            for i, sid in enumerate(sorted(picked))}


def _need_audio():
    try:
        import numpy as np                                                    # noqa: PLC0415
        import soundfile as sf                                                # noqa: PLC0415
    except ImportError as missing:
        raise SystemExit("copilot-bench refuses: LEVEL=audio renders with numpy and soundfile (the noise synth's own: "
                         ".venv/bin/pip install numpy scipy soundfile)") from missing
    return np, sf


def write_pcm16(path: Path, samples) -> None:
    """A float track as 16-bit PCM wav (stdlib `wave`, so the stacks read it without numpy)."""
    np, _sf = _need_audio()
    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype("<i2").tobytes()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm)


def render(script: dict, out_dir: Path, key: str, *, pair: tuple[str, str] | None = None, noise: dict | None = None,
           beds_root: Path | None = None, tts=None) -> dict:
    """One script to `out_dir/founder.wav`, `them.wav` and `turns.json`; returns `{"clocks", "tts_seconds"}`. Turns
    already said aloud (`turns/<i>.wav`) are never made again."""
    np, sf = _need_audio()
    from evals.noise import synth                                            # noqa: PLC0415

    out_dir = Path(out_dir)
    (out_dir / "turns").mkdir(parents=True, exist_ok=True)
    synth.KEY = key
    say = tts or synth.tts
    fv, tv = pair or voices()
    takes, durations = [], []
    for i, turn in enumerate(script["turns"]):
        path = out_dir / "turns" / f"{i:04d}-{turn['who']}.wav"
        if turn["who"] == "founder":
            say(turn["text"], fv, path, FOUNDER_TTS)
        else:
            say(turn["text"], tv, path, synth.TTS_INSTRUCTIONS)
        y, sr = sf.read(path, dtype="float32")
        if y.ndim > 1:
            y = y.mean(axis=1)
        takes.append(y)
        durations.append(len(y) / SR)
    clocks = timeline(script["turns"], durations)
    total = int((clocks[-1]["end"] + float(script["turns"][-1].get("silence_after") or 0) + 0.5) * SR)
    tracks = {"founder": np.zeros(total, np.float32), "them": np.zeros(total, np.float32)}
    for c, y in zip(clocks, takes):
        a = int(c["start"] * SR)
        tracks[c["who"]][a:a + len(y)] += y[:max(0, total - a)]
    if noise and beds_root is not None:
        bed, _ = sf.read(Path(beds_root) / "beds" / f"{noise['bed']}.wav", dtype="float32")
        reps = int(np.ceil(total / len(bed)))
        seg = np.tile(bed, reps)[:total]
        speech = tracks["them"]
        s_rms = synth.active_rms(speech) if np.any(speech) else 0.0
        n_rms = float(np.sqrt(np.mean(seg ** 2))) or 1.0
        g = s_rms / (n_rms * 10 ** (noise["snr"] / 20)) if s_rms else 0.0
        m = speech + g * seg
        peak = float(np.abs(m).max()) if len(m) else 0.0
        tracks["them"] = m / peak * 0.98 if peak > 0.98 else m
    write_pcm16(out_dir / "founder.wav", tracks["founder"])
    write_pcm16(out_dir / "them.wav", tracks["them"])
    (out_dir / "turns.json").write_text(json.dumps({"script": script["id"], "voices": [fv, tv], "noise": noise,
                                                    "clocks": clocks}, indent=1), encoding="utf-8")
    return {"clocks": clocks, "tts_seconds": round(sum(durations), 2)}


def load_clocks(out_dir: Path) -> list[dict] | None:
    path = Path(out_dir) / "turns.json"
    return json.loads(path.read_text(encoding="utf-8"))["clocks"] if path.is_file() else None
