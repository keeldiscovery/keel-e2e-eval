"""Spec 074 FR-3: make the recordings when the kept set is absent -- the canon's `synth.py` (keel-cloud
`canon/designs/noise-capture-check-2026-10-26/`) moved here: the thirty answers said aloud by two voices each (OpenAI
gpt-4o-mini-tts), five synthesized noise beds, every answer mixed into every bed at 20 / 10 / 5 / 0 dB signal-to-noise
(speech RMS over its active frames against the bed's RMS), each sample kept as 24 kHz wav and as AAC in an mp4 container
(macOS `afconvert`), which is what an iPhone's MediaRecorder hands Keel.

Written under the samples' root (`KEEL_NOISE_SAMPLES`, default `~/Documents/projects/keel-noise-check-2026-10-26/audio`,
the kept set of 2026-10-26): `clean/`, `beds/`, `mix/`, `babble/` -- what is already there is never made again.
**It spends money** (the voices) and needs numpy, scipy and soundfile, which this repository does not install
(`.venv/bin/pip install numpy scipy soundfile`); `make noise-check` calls it only for samples that are absent. Two
changes from the canon: the TTS call is a plain HTTPS request with the key from `KEEL_OPENAI_API_KEY` (no SDK), and a
bed's random seed is a stable hash of its name (the canon's `hash()` changed every process).

  KEEL_OPENAI_API_KEY=... python -m evals.noise.synth [tts | beds | mix | all]
"""
import os, subprocess, sys, zlib
from pathlib import Path

try:
    import numpy as np, soundfile as sf
    from scipy import signal
except ImportError:  # the check's own heavy deps: needed to synthesize only
    np = sf = signal = None

from evals.noise.dataset import UTTERANCES, BABBLE, BABBLE_VOICES, BEDS, SNRS, voices_for

AUDIO = CLEAN = BEDDIR = MIX = BAB = None      # set by `use(root)`
KEY = None


def use(root, key=None):
    """Point the module at a samples' root (and the key), making its four folders."""
    global AUDIO, CLEAN, BEDDIR, MIX, BAB, KEY
    AUDIO = Path(root); CLEAN = AUDIO / "clean"; BEDDIR = AUDIO / "beds"; MIX = AUDIO / "mix"; BAB = AUDIO / "babble"
    for d in (CLEAN, BEDDIR, MIX, BAB): d.mkdir(parents=True, exist_ok=True)
    if key is not None: KEY = key
SR = 24000
BED_SECONDS = 24
PAD = 0.5          # the recording window opens a little before and closes a little after the words

TTS_INSTRUCTIONS = ("You are an ordinary person answering a survey question on your phone, speaking naturally at a "
                    "normal everyday pace. Keep every hesitation, pause and filler exactly as written.")

def tts(text, voice, path, instructions=TTS_INSTRUCTIONS):
    if path.exists(): return
    import requests
    r = requests.post("https://api.openai.com/v1/audio/speech", headers={"Authorization": "Bearer " + KEY},
                      json={"model": "gpt-4o-mini-tts", "voice": voice, "input": text, "instructions": instructions,
                            "response_format": "wav"}, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)
    y, sr = sf.read(path, dtype="float32")
    if y.ndim > 1: y = y.mean(axis=1)
    if sr != SR: y = signal.resample_poly(y, SR, sr).astype(np.float32)
    sf.write(path, y, SR)

def do_tts():
    for i, (uid, item, said, exp, tag) in enumerate(UTTERANCES):
        for v in voices_for(i):
            tts(said, v, CLEAN / f"{uid}-{v}.wav"); print("tts", uid, v, flush=True)
    for j, line in enumerate(BABBLE):
        tts(line, BABBLE_VOICES[j], BAB / f"b{j}.wav",
            "Two friends chatting in a busy cafe, relaxed, a little animated."); print("babble", j, flush=True)

# ----------------------------------------------------------------------------------------------- the beds
def butter(y, kind, cut, order=4):
    sos = signal.butter(order, cut, btype=kind, fs=SR, output="sos"); return signal.sosfilt(sos, y)

def pink(n, rng):
    w = rng.standard_normal(n); f = np.fft.rfft(w); k = np.arange(len(f)); k[0] = 1
    return np.fft.irfft(f / np.sqrt(k), n).astype(np.float32)

def env_hann(n): return np.hanning(n).astype(np.float32)

def bed_construction(n, rng):
    t = np.arange(n) / SR
    floor = 0.15 * pink(n, rng)
    out = floor.copy()
    pos = 0.0
    while pos < n / SR:                                     # hammer blows, irregular
        i = int(pos * SR); L = int(0.07 * SR)
        if i + L < n:
            out[i:i+L] += 1.6 * butter(rng.standard_normal(L), "band", [900, 4500]) * np.exp(-np.linspace(0, 7, L))
        pos += rng.uniform(0.45, 1.4)
    pos = rng.uniform(0, 2)
    while pos < n / SR:                                     # a drill in bursts
        i = int(pos * SR); L = int(rng.uniform(1.5, 3.5) * SR)
        if i + L > n: L = n - i
        tt = t[:L]; saw = signal.sawtooth(2 * np.pi * 118 * tt) * (0.7 + 0.3 * np.sin(2 * np.pi * 31 * tt))
        out[i:i+L] += 0.5 * butter(saw, "band", [400, 6000]) * env_hann(L) ** 0.3
        pos += L / SR + rng.uniform(1.0, 3.0)
    return out

