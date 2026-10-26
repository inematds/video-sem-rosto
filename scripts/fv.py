"""video-sem-rosto — motor de motion design para vídeos 16:9 SEM ROSTO (sem câmera, sem avatar).

Tema padrão "inema" (FV_THEME=inema): cenas alternando PAPEL claro e PRETO #0c0c10, cartão AMARELO #FACC15 de
afirmação ~1x por minuto; títulos em Sora 800 com UMA palavra-chave em destaque (amarelo no escuro, marca-texto no
claro); render 3D por ideia; pílula de contexto com a origem; chips que entram a cada batida falada; print real do
site numa janela de navegador com zoom + carimbo; legenda karaokê escura embaixo (falada = branco, atual = amarelo,
por vir = cinza). FV_THEME=original devolve a paleta creme/laranja do kit de base.

Every scene is its own HTML page; all times are ABSOLUTE voiceover seconds (straight from words.json), so a scene is
written by reading the word timings. Pages are seeked frame-by-frame in headless Chromium and piped into ffmpeg.

    from fv import *
    v = Video(job_dir)                  # loads words.json + vo.mp3
    v.scene(0, 3.3, "cream", head(...) + hero(...) + chip(...))
    v.render()                          # -> <job>/out/final.mp4
"""
import os, re, json, html as _h, subprocess, urllib.request, itertools, shutil, math, concurrent.futures as cf

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(SKILL, "cache")
W, H = 1920, 1080
FPS = int(os.environ.get("FV_FPS", 60))
THEME = os.environ.get("FV_THEME", "inema")
INK, CREAM, DARK, ORANGE, GREY = "#16110f", "#efe8df", "#1b1513", "#e2622b", "#a59d95"
ON_ACC = "#fff"                      # letra sobre o acento
CAP_BG, CAP_SPOKEN = "#fff", "#16110f"
if THEME == "inema":
    INK, CREAM, DARK, ORANGE, GREY = "#0c0c10", "#f2f1ec", "#0c0c10", "#FACC15", "#8b8b94"
    ON_ACC = "#1a1206"
    CAP_BG, CAP_SPOKEN = "#0c0c10", "#ffffff"
_uid = itertools.count()


