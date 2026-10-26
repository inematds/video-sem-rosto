"""LOOK 2 "cinema" pieces — footage-first (imagem real primeiro). Use with Video(..., look="cinema").
Backgrounds: "film" (black, under full-bleed footage), "warm" (graphite + amber glow), "ink" (cool graphite).
Type: Fraunces serif display (_word_ = amber italic), JetBrains Mono labels, Inter Tight body. No pills, no clay renders.
All times absolute seconds. Every footage use: short (≈3–8 s), credited, muted under the voiceover."""
import os, html as _h, re
from fv import *
from fv import _uid

AMBER, PAPER, DIM = "#ffb547", "#f4ede4", "rgba(244,237,228,.62)"


def ser(s):
    """_word_ -> amber italic; *word* -> amber upright."""
    s = _h.escape(str(s))
    s = re.sub(r"_(.+?)_", rf"<i style='color:{AMBER};font-style:italic'>\1</i>", s)
    return re.sub(r"\*(.+?)\*", rf"<span style='color:{AMBER}'>\1</span>", s)


def footage(src, at, dur, start=0.0, credit="Imagem oficial · @conta", ks=1.07, letterbox=True, dim=0.0,
            x=0, y=0, w=1920, h=1080, origin="50% 50%"):
    """Full-bleed (or framed-region) real footage with a slow Ken Burns push, optional letterbox and darkening.
    The clip plays from `start`s of the source at time `at`."""
    wb = prep_clip(src)
    vid = (f"<video class='fvclip' data-at='{at}' data-start='{start}' src='file://{wb}' muted playsinline preload='auto' "
           f"style='width:100%;height:100%;object-fit:cover;display:block'></video>")
    shade = f"<div style='position:absolute;inset:0;background:rgba(0,0,0,{dim})'></div>" if dim else ""
    vign = "<div style='position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,transparent 55%,rgba(0,0,0,.55) 100%)'></div>"
    lb = ("<div class='lbox' style='top:0'></div><div class='lbox' style='bottom:0'></div>" if letterbox else "")
    cr = (f"<div class='slide' style='--at:{ms(at + .3)};position:absolute;left:{x + 48}px;top:{y + (84 if letterbox else 28)}px;z-index:45;"
          f"font:700 17px \"JetBrains Mono\";letter-spacing:.08em;text-transform:uppercase;color:{DIM}'>▶ {_h.escape(credit)}</div>" if credit else "")
    return (f"<div style='position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;overflow:hidden'>"
            f"<div class='kb' style='--at:{ms(at)};--d:{ms(dur)};--ks:{ks};position:absolute;inset:0;transform-origin:{origin}'>{vid}</div>"
            f"{shade}{vign}</div>{lb}{cr}")


def pip(src, at, x, y, w, start=0.0, credit="Oficial · @conta", aspect=16 / 9, tilt=0):
    """Framed smaller clip (thin warm border, soft shadow) — for side-by-side with text/pages."""
    wb = prep_clip(src); h = w / aspect
    return (f"<div class='slide' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;width:{w}px;transform:rotate({tilt}deg)'>"
            f"<div style='border:1px solid rgba(255,181,71,.45);border-radius:10px;overflow:hidden;box-shadow:0 40px 90px rgba(0,0,0,.6)'>"
            f"<video class='fvclip' data-at='{at}' data-start='{start}' src='file://{wb}' muted playsinline preload='auto' "
            f"style='width:{w}px;height:{h:.0f}px;object-fit:cover;display:block'></video></div>"
            f"<div style='margin-top:12px;font:700 15px \"JetBrains Mono\";letter-spacing:.08em;text-transform:uppercase;color:{DIM}'>▶ {_h.escape(credit)}</div></div>")


def chapter(num, name, at, x=110, y=120):
    """Chapter marker: '02 —' amber mono + serif section name."""
    return (f"<div class='slide' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;z-index:50'>"
            f"<div style='font:700 20px \"JetBrains Mono\";color:{AMBER};letter-spacing:.14em'>{num:02d} —</div>"
            f"<div style='font:300 64px/1.05 Fraunces;color:{PAPER};letter-spacing:-.02em;margin-top:8px;text-shadow:0 4px 30px rgba(0,0,0,.6)'>{ser(name)}</div></div>")


def display(text, at, x=110, y=360, size=120, width=1500, align="left", per_line=None):
    """Big editorial serif statement (lines split on '|'), each line lands at its time."""
    lines = text.split("|")
    out = []
    for i, ln in enumerate(lines):
        t = per_line[i] if per_line and i < len(per_line) else at + i * .35
        out.append(f"<div class='rise' style='--at:{ms(t)}'>{ser(ln)}</div>")
    return (f"<div style='position:absolute;left:{x}px;top:{y}px;width:{width}px;text-align:{align};z-index:50;font:300 {size}px/1.02 Fraunces;"
            f"letter-spacing:-.035em;color:{PAPER};text-shadow:0 6px 40px rgba(0,0,0,.65)'>{''.join(out)}</div>")


