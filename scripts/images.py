"""Renders 3D de uma ideia por cena — Codex CLI image_gen pela ASSINATURA do ChatGPT (sem API).
Uso: python3 images.py <pasta_saida> c_nome="objeto…" d_nome="objeto…"   (paralelo, pula o que já existe)
c_ = fundo claro (papel), d_ = fundo escuro (preto INEMA). Cada prompt = SÓ o objeto; o estilo da casa é acrescentado aqui.
FV_IMG=flux usa o flux2-klein local (inemaimg :8000) como reserva, quando o Codex estiver sem cota."""
import sys, os, json, base64, urllib.request, subprocess, tempfile, glob, concurrent.futures as cf

STYLE = ("Premium 3D render, matte realistic materials, soft NEUTRAL white studio light (no yellow or orange colour cast), "
         "single centred hero object with a gentle contact shadow, plenty of empty space around it, plain seamless background "
         "of solid colour {bg}. One small accent detail in yellow #FACC15 is allowed. NO text, NO letters, NO logos, NO watermark. "
         "Any robot must be a sleek industrial humanoid (Tesla Optimus style) with a dark visor — never a cute cartoon, mascot or toy. "
         "Wide 16:9 landscape composition, object fills about 45% of the frame height.")


def gen(out, name, prompt, bg):
    p = os.path.join(out, name + ".png")
    if os.path.exists(p): return p, "cache"
    text = prompt + ". " + STYLE.format(bg=bg)
    return gen_flux(p, text) if os.environ.get("FV_IMG", "codex") == "flux" else gen_codex(p, text)


def gen_codex(p, text):
    """Geração de imagem do ChatGPT pelo Codex CLI (login da assinatura). ~1–2 min por imagem, no máximo 3 em paralelo."""
    wd = tempfile.mkdtemp(prefix="fvimg_")
    msg = ("Use your built-in image generation tool (NOT code, NOT PIL) to create ONE image, 16:9 landscape, and save it in the "
           "current folder as out.png. " + text + "\nReply only with the saved path.")
    pr = subprocess.run(["codex", "exec", "--skip-git-repo-check", "-s", "workspace-write", "-"], input=msg, cwd=wd,
                        capture_output=True, text=True, timeout=900)
    c = glob.glob(os.path.join(wd, "*.png")) + glob.glob(os.path.join(wd, "*.jpg"))
    if not c: raise RuntimeError("codex não gerou imagem: " + (pr.stdout + pr.stderr)[-300:])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", c[0], p], check=True)
    return p, "ok"


def gen_flux(p, text):
    """Reserva local: flux2-klein no inemaimg (http://localhost:8000). Ajuste FV_FLUX_URL se a porta mudar."""
    url = os.environ.get("FV_FLUX_URL", "http://localhost:8000/generate")
    body = json.dumps({"model": "flux2-klein", "prompt": text, "width": 1536, "height": 864, "steps": 4,
                       "guidance_scale": 1.0, "seed": 7}).encode()
    d = json.load(urllib.request.urlopen(urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}), timeout=600))
    open(p, "wb").write(base64.b64decode(d["image"]))
    return p, "ok"


if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    jobs = []
    for a in sys.argv[2:]:
        n, pr = a.split("=", 1)
        bg = "#0c0c10 near-black" if n.startswith("d_") else "#f2f1ec light warm-grey paper"
        jobs.append((n, pr, bg))
    with cf.ThreadPoolExecutor(3) as ex:
        for f in cf.as_completed([ex.submit(gen, out, n, p, b) for n, p, b in jobs]):
            try: print(*f.result())
            except Exception as e: print("FALHOU", e)