def _get(url, name):
    p = os.path.join(CACHE, name)
    if not os.path.exists(p):
        os.makedirs(CACHE, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        open(p, "wb").write(urllib.request.urlopen(req, timeout=30).read())
    return p


def icon(name, color=INK, size=34, stroke=2.2):
    """Inline Lucide icon (lock, bot, calendar-clock, brain, briefcase, shield-check, server, star, arrow-right…)."""
    s = open(_get(f"https://cdn.jsdelivr.net/npm/lucide-static@0.460.0/icons/{name}.svg", f"lucide_{name}.svg")).read()
    return (s.replace('stroke="currentColor"', f'stroke="{color}"').replace('width="24"', f'width="{size}"')
             .replace('height="24"', f'height="{size}"').replace('stroke-width="2"', f'stroke-width="{stroke}"'))


def logo_src(slug, color=None):
    """Real brand logo (Simple Icons) as a local file path for <img>."""
    c = f"/{color.strip('#')}" if color else ""
    return "file://" + _get(f"https://cdn.simpleicons.org/{slug}{c}", f"si_{slug}_{(color or 'brand').strip('#')}.svg")


def em(s):
    """Escape text; *word* -> orange keyword, _word_ -> italic serif accent."""
    s = _h.escape(str(s))
    s = re.sub(r"\*(.+?)\*", r"<b class='k'>\1</b>", s)
    return re.sub(r"_(.+?)_", r"<i class='sf'>\1</i>", s)


def _wordlist(text):
    """Split into words, carrying *multi word* / _multi word_ accents onto every word they cover."""
    out, st = [], None
    for w in text.split(" "):
        raw = w
        if st is None and raw[:1] in "*_":
            st = raw[0]; raw = raw[1:]
        cur = st
        if st and raw.rstrip("?.!,:;").endswith(st):
            i = raw.rstrip("?.!,:;"); tail = raw[len(i):]; raw = i[:-1] + tail; st = None
        e = _h.escape(raw)
        out.append(f"<b class='k'>{e}</b>" if cur == "*" else f"<i class='sf'>{e}</i>" if cur == "_" else e)
    return out


def ms(t):
    return f"{t * 1000:.0f}ms"


# ----------------------------------------------------------------------------- pieces (all times = absolute seconds)

def kicker(text, at, y=70, dark=False):
    """Black (or white on dark) pill naming the source/context, top centre."""
    bg, fg = ("#fff", INK) if dark else (INK, "#fff")
    return (f"<div class='pop' style='--at:{ms(at)};position:absolute;left:50%;top:{y}px;transform:translateX(-50%)'>"
            f"<div style='background:{bg};color:{fg};font:700 24px Manrope;padding:10px 22px;border-radius:99px;white-space:nowrap'>{em(text)}</div></div>")


def head(text, at, y=140, size=118, color=None, x=None, align="center", width=1700, per_word=None):
    """Condensed CAPS headline (Anton). *word* = orange. per_word=[t1,t2,…] makes words land on their spoken times."""
    color = color or "#fff"
    parts, out = _wordlist(text), []
    for i, w in enumerate(parts):
        t = per_word[i] if per_word and i < len(per_word) else at + i * 0.07
        out.append(f"<span class='rise' style='--at:{ms(t)};display:inline-block'>{w}</span>")
    left = f"left:{x}px" if x is not None else f"left:{(W - width) / 2}px"
    return (f"<div style='position:absolute;{left};top:{y}px;width:{width}px;text-align:{align};font:400 {size}px/1.02 Anton;"
            f"letter-spacing:.005em;text-transform:uppercase;color:{color}'>{' '.join(out)}</div>")


def title(text, at, y=150, size=104, color=INK, x=None, align="center", width=1700, per_word=None):
    """Sentence-case bold headline (Manrope 800) with _serif italic_ / *orange* accents — the 'Still _losing_ leads?' look."""
    parts, out = _wordlist(text), []
    for i, w in enumerate(parts):
        t = per_word[i] if per_word and i < len(per_word) else at + i * 0.06
        out.append(f"<span class='rise' style='--at:{ms(t)};display:inline-block'>{w}</span>")
    left = f"left:{x}px" if x is not None else f"left:{(W - width) / 2}px"
    return (f"<div style='position:absolute;{left};top:{y}px;width:{width}px;text-align:{align};font:800 {size}px/1.05 Manrope;"
            f"letter-spacing:-.035em;color:{color}'>{' '.join(out)}</div>")


def hero(img, at, cx=960, cy=560, w=900, dark=False, float_px=12):
    """3D clay render, edges feathered into the scene background, gentle float. img = path."""
    return (f"<div class='heroin' style='--at:{ms(at)};position:absolute;left:{cx - w / 2}px;top:{cy - w * 9 / 32}px;width:{w}px'>"
            f"<div class='float' style='--fp:{float_px}px'><img src='file://{img}' style='width:100%;display:block;"
            f"-webkit-mask-image:radial-gradient(ellipse 50% 50% at 50% 50%,#000 62%,transparent 100%)'></div></div>")


def chip(text, at, x, y, ico=None, accent=False, size=30, anchor="center", cls="pop"):
    """White chip (or orange accent chip) that pops in on its spoken word."""
    bg, fg, ic = (ORANGE, ON_ACC, ON_ACC) if accent else ("#fff", INK, INK)
    i = f"<span style='display:inline-flex;margin-right:12px'>{icon(ico, ic, size + 2)}</span>" if ico else ""
    tx = {"center": "-50%", "left": "0", "right": "-100%"}[anchor]
    return (f"<div style='position:absolute;left:{x}px;top:{y}px;transform:translateX({tx})'><div class='{cls}' style='--at:{ms(at)}'>"
            f"<div class='{"acc" if accent else ""}' style='display:flex;align-items:center;background:{bg};color:{fg};font:700 {size}px Manrope;padding:16px 26px;"
            f"border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.18);white-space:nowrap'>{i}<span>{em(text)}</span></div></div></div>")


def tile(src, at, x, y, size=190, label=None, dark=True, cls="pop"):
    """Rounded app tile with a logo image + label under it."""
    lab = (f"<div style='margin-top:18px;font:700 30px Manrope;color:{'#fff' if dark else INK};text-align:center;white-space:nowrap'>{em(label)}</div>"
           if label else "")
    return (f"<div style='position:absolute;left:{x - size / 2}px;top:{y}px;width:{size}px'><div class='{cls}' style='--at:{ms(at)}'>"
            f"<div style='width:{size}px;height:{size}px;border-radius:{size * .24}px;background:#fff;display:flex;align-items:center;"
            f"justify-content:center;box-shadow:0 18px 50px rgba(0,0,0,.35)'><img src='{src}' style='width:{size * .56}px;height:{size * .56}px'></div>{lab}</div></div>")


def browser(img, at, x, y, w, h, scroll=(), zoom=(), url="github.com", page_w=2400):
    """Real screencast: tall page capture inside a browser frame.
    scroll=[(t, page_y_px_in_capture)], zoom=[(t, scale, focus_x, focus_y)] (focus in frame px). Keyframes are generated."""
    uid = next(_uid)
    sc = page_w / w
    css = ""
    if scroll:
        kf = [(t, -py / sc) for t, py in scroll]
        t0, t1 = kf[0][0], kf[-1][0]
        span = max(t1 - t0, .01)
        steps = "".join(f"{(t - t0) / span * 100:.2f}%{{transform:translateY({yy:.1f}px)}}" for t, yy in kf)
        css += f"@keyframes sc{uid}{{{steps}}}.sc{uid}{{animation:sc{uid} {span:.3f}s cubic-bezier(.65,0,.35,1) {t0:.3f}s both}}"
    inner_cls = f"sc{uid}" if scroll else ""
    zcls = ""
    if zoom:
        t0, t1 = zoom[0][0], zoom[-1][0]
        span = max(t1 - t0, .01)
        steps = "".join(f"{(t - t0) / span * 100:.2f}%{{transform:scale({s})}}" for t, s, fx, fy in zoom)
        fx, fy = zoom[-1][2], zoom[-1][3]
        css += f"@keyframes zm{uid}{{{steps}}}.zm{uid}{{transform-origin:{fx}px {fy}px;animation:zm{uid} {span:.3f}s cubic-bezier(.65,0,.35,1) {t0:.3f}s both}}"
        zcls = f"zm{uid}"
    bar = ("<div style='height:46px;background:#f3f1ee;display:flex;align-items:center;gap:9px;padding:0 18px;border-bottom:1px solid #e3ded8'>"
           + "".join(f"<i style='width:13px;height:13px;border-radius:50%;background:{c}'></i>" for c in ("#ff5f57", "#febc2e", "#28c840"))
           + f"<div style='margin-left:18px;flex:1;max-width:560px;height:28px;border-radius:8px;background:#fff;font:500 16px Manrope;color:#6b625b;"
             f"display:flex;align-items:center;padding:0 14px'>🔒&nbsp; {_h.escape(url)}</div></div>")
    return (f"<style>{css}</style><div class='heroin' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;"
            f"border-radius:18px;overflow:hidden;background:#fff;box-shadow:0 30px 80px rgba(0,0,0,.28)'>{bar}"
            f"<div style='position:relative;height:{h - 46}px;overflow:hidden'><div class='{zcls}' style='width:100%;height:100%'>"
            f"<img class='{inner_cls}' src='file://{img}' style='width:{w}px;display:block'></div></div></div>")


def stamp(text, at, x, y, size=78, rot=-8):
    """Red outlined stamp that slams in (big stat on a screenshot)."""
    return (f"<div style='position:absolute;left:{x}px;top:{y}px;transform:translate(-50%,-50%) rotate({rot}deg)'><div class='slam' style='--at:{ms(at)}'>"
            f"<div style='border:7px solid #e03a2f;color:#e03a2f;background:rgba(255,255,255,.92);font:400 {size}px Anton;padding:6px 26px;"
            f"border-radius:14px;white-space:nowrap;letter-spacing:.01em'>{em(text)}</div></div></div>")


def ring(at, x, y, w, h, color=ORANGE):
    """Hand-drawn style highlight ring around a box (frame px)."""
    return (f"<div class='ringin' style='--at:{ms(at)};position:absolute;left:{x - 14}px;top:{y - 10}px;width:{w + 28}px;height:{h + 20}px;"
            f"border:5px solid {color};border-radius:999px'></div>")


def card(inner, at, x, y, w, cls="pop", pad=34, dark=False):
    bg = "#241c19" if dark else "#fff"
    return (f"<div style='position:absolute;left:{x}px;top:{y}px;width:{w}px'><div class='{cls}' style='--at:{ms(at)}'>"
            f"<div style='background:{bg};border-radius:24px;padding:{pad}px;box-shadow:0 20px 60px rgba(0,0,0,.22)'>{inner}</div></div></div>")


def cursor_click(t_move, t_click, x0, y0, x1, y1):
    """Mouse cursor travels to (x1,y1) and clicks at t_click."""
    uid = next(_uid)
    css = (f"@keyframes cm{uid}{{0%{{transform:translate({x0}px,{y0}px)}}100%{{transform:translate({x1}px,{y1}px)}}}}"
           f".cm{uid}{{animation:cm{uid} {t_click - t_move:.3f}s cubic-bezier(.45,0,.2,1) {t_move:.3f}s both}}")
    svg = ("<svg width='54' height='54' viewBox='0 0 24 24'><path d='M4 2l15 9-6.5 1.6L9.6 19z' fill='#16110f' stroke='#fff' "
           "stroke-width='1.6' stroke-linejoin='round'/></svg>")
    return (f"<style>{css}</style><div class='cm{uid}' style='position:absolute;left:0;top:0;z-index:50'><div class='fade' style='--at:{ms(t_move)}'>"
            f"<div class='press' style='--at:{ms(t_click)}'>{svg}</div></div></div>")


def big_card(lines, color=ORANGE):
    """Full-colour statement card ("This is _why._"): lines=[(text, t)] stacked centre."""
    rows = "".join(f"<div class='rise' style='--at:{ms(t)}'>{em(tx)}</div>" for tx, t in lines)
    return (f"<div style='position:absolute;inset:0;background:radial-gradient(ellipse at 50% 40%,#ee7a45,{color} 70%)'></div>"
            f"<div style='position:absolute;left:0;right:0;top:330px;text-align:center;color:{ON_ACC};font:800 132px/1.08 Manrope;letter-spacing:-.04em'>{rows}</div>")


# ----------------------------------------------------------------------------- imagem real + prova (opcional)

def prep_clip(src):
    """Convert a downloaded clip (mp4 from X/YouTube/press kit) to a seek-friendly silent WebM (Playwright's Chromium can't
    decode H.264). Returns the .webm path. Cached next to the source."""
    out = os.path.splitext(src)[0] + ".fv.webm"
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an", "-vf", "scale='min(1600,iw)':-2,fps=30", "-c:v", "libvpx-vp9",
                        "-b:v", "0", "-crf", "30", "-g", "6", "-deadline", "good", "-cpu-used", "4", "-row-mt", "1", out], check=True)
    return out