def callout(label, sub, at, px, py, tx, ty):
    """Leader line from a point ON THE FOOTAGE (px,py) to a mono label at (tx,ty). Dot pulses at the point."""
    uid = next(_uid); side = "start" if tx > px else "end"
    lx = tx - 8 if tx > px else tx + 8
    svg = (f"<svg style='position:absolute;left:0;top:0;z-index:48' width='1920' height='1080'>"
           f"<circle cx='{px}' cy='{py}' r='7' fill='{AMBER}' class='pop' style='--at:{ms(at)};transform-origin:{px}px {py}px'/>"
           f"<circle cx='{px}' cy='{py}' r='16' fill='none' stroke='{AMBER}' stroke-width='2' opacity='.6' class='pop' style='--at:{ms(at + .1)};transform-origin:{px}px {py}px'/>"
           f"<path d='M{px},{py} L{(px + tx) / 2:.0f},{ty} L{lx},{ty}' fill='none' stroke='{AMBER}' stroke-width='2' class='draw' style='--at:{ms(at + .1)}'/></svg>")
    anchor = "" if tx > px else "transform:translateX(-100%);text-align:right;"
    lab = (f"<div class='fade' style='--at:{ms(at + .45)};position:absolute;left:{tx}px;top:{ty - 26}px;{anchor}z-index:49;white-space:nowrap'>"
           f"<div style='font:700 22px \"JetBrains Mono\";letter-spacing:.1em;text-transform:uppercase;color:{PAPER}'>{_h.escape(label)}</div>"
           f"<div style='font:italic 400 26px Fraunces;color:{AMBER}'>{_h.escape(sub)}</div></div>")
    return svg + lab


def spec(rows, at, x=1180, y=230, w=620, step=.45, times=None):
    """Data-sheet panel: mono label left, value right, rows appear on their spoken beats."""
    out = []
    for i, (k, v) in enumerate(rows):
        t = times[i] if times and i < len(times) else at + i * step
        out.append(f"<div class='slide' style='--at:{ms(t)};display:flex;justify-content:space-between;padding:16px 0;border-bottom:1px solid rgba(244,237,228,.16)'>"
                   f"<span style='font:700 18px \"JetBrains Mono\";letter-spacing:.1em;text-transform:uppercase;color:{DIM}'>{_h.escape(k)}</span>"
                   f"<span style='font:600 28px \"Inter Tight\";color:{PAPER}'>{ser(v)}</span></div>")
    return (f"<div style='position:absolute;left:{x}px;top:{y}px;width:{w}px;z-index:50;background:rgba(12,10,8,.72);backdrop-filter:blur(6px);"
            f"padding:22px 30px;border:1px solid rgba(255,181,71,.25);border-radius:6px'>{''.join(out)}</div>")


def tagline(text, at, x=110, y=860, size=34):
    """Small lower-left editorial line (mono kicker feel) — sits above the subtitles."""
    return (f"<div class='slide' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;z-index:50;font:600 {size}px \"Inter Tight\";"
            f"color:{PAPER};text-shadow:0 2px 16px rgba(0,0,0,.8)'>{ser(text)}</div>")


def code_file(name, lines, at, x, y, w=760, step=.3):
    """A real-looking file view (SKILL.md / SOUL.md / SAFETY.md) — dark editor, lines type in."""
    rows = "".join(f"<div class='fade' style='--at:{ms(at + .3 + i * step)};white-space:pre'>{_h.escape(l)}</div>" for i, l in enumerate(lines))
    return (f"<div class='slide' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;width:{w}px;z-index:50;background:#0d0c0b;"
            f"border:1px solid rgba(244,237,228,.14);border-radius:10px;box-shadow:0 40px 90px rgba(0,0,0,.6);overflow:hidden'>"
            f"<div style='padding:12px 18px;border-bottom:1px solid rgba(244,237,228,.1);font:700 17px \"JetBrains Mono\";color:{AMBER}'>{_h.escape(name)}</div>"
            f"<div style='padding:18px 22px;font:500 21px/1.6 \"JetBrains Mono\";color:{PAPER}'>{rows}</div></div>")


def darkpage(img, at, x, y, w, h, scroll=(), url="", page_w=2400):
    """Real page screencast in a dark minimal frame."""
    return browser(img, at, x, y, w, h, scroll=scroll, url=url, page_w=page_w)