def bed_traffic(n, rng):
    brown = np.cumsum(rng.standard_normal(n)); brown -= np.linspace(brown[0], brown[-1], n)
    brown = butter(brown, "high", 25); brown /= np.abs(brown).max() + 1e-9
    out = 0.6 * butter(brown, "low", 900)
    pos = rng.uniform(0, 1.5)
    while pos < n / SR:                                     # a car passing
        i = int(pos * SR); L = int(rng.uniform(1.6, 2.8) * SR)
        if i + L > n: L = n - i
        out[i:i+L] += 0.5 * butter(rng.standard_normal(L), "band", [150, 2500]) * env_hann(L) ** 1.5
        pos += rng.uniform(1.2, 3.0)
    for _ in range(2):                                      # a horn
        i = int(rng.uniform(1, BED_SECONDS - 2) * SR); L = int(0.7 * SR); tt = np.arange(L) / SR
        out[i:i+L] += 0.35 * (np.sign(np.sin(2 * np.pi * 415 * tt)) + np.sign(np.sin(2 * np.pi * 520 * tt))) * env_hann(L) ** 0.4
    return out.astype(np.float32)

def bed_cafe(n, rng):
    out = 0.12 * pink(n, rng)
    lines = []
    for p in sorted(BAB.glob("b*.wav")):
        y, _ = sf.read(p, dtype="float32"); lines.append(y)
    assert lines, "run tts first (the babble lines)"
    for k in range(14):                                     # other people talking, three or four at once
        y = lines[k % len(lines)]; i = int(rng.uniform(0, max(0.1, BED_SECONDS - len(y) / SR)) * SR)
        y = butter(y, "low", 3800) * rng.uniform(0.35, 0.7)
        L = min(len(y), n - i); out[i:i+L] += y[:L]
    pos = 0.3
    while pos < n / SR:                                     # cups and cutlery
        i = int(pos * SR); L = int(0.05 * SR)
        if i + L < n: out[i:i+L] += 0.8 * butter(rng.standard_normal(L), "high", 2500) * np.exp(-np.linspace(0, 9, L))
        pos += rng.uniform(0.6, 2.5)
    i = int(rng.uniform(2, BED_SECONDS - 4) * SR); L = int(2.2 * SR)  # the steam wand
    out[i:i+L] += 0.5 * butter(rng.standard_normal(L), "band", [1800, 7000]) * env_hann(L) ** 0.5
    return out.astype(np.float32)

def bed_music(n, rng):
    t = np.arange(n) / SR; out = np.zeros(n, np.float32)
    chords = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
    bar = 2.4
    for b in range(int(BED_SECONDS / bar) + 1):
        i = int(b * bar * SR); L = min(int(bar * SR), n - i)
        if L <= 0: break
        tt = t[:L]; pad = np.zeros(L)
        for f in chords[b % 4]:
            for h, a in ((1, 1), (2, 0.4), (3, 0.2)): pad += a * np.sin(2 * np.pi * f * h * tt)
        env = np.minimum(1, tt / 0.3) * np.minimum(1, (bar - tt) / 0.2)
        out[i:i+L] += 0.12 * pad * env
        bass = np.sin(2 * np.pi * chords[b % 4][0] / 2 * tt); out[i:i+L] += 0.2 * bass * env
    beat = 60 / 100
    k = 0.0
    while k < BED_SECONDS:
        i = int(k * SR); L = int(0.25 * SR)
        if i + L < n:
            tt = np.arange(L) / SR
            out[i:i+L] += 0.6 * np.sin(2 * np.pi * (55 + 40 * np.exp(-tt * 40)) * tt) * np.exp(-tt * 12)
        for h in (0, 0.5):
            j = int((k + h * beat) * SR); M = int(0.06 * SR)
            if j + M < n: out[j:j+M] += 0.25 * butter(rng.standard_normal(M), "high", 6000) * np.exp(-np.linspace(0, 8, M))
        k += beat
    return out

def bed_wind(n, rng):
    w = rng.standard_normal(n).astype(np.float32)
    slow = butter(rng.standard_normal(n), "low", 0.4); slow = (slow - slow.min()) / (np.ptp(slow) + 1e-9)
    cut = 200 + 800 * slow
    out = np.zeros(n, np.float32); step = int(0.05 * SR); zi = None
    for i in range(0, n, step):                             # a low-pass that wanders with the gusts
        sos = signal.butter(2, float(cut[i]), btype="low", fs=SR, output="sos")
        if zi is None: zi = signal.sosfilt_zi(sos) * 0
        seg, zi = signal.sosfilt(sos, w[i:i+step], zi=zi); out[i:i+step] = seg
    gust = 0.35 + 0.65 * slow
    rumble = 0.3 * butter(rng.standard_normal(n), "low", 60)
    return (out / (np.abs(out).max() + 1e-9) * gust + rumble).astype(np.float32)