def clip(src, at, x, y, w, start=0.0, credit=None, frame=True, aspect=None, cls="heroin"):
    """REAL footage on screen (official teaser, tester demo, product video): plays from `start` seconds of the clip when the
    scene reaches `at`. Always pass credit="@handle · X" (or "Teaser oficial · @conta"). Keep each use short
    (≈3–8 s) and add commentary/graphics around it. src = mp4 path (auto-converted)."""
    wb = prep_clip(src)
    if aspect is None:
        try:
            wh = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                          "-of", "csv=p=0", wb]).decode().strip().split(",")
            aspect = int(wh[0]) / int(wh[1])
        except Exception:
            aspect = 16 / 9
    h = w / aspect
    vid = (f"<video class='fvclip' data-at='{at}' data-start='{start}' src='file://{wb}' muted playsinline preload='auto' "
           f"style='width:{w}px;height:{h:.0f}px;display:block;object-fit:cover;background:#000'></video>")
    box = (f"<div style='border-radius:18px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.35);{'border:6px solid #fff;' if frame else ''}'>{vid}</div>")
    cr = (f"<div style='position:absolute;left:14px;bottom:14px;background:rgba(22,17,15,.85);color:#fff;font:700 20px Manrope;"
          f"padding:8px 14px;border-radius:10px'>{_h.escape(credit)}</div>" if credit else "")
    return f"<div class='{cls}' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;width:{w}px'>{box}{cr}</div>"


PROOF = os.path.join(SKILL, "assets", "proof")   # prints SEUS (depoimentos, página da oferta) — opcional


def proof_badge(at, x=960, y=70, dark=False, text="Depoimentos reais"):
    """Selo '★★★★★ Depoimentos reais'. Nunca mostrar nota numérica: mostre os próprios depoimentos."""
    bg, fg = ("#fff", INK) if dark else (INK, "#fff")
    return (f"<div class='pop' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;transform:translateX(-50%)'><div style='background:{bg};color:{fg};"
            f"font:800 30px Manrope;padding:14px 28px;border-radius:99px;white-space:nowrap'><span style='color:#f5b301'>★★★★★</span>&nbsp; {_h.escape(text)}</div></div>")


