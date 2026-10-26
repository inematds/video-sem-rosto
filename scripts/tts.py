"""Narração LOCAL com tempo por palavra — sem API.
Uso: python3 tts.py <job_dir>   (lê <job>/script.txt -> vo.mp3, words.json [[palavra, início, fim], …], vo_qc.json)

Como funciona:
  1. Divide o roteiro em batidas (linha em branco) e frases (≤ 160 caracteres).
  2. Chatterbox (inemavox, GPU) gera cada frase com a voz clonada de FV_VOICE (padrão: nei).
  3. Whisper large-v3 local ouve cada frase, mede a semelhança com o texto e dá o tempo de cada palavra.
     Frase abaixo de FV_MIN_SIM (0,80) é gerada de novo (até 2 vezes); se continuar ruim, para com erro.
  4. Junta tudo com pausas (0,28 s entre frases, 0,55 s entre batidas) e grava vo.mp3 + words.json.
Variáveis: FV_VOICE (nei|nei2|nei3|nei4|caminho.wav) · FV_LANG (pt) · FV_ATEMPO (1.0; máx. 1.15) ·
           FV_CFG / FV_EXAG (0.6/0.6) · CHATTERBOX_PYTHON · INEMAVOX_DIR."""
import sys, os, json, re, subprocess, tempfile, shutil

HOME = os.path.expanduser("~")
VOX = os.environ.get("INEMAVOX_DIR", os.path.join(HOME, "projetos/inemavox"))
CB_PY = os.environ.get("CHATTERBOX_PYTHON", os.path.join(HOME, "miniconda3/envs/chatterbox/bin/python3"))
VOX_PY = os.path.join(VOX, "venv/bin/python")
REFS = os.path.join(HOME, "projetos/timesmkt3/media/voice-refs")
VOICE = os.environ.get("FV_VOICE", "nei")
REF = VOICE if VOICE.endswith(".wav") else os.path.join(REFS, VOICE + ".wav")
LANG = os.environ.get("FV_LANG", "pt")
ATEMPO = min(1.15, float(os.environ.get("FV_ATEMPO", "1.0")))
MIN_SIM = float(os.environ.get("FV_MIN_SIM", "0.80"))
HERE = os.path.dirname(os.path.abspath(__file__))
for need in (CB_PY, VOX_PY, REF):
    if not os.path.exists(need): raise SystemExit(f"Falta: {need} (ver README › Instalação)")

job = os.path.abspath(sys.argv[1])
beats = [re.sub(r"\s+", " ", p).strip() for p in open(os.path.join(job, "script.txt")).read().split("\n\n") if p.strip()]


def sentences(p, mx=160):
    out, cur = [], ""
    for s in re.split(r"(?<=[.!?…])\s+", p):
        if len(cur) + len(s) + 1 <= mx or not cur: cur = (cur + " " + s).strip()
        else: out.append(cur); cur = s
    if cur: out.append(cur)
    fixed = []
    for s in out:                       # frase única longa demais: quebra em vírgula/palavra
        while len(s) > mx:
            cut = s.rfind(", ", 0, mx); cut = cut + 1 if cut > 40 else s.rfind(" ", 0, mx)
            fixed.append(s[:cut].strip()); s = s[cut:].strip()
        fixed.append(s)
    return fixed


segs = [(bi, s) for bi, p in enumerate(beats) for s in sentences(p)]
work = tempfile.mkdtemp(prefix="fvtts_", dir=job)


def synth(items, tag):
    """items = [(idx, texto)] -> {idx: wav}. Um carregamento do modelo por chamada."""
    wd = os.path.join(work, tag); os.makedirs(wd, exist_ok=True)
    sj, oj = os.path.join(wd, "segs.json"), os.path.join(wd, "out.json")
    json.dump([{"text_trad": t, "start": 0.0, "end": 1.0} for _, t in items], open(sj, "w"), ensure_ascii=False)
    cmd = [CB_PY, os.path.join(VOX, "chatterbox_tts_worker.py"), "--segments-json", sj, "--workdir", wd, "--lang", LANG,
           "--output-json", oj, "--ref", REF, "--cfg-weight", os.environ.get("FV_CFG", "0.6"),
           "--exaggeration", os.environ.get("FV_EXAG", "0.6"), "--temperature", "0.75"]
    r = subprocess.run(cmd, cwd=VOX, capture_output=True, text=True, timeout=3600)
    if r.returncode != 0: raise SystemExit("Chatterbox falhou:\n" + (r.stdout + r.stderr)[-1500:])
    d = json.load(open(oj))
    return {idx: s["file"] for (idx, _), s in zip(items, d["segments"])}