MAKERS = {"construction": bed_construction, "traffic": bed_traffic, "cafe": bed_cafe, "music": bed_music, "wind": bed_wind}

def do_beds():
    for name in BEDS:
        if (BEDDIR / f"{name}.wav").exists(): continue
        rng = np.random.default_rng(zlib.crc32(name.encode()))
        y = MAKERS[name](BED_SECONDS * SR, rng)
        y = y / (np.abs(y).max() + 1e-9) * 0.9
        sf.write(BEDDIR / f"{name}.wav", y.astype(np.float32), SR); print("bed", name, flush=True)

# ----------------------------------------------------------------------------------------------- the mix
def active_rms(y):
    frame = int(0.03 * SR); frames = [y[i:i+frame] for i in range(0, len(y) - frame, frame)]
    rms = np.array([np.sqrt(np.mean(f ** 2)) for f in frames]); peak = rms.max()
    on = rms[rms > peak * 0.1]
    return float(np.sqrt(np.mean(on ** 2)))

def encode_m4a(wav, m4a):
    if not m4a.exists():
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "64000", str(wav), str(m4a)], check=True, capture_output=True)

def do_mix():
    rng = np.random.default_rng(2026)
    beds = {b: sf.read(BEDDIR / f"{b}.wav", dtype="float32")[0] for b in BEDS}
    manifest = []     # the canon wrote samples.json; here the manifest is `evals.noise.pipeline.manifest()`
    for i, (uid, item, said, exp, tag) in enumerate(UTTERANCES):
        for v in voices_for(i):
            base = CLEAN / f"{uid}-{v}"
            if base.with_suffix(".m4a").exists() and all((MIX / f"{uid}-{v}-{b}-{snr}.m4a").exists()
                                                         for b in BEDS for snr in SNRS):
                for b in BEDS: rng.uniform()     # made already: never padded or mixed twice (the draws kept in step)
                continue
            y, _ = sf.read(CLEAN / f"{uid}-{v}.wav", dtype="float32")
            if not base.with_suffix(".m4a").exists():      # the take is padded once, when it is first mixed
                pad = np.zeros(int(PAD * SR), np.float32); y = np.concatenate([pad, y, pad])
                sf.write(base.with_suffix(".wav"), y, SR); encode_m4a(base.with_suffix(".wav"), base.with_suffix(".m4a"))
            s_rms = active_rms(y)
            manifest.append({"id": f"{uid}-{v}-clean", "utterance": uid, "item": item, "voice": v, "bed": "clean", "snr": None,
                             "wav": str(base.with_suffix(".wav").relative_to(AUDIO)), "m4a": str(base.with_suffix(".m4a").relative_to(AUDIO)),
                             "seconds": round(len(y) / SR, 2)})
            for b in BEDS:
                bed = beds[b]; start = int(rng.uniform(0, len(bed) - len(y))); seg = bed[start:start + len(y)]
                n_rms = float(np.sqrt(np.mean(seg ** 2)))
                for snr in SNRS:
                    g = s_rms / (n_rms * 10 ** (snr / 20))
                    m = y + g * seg
                    peak = np.abs(m).max()
                    if peak > 0.98: m = m / peak * 0.98
                    out = MIX / f"{uid}-{v}-{b}-{snr}"
                    sf.write(out.with_suffix(".wav"), m.astype(np.float32), SR); encode_m4a(out.with_suffix(".wav"), out.with_suffix(".m4a"))
                    manifest.append({"id": f"{uid}-{v}-{b}-{snr}", "utterance": uid, "item": item, "voice": v, "bed": b, "snr": snr,
                                     "wav": str(out.with_suffix(".wav").relative_to(AUDIO)), "m4a": str(out.with_suffix(".m4a").relative_to(AUDIO)),
                                     "seconds": round(len(y) / SR, 2)})
            print("mixed", uid, v, flush=True)
    print(len(manifest), "samples")

def synthesize(root, key):
    """Everything absent under `root`: the voices, the beds, the mix. Refuses without numpy, scipy and soundfile."""
    if np is None:
        raise SystemExit("noise-check refuses: synthesizing the absent samples needs numpy, scipy and soundfile "
                         "(.venv/bin/pip install numpy scipy soundfile) and macOS afconvert -- or point "
                         "KEEL_NOISE_SAMPLES at the kept set")
    use(root, key)
    do_tts(); do_beds(); do_mix()


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    key = (os.environ.get("KEEL_OPENAI_API_KEY") or "").strip()
    if what in ("tts", "all") and not key:
        raise SystemExit("synth refuses: KEEL_OPENAI_API_KEY is not set in this shell")
    from evals.noise.pipeline import samples_root
    use(samples_root(), key)
    if what in ("tts", "all"): do_tts()
    if what in ("beds", "all"): do_beds()
    if what in ("mix", "all"): do_mix()