def reviews_wall(at, dur, x=110, y=170, w=1700, h=690, cols=2, start_idx=0, speed=45):
    """Prints de depoimentos (assets/proof/review_*.png) subindo em colunas durante o CTA. dur = segundos na tela."""
    import glob
    files = sorted(glob.glob(os.path.join(PROOF, "review_*.png")))
    if not files: return ""
    cw = (w - (cols - 1) * 26) / cols
    out = []
    for c in range(cols):
        pick = [files[(start_idx + c + k * cols) % len(files)] for k in range(8)]
        cards = "".join(f"<img src='file://{f}' style='width:{cw:.0f}px;display:block;margin-bottom:20px;border-radius:16px;background:#fff;"
                        f"box-shadow:0 12px 34px rgba(0,0,0,.18)'>" for f in pick)
        uid = next(_uid); dist = speed * dur * (1.0 if c % 2 == 0 else 0.75)
        out.append(f"<style>@keyframes rw{uid}{{from{{transform:translateY(0)}}to{{transform:translateY(-{dist:.0f}px)}}}}"
                   f".rw{uid}{{animation:rw{uid} {dur:.2f}s linear {at:.3f}s both}}</style>"
                   f"<div style='position:absolute;left:{x + c * (cw + 26):.0f}px;top:{y}px;width:{cw:.0f}px;height:{h}px;overflow:hidden;"
                   f"-webkit-mask-image:linear-gradient(transparent,#000 8%,#000 92%,transparent)'><div class='rise' style='--at:{ms(at + c * .12)}'>"
                   f"<div class='rw{uid}' style='padding-top:{30 + c * 60}px'>{cards}</div></div></div>")
    return "".join(out)


def offer_page(at, x=260, y=120, w=1400, h=760, scroll=None, img=None):
    """Print real da página da sua oferta (assets/proof/offer_page.png, ou img=) rolando numa janela de navegador.
    URL na barra = FV_OFFER_URL (padrão inema.club)."""
    return browser(img or os.path.join(PROOF, "offer_page.png"), at, x, y, w, h, scroll=scroll or [(at + .6, 0), (at + 4, 1500)],
                   url=os.environ.get("FV_OFFER_URL", "inema.club"), page_w=2800)


# ----------------------------------------------------------------------------- captions

def caption_chunks(words, max_words=3):
    """Group words into 1–3 word caption chunks, breaking after punctuation."""
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= max_words or re.search(r"[.,?!:;]$", w[0]):
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    return chunks


def captions(words, s, e, y=925):
    """Karaoke caption pill for every chunk that starts inside [s, e)."""
    out = []
    chunks = caption_chunks(words)
    for ci, ch in enumerate(chunks):
        c0 = ch[0][1]
        if not (s <= c0 < e): continue
        c1 = chunks[ci + 1][0][1] if ci + 1 < len(chunks) else ch[-1][2] + 0.8
        c1 = min(c1, e)
        spans = []
        for w, a, b in ch:
            spans.append(f"<span class='kw' style='--at:{ms(a)};--to:{ms(max(b, a + .12))}'>{_h.escape(w)}</span>")
        out.append(f"<div class='cap' style='--s:{ms(c0)};--d:{ms(c1 - c0)};position:absolute;left:50%;top:{y}px;transform:translateX(-50%)'>"
                   f"<div class='capin' style='--at:{ms(c0)}'><div style='background:{CAP_BG};border-radius:18px;padding:14px 30px 16px;"
                   f"box-shadow:0 8px 0 rgba(0,0,0,.10),0 14px 40px rgba(0,0,0,.18);border:2px solid rgba(0,0,0,.08);font:800 50px Manrope;"
                   f"letter-spacing:-.02em;white-space:nowrap;word-spacing:.08em'>{' '.join(spans)}</div></div></div>")
    return "".join(out)