def align(wavs):
    """wavs = {idx: wav} -> {idx: resultado do _align.py}"""
    keys = sorted(wavs)
    rq, rs = os.path.join(work, "al_in.json"), os.path.join(work, "al_out.json")
    json.dump({"lang": LANG, "segs": [{"wav": wavs[k], "text": segs[k][1]} for k in keys]}, open(rq, "w"), ensure_ascii=False)
    r = subprocess.run([VOX_PY, "-I", os.path.join(HERE, "_align.py"), rq, rs], capture_output=True, text=True, timeout=3600)
    if r.returncode != 0: raise SystemExit("Whisper falhou:\n" + (r.stdout + r.stderr)[-1500:])
    return dict(zip(keys, json.load(open(rs))["segs"]))


todo = list(range(len(segs))); got = {}
for attempt in range(3):
    wavs = synth([(i, segs[i][1]) for i in todo], f"t{attempt}")
    res = align(wavs)
    for i, r in res.items():
        if i not in got or r["sim"] > got[i]["sim"]: got[i] = r
    todo = [i for i in todo if got[i]["sim"] < MIN_SIM]
    print(f"tentativa {attempt + 1}: {len(segs) - len(todo)}/{len(segs)} frases ok", flush=True)
    if not todo: break
bad = [(i, got[i]["sim"], segs[i][1], got[i]["heard"]) for i in todo]

# junta com pausas e monta words.json
words, files, t = [], [], 0.0
sil = lambda d: (lambda p: (subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono",
                                            "-t", f"{d:.3f}", p], check=True), p)[1])(os.path.join(work, f"sil{d:.2f}.wav"))
for i, (bi, _) in enumerate(segs):
    if i:
        gap = 0.55 if bi != segs[i - 1][0] else 0.28
        files.append(sil(gap)); t += gap
    r = got[i]; files.append(r["wav"])
    words += [[w, round(t + a, 3), round(t + b, 3)] for w, a, b in r["words"]]
    t += r["dur"]
lst = os.path.join(work, "list.txt"); open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
raw = os.path.join(work, "vo.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-ar", "24000", "-ac", "1", raw], check=True)
af = ["-af", f"atempo={ATEMPO}"] if ATEMPO != 1.0 else []
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, *af, "-ar", "44100", "-b:a", "192k", os.path.join(job, "vo.mp3")], check=True)
if ATEMPO != 1.0: words = [[w, round(a / ATEMPO, 3), round(b / ATEMPO, 3)] for w, a, b in words]
json.dump(words, open(os.path.join(job, "words.json"), "w"), ensure_ascii=False)
qc = {"voz": VOICE, "frases": len(segs), "semelhanca_min": min(r["sim"] for r in got.values()),
      "semelhanca_media": round(sum(r["sim"] for r in got.values()) / len(got), 3),
      "ruins": [{"frase": s, "ouvido": h, "sim": m} for _, m, s, h in bad]}
json.dump(qc, open(os.path.join(job, "vo_qc.json"), "w"), ensure_ascii=False, indent=1)
shutil.rmtree(work, ignore_errors=True)
print(f"vo.mp3 {t / ATEMPO:.1f}s, {len(words)} palavras, semelhança mín {qc['semelhanca_min']} média {qc['semelhanca_media']}")
print(" ".join(f"{w}@{s:.2f}" for w, s, e in words))
if bad: raise SystemExit(f"{len(bad)} frase(s) abaixo de {MIN_SIM} — ver vo_qc.json (reescreva a frase ou rode de novo)")
