"""Ajudante do tts.py — roda no Python do inemavox (faster-whisper + soundfile).
Uso: python _align.py <pedido.json> <saida.json>
pedido = {"lang": "pt", "segs": [{"wav": ..., "text": ...}, ...]}
Para cada frase: corta o silêncio da ponta, transcreve com tempo por palavra e mede a semelhança com o texto.
Saída = {"segs": [{"wav": <cortado>, "dur": s, "words": [[w, a, b]], "heard": "...", "sim": 0..1}]}"""
import sys, json, re, difflib, unicodedata, fcntl
import numpy as np, soundfile as sf

req = json.load(open(sys.argv[1]))


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9%]", "", w)


def trim(path):
    a, sr = sf.read(path, dtype="float32")
    if a.ndim > 1: a = a.mean(1)
    thr = 10 ** (-38 / 20) * max(1e-6, float(np.abs(a).max()))
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx):
        pad = int(sr * 0.06)
        a = a[max(0, idx[0] - pad): min(len(a), idx[-1] + pad)]
    out = path.replace(".wav", "_t.wav")
    sf.write(out, a, sr)
    return out, len(a) / sr


# Um Whisper por vez na máquina (mesmo lock do explicavideos: GPU dividida).
with open("/tmp/explicavideos-whisper.lock", "w") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    from faster_whisper import WhisperModel
    try:
        model = WhisperModel(req.get("model", "large-v3"), device="cuda", compute_type="float16")
    except Exception:
        model = WhisperModel(req.get("model", "large-v3"), device="cpu", compute_type="int8")
    res = []
    for sg in req["segs"]:
        wav, dur = trim(sg["wav"])
        segs, _ = model.transcribe(wav, language=req.get("lang", "pt"), word_timestamps=True,
                                   condition_on_previous_text=False, initial_prompt=req.get("prompt", "INEMA, Nei Maldaner."))
        heard = [(w.word.strip(), float(w.start), float(w.end)) for s in segs for w in (s.words or []) if w.word.strip()]
        want = sg["text"].split()
        a, b = [norm(w) for w in want], [norm(h[0]) for h in heard]
        sim = difflib.SequenceMatcher(None, a, b).ratio() if a else 0.0
        # tempo de cada palavra do ROTEIRO (grafia certa na legenda); sem par = interpolado
        times = [None] * len(want)
        for blk in difflib.SequenceMatcher(None, a, b).get_matching_blocks():
            for k in range(blk.size):
                h = heard[blk.b + k]; times[blk.a + k] = [h[1], h[2]]
        known = [i for i, t in enumerate(times) if t]
        for i in range(len(want)):
            if times[i]: continue
            lo = max([k for k in known if k < i], default=None); hi = min([k for k in known if k > i], default=None)
            t0 = times[lo][1] if lo is not None else 0.0
            t1 = times[hi][0] if hi is not None else dur
            n0 = lo if lo is not None else -1; n1 = hi if hi is not None else len(want)
            step = (t1 - t0) / max(1, n1 - n0 - 1)
            times[i] = [t0 + step * (i - n0 - 1) + 0.01, t0 + step * (i - n0) - 0.01]
        res.append({"wav": wav, "dur": dur, "sim": round(sim, 3), "heard": " ".join(h[0] for h in heard),
                    "words": [[w, max(0.0, t[0]), min(dur, max(t[1], t[0] + 0.08))] for w, t in zip(want, times)]})
json.dump({"segs": res}, open(sys.argv[2], "w"), ensure_ascii=False)