# ----------------------------------------------------------------------------- page template

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Manrope:wght@500;700;800&family=Instrument+Serif:ital@1&display=block');
*{margin:0;padding:0;box-sizing:border-box} html,body{width:1920px;height:1080px;overflow:hidden}
.k{color:#e2622b;font-weight:inherit} .sf{font-family:'Instrument Serif';font-style:italic;font-weight:400;letter-spacing:-.01em;color:inherit;padding-right:.06em}
.dark .sf, .orange .sf{color:inherit} .acc .k{color:#fff;text-decoration:underline;text-decoration-thickness:3px;text-underline-offset:5px}
.stage{position:absolute;inset:0;overflow:hidden}
.cream{background:radial-gradient(ellipse at 50% 35%,#f8f4ee 0%,#efe8df 55%,#e6ddd2 100%)}
.dark{background:radial-gradient(ellipse at 50% 38%,#3a2c26 0%,#1b1513 60%,#120d0c 100%)}
.scenein{animation:scenein .42s cubic-bezier(.16,1,.3,1) var(--at) both}
@keyframes scenein{from{transform:scale(1.07);filter:blur(10px)}to{transform:none;filter:none}}
.drift{animation:drift var(--d) linear var(--at) both} @keyframes drift{from{transform:scale(1)}to{transform:scale(1.045)}}
.pop{animation:pop .5s cubic-bezier(.34,1.56,.64,1) var(--at) both} @keyframes pop{from{opacity:0;transform:scale(.6) translateY(20px)}to{opacity:1;transform:none}}
.rise{animation:rise .5s cubic-bezier(.16,1,.3,1) var(--at) both} @keyframes rise{from{opacity:0;transform:translateY(40px);filter:blur(8px)}to{opacity:1;transform:none;filter:none}}
.fade{animation:fade .3s ease var(--at) both} @keyframes fade{from{opacity:0}to{opacity:1}}
.heroin{animation:heroin .8s cubic-bezier(.16,1,.3,1) var(--at) both} @keyframes heroin{from{opacity:0;transform:scale(.82) translateY(50px)}to{opacity:1;transform:none}}
.float{animation:float 3.2s ease-in-out 0s infinite alternate both} @keyframes float{from{transform:translateY(calc(var(--fp)*-1))}to{transform:translateY(var(--fp))}}
.slam{animation:slam .45s cubic-bezier(.2,1.6,.4,1) var(--at) both} @keyframes slam{from{opacity:0;transform:scale(2.4)}to{opacity:1;transform:none}}
.ringin{animation:ringin .5s cubic-bezier(.16,1,.3,1) var(--at) both} @keyframes ringin{from{opacity:0;transform:scale(1.4)}to{opacity:1;transform:none}}
.press{animation:press .35s ease var(--at) both} @keyframes press{0%{transform:scale(1)}40%{transform:scale(.78)}100%{transform:scale(1)}}
.flash{animation:flash .6s ease var(--at) both} @keyframes flash{0%{box-shadow:0 0 0 0 rgba(226,98,43,.7)}100%{box-shadow:0 0 0 40px rgba(226,98,43,0)}}
.gone{animation:gone .45s cubic-bezier(.5,0,.75,0) var(--at) both} @keyframes gone{from{opacity:1;transform:none}to{opacity:0;transform:translate(var(--tx),var(--ty)) scale(.3)}}
.cap{opacity:0;animation:capvis var(--d) linear var(--s) none} @keyframes capvis{from,to{opacity:1}}
.capin{animation:capin .22s cubic-bezier(.34,1.56,.64,1) var(--at) both} @keyframes capin{from{transform:scale(.85)}to{transform:none}}
.kw{color:#b9b0a7;animation:kwon .05s linear var(--at) both,kwoff .12s linear var(--to) both}
@keyframes kwon{to{color:#e2622b}} @keyframes kwoff{to{color:#16110f}}
"""

SEEK_JS = """window.__seek = async (t) => { for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; }
  const vs = [...document.querySelectorAll('video.fvclip')];
  await Promise.all(vs.map(v => { const d = v.duration || 1e9;
    const lt = Math.max(0, Math.min(d - 0.04, (t - +v.dataset.at) + +v.dataset.start));
    if (Math.abs(v.currentTime - lt) < 0.002) return null;
    return new Promise(r => { v.addEventListener('seeked', r, {once: true}); v.currentTime = lt; setTimeout(r, 3000); }); })); };
window.__ready = async () => { await document.fonts.ready; const vs = [...document.querySelectorAll('video.fvclip')];
  await Promise.all(vs.map(v => v.readyState >= 2 ? null : new Promise(r => { v.addEventListener('loadeddata', r, {once: true}); setTimeout(r, 8000); }))); };"""


# ----------------------------------------------------------------------------- LOOK 2: "cinema" — para o vídeo não parecer
# sempre o mesmo modelo. Footage-first, dark warm palette, serif display +
# mono labels, subtitle captions (no pill), light-leak cuts, letterbox. Use Video(..., look="cinema") with bg "film" | "warm" | "ink".
CINEMA_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;1,9..144,400&family=Inter+Tight:wght@400;600;800&family=JetBrains+Mono:wght@500;700&display=block');
.film{background:#060505} .warm{background:radial-gradient(ellipse at 70% 30%,#3b2a17 0%,#16110c 55%,#0b0907 100%)}
.ink{background:radial-gradient(ellipse at 30% 70%,#1d1f24 0%,#0c0d10 70%)}
.filmin{animation:filmin .55s ease var(--at) both} @keyframes filmin{from{opacity:0;filter:brightness(1.8) saturate(.6)}to{opacity:1;filter:none}}
.leak{position:absolute;inset:-20%;pointer-events:none;mix-blend-mode:screen;background:radial-gradient(ellipse at 20% 40%,rgba(255,170,80,.55),transparent 45%),radial-gradient(ellipse at 85% 70%,rgba(255,120,60,.35),transparent 40%);
  opacity:0;animation:leak .9s ease var(--at) both;z-index:60} @keyframes leak{0%{opacity:0;transform:translateX(-8%)}30%{opacity:1}100%{opacity:0;transform:translateX(8%)}}
.lbox{position:absolute;left:0;right:0;height:64px;background:#000;z-index:40}
.slide{animation:slide .7s cubic-bezier(.16,1,.3,1) var(--at) both} @keyframes slide{from{opacity:0;transform:translateX(-40px)}to{opacity:1;transform:none}}
.draw{stroke-dasharray:1000;stroke-dashoffset:1000;animation:draw .7s ease var(--at) forwards} @keyframes draw{to{stroke-dashoffset:0}}
.kb{animation:kb var(--d) linear var(--at) both} @keyframes kb{from{transform:scale(1.0)}to{transform:scale(var(--ks,1.08))}}
.sub{opacity:0;animation:capvis var(--d) linear var(--s) none}
.sw{color:rgba(255,255,255,.55);animation:swon .05s linear var(--at) both} @keyframes swon{to{color:#fff}}
.amb{color:#ffb547}
"""


def captions_cinema(words, s, e, y=968):
    """Subtitle-style captions: centred white serif-free text with soft shadow, words brighten as spoken; amber on numbers."""
    out = []
    chunks = caption_chunks(words, max_words=5)
    for ci, ch in enumerate(chunks):
        c0 = ch[0][1]
        if not (s <= c0 < e): continue
        c1 = chunks[ci + 1][0][1] if ci + 1 < len(chunks) else ch[-1][2] + 0.8
        c1 = min(c1, e)
        sp = " ".join(f"<span class='sw{' amb' if any(x.isdigit() for x in w) else ''}' style='--at:{ms(a)}'>{_h.escape(w)}</span>" for w, a, b in ch)
        out.append(f"<div class='sub' style='--s:{ms(c0)};--d:{ms(c1 - c0)};position:absolute;left:0;right:0;top:{y}px;text-align:center;z-index:70;"
                   f"font:600 40px \"Inter Tight\";letter-spacing:-.01em;text-shadow:0 2px 12px rgba(0,0,0,.9),0 0 2px #000'>{sp}</div>")
    return "".join(out)


# ----------------------------------------------------------------------------- LOOK 3: "ledger" (cara de notas de versão).
# Release-notes / blueprint feel: warm PAPER with a faint grid ↔ deep NAVY with a dot grid, one LIME statement card ~1/min.
# Space Grotesk display, IBM Plex Mono labels, Instrument Serif italic accents. *word* = lime highlighter swipe on paper,
# lime ink on navy. Captions = lower-left terminal line ("›" + words typing in + caret). Cuts = a lime bar wipes across.
# Use Video(..., look="ledger") with bg "paper" | "navy" | "lime". Pieces in templates/pieces_ledger.py.
LEDGER_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=IBM+Plex+Mono:wght@500;700&family=Instrument+Serif:ital@1&display=block');
.paper{background:#f3efe6;background-image:linear-gradient(rgba(13,19,48,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(13,19,48,.055) 1px,transparent 1px);background-size:48px 48px}
.navy{background:radial-gradient(ellipse at 50% 30%,#1b2550 0%,#0d1330 60%,#080c20 100%)}
.navy:before{content:'';position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.09) 1.2px,transparent 1.3px);background-size:32px 32px}
.lime{background:#d4ff3a}
.paper .k{color:#0d1330;background:linear-gradient(#d4ff3a,#d4ff3a) no-repeat 0 82%/0% 46%;animation:hl .45s ease var(--hl,0s) both;padding:0 .08em}
@keyframes hl{to{background-size:100% 46%}}
.navy .k{color:#d4ff3a} .lime .k{color:#0d1330;text-decoration:underline;text-decoration-thickness:6px;text-underline-offset:8px}
.wipe{position:absolute;top:0;bottom:0;width:260px;left:-300px;background:#d4ff3a;z-index:80;animation:wipe .5s cubic-bezier(.7,0,.3,1) var(--at) both}
@keyframes wipe{from{transform:translateX(0)}to{transform:translateX(2500px)}}
.ledin{animation:ledin .5s cubic-bezier(.16,1,.3,1) var(--at) both} @keyframes ledin{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
.lslide{animation:lslide .5s cubic-bezier(.16,1,.3,1) var(--at) both} @keyframes lslide{from{opacity:0;transform:translateX(-60px)}to{opacity:1;transform:none}}
.ldrop{animation:ldrop .55s cubic-bezier(.34,1.4,.64,1) var(--at) both} @keyframes ldrop{from{opacity:0;transform:translateY(-70px)}to{opacity:1;transform:none}}
.lt{opacity:0;animation:capvis var(--d) linear var(--s) none}
.tw{display:inline-block;opacity:0;animation:twin .01s linear var(--at) both} @keyframes twin{to{opacity:1}}
.caret{display:inline-block;width:16px;height:34px;background:#d4ff3a;vertical-align:-6px;margin-left:8px;animation:blink 1s steps(1) 0s infinite}
@keyframes blink{50%{opacity:0}}
.marker{position:absolute;background:rgba(212,255,58,.55);mix-blend-mode:multiply;border-radius:4px;transform-origin:left;animation:mk .45s ease var(--at) both}
@keyframes mk{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.count{font-variant-numeric:tabular-nums}
"""


def captions_ledger(words, s, e, x=110, y=950):
    """Terminal-line captions, lower left: '›' prompt, words appear as spoken, lime caret. Numbers in lime."""
    out = []
    chunks = caption_chunks(words, max_words=4)
    for ci, ch in enumerate(chunks):
        c0 = ch[0][1]
        if not (s <= c0 < e): continue
        c1 = chunks[ci + 1][0][1] if ci + 1 < len(chunks) else ch[-1][2] + 0.8
        c1 = min(c1, e)
        sp = " ".join(f"<span class='tw' style='--at:{ms(a)};{'color:#d4ff3a' if any(x.isdigit() for x in w) else ''}'>{_h.escape(w)}</span>" for w, a, b in ch)
        out.append(f"<div class='lt' style='--s:{ms(c0)};--d:{ms(c1 - c0)};position:absolute;left:{x}px;top:{y}px;z-index:70'>"
                   f"<div style='display:inline-block;background:rgba(9,13,34,.92);color:#fff;font:700 36px IBM Plex Mono;padding:12px 26px 14px;"
                   f"border-radius:12px;border:2px solid rgba(212,255,58,.35);white-space:nowrap;box-shadow:0 12px 30px rgba(0,0,0,.25)'>"
                   f"<span style='color:#d4ff3a'>›</span> {sp}<span class='caret'></span></div></div>")
    return "".join(out)


# ----------------------------------------------------------------------------- tema INEMA (padrão)
# Aplicado na página final de cada cena: troca as cores e fontes fixas do kit de base pelas do DESIGN.md INEMA
# (amarelo #FACC15, preto #0c0c10, títulos Sora, corpo Inter, código JetBrains Mono; sem serifa e sem condensada).
_THEME_MAP = [
    ("#e2622b", "#FACC15"), ("#E2622B", "#FACC15"), ("rgba(226,98,43", "rgba(250,204,21"), ("#ee7a45", "#FDE047"),
    ("#fbe3d6", "#FEF9C3"),
    ("#f8f4ee", "#fafaf7"), ("#efe8df", "#f2f1ec"), ("#e6ddd2", "#e4e3dd"), ("#f4efe9", "#f1f1ee"), ("#f3f1ee", "#f1f1ee"),
    ("#3a2c26", "#22222a"), ("#1b1513", "#0c0c10"), ("#120d0c", "#060608"), ("#16110f", "#0c0c10"), ("#241c19", "#17171d"),
    ("#3b302b", "#2a2a33"), ("#8a817a", "#6b6b75"), ("#b9b0a7", "#8b8b94"), ("#6b625b", "#5b5b66"), ("#e3ddd6", "#deded9"),
    ("border:2px solid rgba(0,0,0,.08)", "border:2px solid rgba(255,255,255,.18)"),
    ("#ffb547", "#FACC15"), ("#d4ff3a", "#FACC15"), ("rgba(212,255,58", "rgba(250,204,21"), ("#f3efe6", "#f2f1ec"),
    ("Inter Tight", "Inter"), ("Manrope", "Inter"), ("'Instrument Serif'", "Sora"), ("Instrument Serif", "Sora"),
    ("Fraunces", "Sora"), ("Space Grotesk", "Sora"), ("IBM Plex Mono", "JetBrains Mono"),
]
_THEME_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=block');
.sf{font-family:Sora!important;font-style:normal!important;font-weight:800!important;letter-spacing:-.02em}
.dark .k,.dark .sf,.film .k,.warm .k,.ink .k,.navy .k{color:#FACC15}
.cream .k,.cream .sf,.paper .sf{color:inherit;background:linear-gradient(transparent 58%,#FACC15 58%);padding:0 .06em}
.orange .k,.orange .sf,.acc .k,.lime .k{color:#1a1206;background:none;text-decoration:underline;text-decoration-thickness:6px;text-underline-offset:8px}
.cream{background:radial-gradient(ellipse at 50% 35%,#fafaf7 0%,#f2f1ec 60%,#e7e6e0 100%)}
.dark{background:radial-gradient(ellipse at 50% 38%,#1d1d24 0%,#0c0c10 62%,#060608 100%)}
@keyframes kwon{to{color:#FACC15}} @keyframes kwoff{to{color:#ffffff}}
"""
def _sora(m):
    size = round(int(m.group(2)) * 0.8)       # Sora é mais larga que a condensada original
    return f"font:800 {size}px{m.group(3) or ''} Sora"
def inema_theme(h):
    for a, b in _THEME_MAP: h = h.replace(a, b)
    h = re.sub(r"font:(\d+) (\d+)px(/[\d.]+)? Anton", _sora, h)
    h = h.replace("Anton", "Sora")
    return h.replace("</head>", f"<style>{_THEME_CSS}</style></head>", 1)


def _loudnorm2(audio, I=-14, TP=-1.5, LRA=11):
    """Compressor leve + loudnorm em 2 passadas (1 passada fica ~2 LU abaixo; o pico da voz sintética segura o ganho)."""
    pre = "acompressor=threshold=0.1:ratio=4:attack=3:release=100,alimiter=limit=0.8"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", audio, "-af", f"{pre},loudnorm=I={I}:TP={TP}:LRA={LRA}:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    return (f"{pre},loudnorm=I={I}:TP={TP}:LRA={LRA}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
            f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")


class Video:
    def __init__(self, job, name="final", look="reel"):
        self.look = look
        self.job, self.name = job, name
        self.words = [tuple(w) for w in json.load(open(os.path.join(job, "words.json")))]
        self.scenes = []
        self.out = os.path.join(job, "out"); os.makedirs(self.out, exist_ok=True)

    def scene(self, s, e, bg, body, caps=True, whoosh=True):
        """bg: 'cream' | 'dark' | 'orange' (use big_card for orange)."""
        self.scenes.append(dict(s=s, e=e, bg=bg, body=body, caps=caps, whoosh=whoosh))

    def html(self, sc):
        h = self._html(sc)
        return inema_theme(h) if THEME == "inema" else h

    def _html(self, sc):
        if self.look == "cinema":
            cap = captions_cinema(self.words, sc["s"], sc["e"]) if sc["caps"] else ""
            return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CINEMA_CSS}</style><style>{CSS}</style></head><body>"
                    f"<div class='stage {sc['bg']}'><div class='stage filmin' style='--at:{ms(sc['s'])}'>{sc['body']}</div>"
                    f"<div class='leak' style='--at:{ms(sc['s'] - 0.25)}'></div>{cap}</div><script>{SEEK_JS}</script></body></html>")
        if self.look == "ledger":
            cap = captions_ledger(self.words, sc["s"], sc["e"]) if sc["caps"] else ""
            return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style><style>{LEDGER_CSS}</style></head><body>"
                    f"<div class='stage {sc['bg']}'><div class='stage ledin' style='--at:{ms(sc['s'])}'>{sc['body']}</div>"
                    f"<div class='wipe' style='--at:{ms(sc['s'] - 0.3)}'></div>{cap}</div><script>{SEEK_JS}</script></body></html>")
        cls = {"cream": "cream", "dark": "dark", "orange": "orange"}[sc["bg"]]
        cap = captions(self.words, sc["s"], sc["e"]) if sc["caps"] else ""
        return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
                f"<div class='stage {cls}'><div class='stage scenein' style='--at:{ms(sc['s'])}'>"
                f"<div class='stage drift' style='--at:{ms(sc['s'])};--d:{ms(sc['e'] - sc['s'])}'>{sc['body']}</div></div>{cap}</div>"
                f"<script>{SEEK_JS}</script></body></html>")

    def write_pages(self):
        pdir = os.path.join(self.out, os.environ.get("FV_PAGES", "pages")); os.makedirs(pdir, exist_ok=True)
        paths = []
        for i, sc in enumerate(self.scenes):
            p = os.path.join(pdir, f"s{i:03d}.html"); open(p, "w").write(self.html(sc)); paths.append(p)
        return paths

    def stills(self, times=None, out="stills.jpg"):
        """Contact sheet: middle + end of every scene (or given times). Look at it before rendering."""
        from playwright.sync_api import sync_playwright
        pages = self.write_pages()
        if times is None:
            times = []
            for sc in self.scenes:
                d = sc["e"] - sc["s"]
                times += [sc["s"] + d * .45, sc["e"] - .12]
        shots = []
        with sync_playwright() as pw:
            br = pw.chromium.launch(); pg = br.new_page(viewport={"width": W, "height": H})
            cur = None
            for t in times:
                i = max((k for k, sc in enumerate(self.scenes) if sc["s"] <= t + 1e-6 < sc["e"] + 1e-6), key=lambda k: self.scenes[k]["s"])
                if cur != i:
                    pg.goto("file://" + pages[i]); pg.wait_for_load_state("networkidle"); pg.evaluate("__ready()"); pg.wait_for_timeout(300); cur = i
                pg.evaluate(f"__seek({t})"); pg.wait_for_timeout(40)
                f = os.path.join(self.out, f"_st_{os.getpid()}_{len(shots):03d}.jpg"); pg.screenshot(path=f, type="jpeg", quality=80); shots.append(f)
            br.close()
        cols = 4; rows = math.ceil(len(shots) / cols)
        from PIL import Image
        sheet = Image.new("RGB", (cols * 480, rows * 270), "black")
        for k, f in enumerate(shots):
            sheet.paste(Image.open(f).resize((480, 270)), ((k % cols) * 480, (k // cols) * 270)); os.remove(f)
        p = os.path.join(self.out, out); sheet.save(p, quality=85); return p

    # ---- render
    def _render_chunk(self, args):
        page, f0, f1, seg = args
        from playwright.sync_api import sync_playwright
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                               "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", "-r", str(FPS), seg],
                              stdin=subprocess.PIPE)
        with sync_playwright() as pw:
            br = pw.chromium.launch(); pg = br.new_page(viewport={"width": W, "height": H})
            pg.goto("file://" + page); pg.wait_for_load_state("networkidle"); pg.evaluate("__ready()"); pg.wait_for_timeout(400)
            for f in range(f0, f1):
                pg.evaluate(f"__seek({f / FPS})")
                ff.stdin.write(pg.screenshot(type="jpeg", quality=93))
            br.close()
        ff.stdin.close(); ff.wait()
        return seg

    def render(self, workers=None, tail=0.7):
        pages = self.write_pages()
        self.scenes[-1]["e"] = max(self.scenes[-1]["e"], self.words[-1][2] + tail)
        segdir = os.path.join(self.out, "segs"); shutil.rmtree(segdir, ignore_errors=True); os.makedirs(segdir)
        tasks = []
        for i, sc in enumerate(self.scenes):
            f0, f1 = round(sc["s"] * FPS), round(sc["e"] * FPS)
            step = FPS * 4                      # 4-second chunks so long scenes parallelise
            for a in range(f0, f1, step):
                tasks.append((pages[i], a, min(f1, a + step), os.path.join(segdir, f"{i:03d}_{a:07d}.mp4")))
        workers = workers or max(2, min(8, (os.cpu_count() or 4) - 2))
        with cf.ProcessPoolExecutor(workers) as ex:
            segs = list(ex.map(self._render_chunk, tasks))
        lst = os.path.join(segdir, "list.txt")
        open(lst, "w").write("".join(f"file '{s}'\n" for s in sorted(segs)))
        silent = os.path.join(self.out, "video_silent.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
        return self.mix(silent)

    def mix(self, silent):
        """Voz (loudnorm -14 LUFS, pico -1,5). Trilha opcional: <job>/music.mp3 a -26 dB. Whoosh só com FV_WHOOSH=1."""
        sfx = os.path.join(SKILL, "sfx", "whoosh.wav")
        ins, flt, n = ["-i", silent, "-i", os.path.join(self.job, "vo.mp3")], [], 2
        flt.append(f"[1:a]{_loudnorm2(os.path.join(self.job, 'vo.mp3'))},aresample=48000,apad[vo]")
        mixes = ["[vo]"]
        # Padrão INEMA: sem som de movimento de tela (só voz + trilha baixa). FV_WHOOSH=1 liga o whoosh nos cortes.
        cuts = [sc["s"] for sc in self.scenes[1:] if sc["whoosh"]] if os.environ.get("FV_WHOOSH") == "1" else []
        for k, t in enumerate(cuts):
            ins += ["-i", sfx]; d = int(max(0, t - 0.12) * 1000)
            flt.append(f"[{n}:a]volume=0.32,adelay={d}|{d},aresample=48000[w{k}]"); mixes.append(f"[w{k}]"); n += 1
        music = os.path.join(self.job, "music.mp3")
        if os.path.exists(music):
            ins += ["-stream_loop", "-1", "-i", music]
            flt.append(f"[{n}:a]volume=-26dB,aresample=48000[mu]"); mixes.append("[mu]"); n += 1
        flt.append(f"{''.join(mixes)}amix=inputs={len(mixes)}:normalize=0:duration=first[a]")
        final = os.path.join(self.out, f"{self.name}.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(flt), "-map", "0:v", "-map", "[a]",
                        "-c:v", "libx264", "-preset", "slow", "-b:v", "12M", "-minrate", "12M", "-maxrate", "12M", "-bufsize", "24M",
                        "-x264-params", "nal-hrd=cbr", "-r", str(FPS), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", f"{self.scenes[-1]['e']:.3f}", "-movflags", "+faststart", final], check=True)
        return final
