"""LOOK 3 "ledger" pieces (cara de notas de versão). Use with Video(..., look="ledger"); bgs "paper" | "navy" | "lime".
All times are absolute voiceover seconds. dark=True when the scene bg is navy.
Palette: NAVY #0d1330, PAPER #f3efe6, LIME #d4ff3a, MERGE purple #8250df. Fonts: Space Grotesk / IBM Plex Mono / Instrument Serif."""
from fv import *
from fv import _uid, _wordlist, _h
import html as _hm
__all__ = [n for n in dir() if not n.startswith('__')] + ['_h', '_uid']

NAVY, PAPER, LIME, MERGE = "#0d1330", "#f3efe6", "#d4ff3a", "#8250df"
SG, MONO = "Space Grotesk", "IBM Plex Mono"


def lhead(text, at, x=110, y=110, size=96, dark=False, align="left", width=1700, per_word=None, color=None):
    """Space Grotesk headline; words rise one by one; *word* gets a lime highlighter swipe (paper) / lime ink (navy)."""
    color = color or ("#fff" if dark else NAVY)
    out = []
    for i, w in enumerate(_wordlist(text)):
        t = per_word[i] if per_word and i < len(per_word) else at + i * 0.06
        out.append(f"<span class='rise' style='--at:{ms(t)};--hl:{ms(t + .25)};display:inline-block'>{w}</span>")
    return (f"<div style='position:absolute;left:{x}px;top:{y}px;width:{width}px;text-align:{align};font:700 {size}px/1.04 {SG};"
            f"letter-spacing:-.035em;color:{color}'>{' '.join(out)}</div>")


def mono(text, at, x, y, dark=False, size=24, dot=True, anchor="left"):
    """Mono label tag, e.g. 'CHANGELOG · OCT 22' / 'github.com/dono/repo'. Lime dot in front."""
    fg = "#c9cfe6" if dark else "#3a4060"
    d = f"<i style='width:12px;height:12px;border-radius:50%;background:{LIME};box-shadow:0 0 0 3px {NAVY if not dark else 'rgba(212,255,58,.25)'};margin-right:14px'></i>" if dot else ""
    tx = {"left": "0", "center": "-50%", "right": "-100%"}[anchor]
    return (f"<div style='position:absolute;left:{x}px;top:{y}px;transform:translateX({tx})'><div class='lslide' style='--at:{ms(at)}'>"
            f"<div style='display:flex;align-items:center;font:700 {size}px {MONO};letter-spacing:.08em;text-transform:uppercase;color:{fg};white-space:nowrap'>{d}{_h.escape(text)}</div></div></div>")


def merged(at, x, y, label="Merged", size=26):
    """GitHub-style purple 'Merged' pill with the merge glyph."""
    return (f"<div class='pop' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px'><div style='display:flex;align-items:center;gap:10px;"
            f"background:{MERGE};color:#fff;font:700 {size}px {SG};padding:10px 20px;border-radius:99px;white-space:nowrap'>{icon('git-merge', '#fff', size + 4)}<span>{_h.escape(label)}</span></div></div>")


def counter(n, at, x, y, size=260, dur=1.3, dark=False, suffix="", anchor="left", color=None):
    """Odometer: every digit rolls up from 0 to its value, landing at at+dur."""
    color = color or ("#fff" if dark else NAVY)
    s = str(n); cols = []
    for i, ch in enumerate(s):
        if not ch.isdigit():
            cols.append(f"<span>{_h.escape(ch)}</span>"); continue
        uid = next(_uid); d = int(ch); laps = 10 * (1 + len(s) - i) + d
        stack = "".join(f"<div style='height:{size}px'>{k % 10}</div>" for k in range(laps + 1))
        cols.append(f"<style>@keyframes od{uid}{{from{{transform:translateY(0)}}to{{transform:translateY(-{laps * size}px)}}}}"
                    f".od{uid}{{animation:od{uid} {dur + i * .08:.2f}s cubic-bezier(.2,.7,.2,1) {at:.3f}s both}}</style>"
                    f"<span style='display:inline-block;height:{size}px;overflow:hidden;vertical-align:top'><div class='od{uid}'>{stack}</div></span>")
    tx = {"left": "0", "center": "-50%", "right": "-100%"}[anchor]
    suf = f"<span style='font-size:.42em;margin-left:.15em;vertical-align:top;line-height:{size * 1.05}px'>{em(suffix)}</span>" if suffix else ""
    return (f"<div class='fade' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;transform:translateX({tx});font:700 {size}px/1 {SG};"
            f"letter-spacing:-.05em;color:{color};white-space:nowrap' ><span class='count'>{''.join(cols)}</span>{suf}</div>")


def loglist(items, x, y, w=1100, dark=False, gap=16, size=32):
    """Changelog rows sliding in: items = [(text, t, tag)] with tag in feat|fix|plugin|desktop|security|core."""
    tags = {"feat": ("#1f883d", "feat"), "fix": ("#cf222e", "fix"), "plugin": (MERGE, "plugin"), "desktop": ("#0969da", "desktop"),
            "security": ("#bf8700", "security"), "core": ("#57606a", "core")}
    bg, fg, line = ("rgba(255,255,255,.06)", "#fff", "rgba(255,255,255,.12)") if dark else ("#fff", NAVY, "rgba(13,19,48,.10)")
    rows = []
    for i, (tx, t, tg) in enumerate(items):
        c, lab = tags.get(tg, ("#57606a", tg))
        hsh = f"{abs(hash(tx)) % 0xfffffff:07x}"
        rows.append(f"<div class='lslide' style='--at:{ms(t)};display:flex;align-items:center;gap:20px;background:{bg};border:1px solid {line};"
                    f"border-radius:14px;padding:16px 22px;margin-bottom:{gap}px;box-shadow:0 8px 24px rgba(0,0,0,.08)'>"
                    f"<span style='font:700 20px {MONO};color:{'#8f97b8' if dark else '#7a7f99'}'>{hsh}</span>"
                    f"<span style='font:700 18px {MONO};color:#fff;background:{c};padding:5px 12px;border-radius:8px;text-transform:uppercase;letter-spacing:.06em'>{lab}</span>"
                    f"<span style='font:600 {size}px {SG};color:{fg};letter-spacing:-.015em'>{em(tx)}</span></div>")
    return f"<div style='position:absolute;left:{x}px;top:{y}px;width:{w}px'>{''.join(rows)}</div>"


def marker(at, x, y, w, h):
    """Lime highlighter swipe over a line of a screencast (frame px)."""
    return f"<div class='marker' style='--at:{ms(at)};left:{x}px;top:{y}px;width:{w}px;height:{h}px;z-index:30'></div>"


def pcard(name, line, tier, at, x, y, w=540, ico="puzzle", dark=False):
    """Plugin catalog card: icon, name (mono), one line, tier badge (OFFICIAL / LABS / COMMUNITY)."""
    tc = {"OFFICIAL": (LIME, NAVY), "LABS": ("#ffd166", NAVY), "COMMUNITY": ("#c9cfe6", NAVY), "MCP": ("#9be7ff", NAVY)}.get(tier, (LIME, NAVY))
    bg, fg, sub = ("#141c42", "#fff", "#b9c0dc") if dark else ("#fff", NAVY, "#4a5070")
    return (f"<div class='ldrop' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;width:{w}px'><div style='background:{bg};border-radius:20px;"
            f"padding:26px 28px;box-shadow:0 18px 50px rgba(0,0,0,.18);border:1px solid {'rgba(255,255,255,.1)' if dark else 'rgba(13,19,48,.08)'}'>"
            f"<div style='display:flex;align-items:center;gap:16px'><div style='width:58px;height:58px;border-radius:14px;background:{NAVY if not dark else LIME};"
            f"display:flex;align-items:center;justify-content:center'>{icon(ico, LIME if not dark else NAVY, 32)}</div>"
            f"<div style='font:700 32px {MONO};color:{fg};letter-spacing:-.02em'>{_h.escape(name)}</div>"
            f"<div style='margin-left:auto;font:700 16px {MONO};background:{tc[0]};color:{tc[1]};padding:6px 12px;border-radius:8px;letter-spacing:.08em;white-space:nowrap'>{tier}</div></div>"
            f"<div style='margin-top:16px;font:500 26px/1.35 {SG};color:{sub}'>{em(line)}</div></div></div>")


def statement(lines, size=150):
    """Full LIME statement card (use with bg 'lime'): lines=[(text, t)] — navy Space Grotesk, *word* underlined."""
    rows = "".join(f"<div class='rise' style='--at:{ms(t)}'>{em(tx)}</div>" for tx, t in lines)
    return (f"<div style='position:absolute;left:150px;right:150px;top:50%;transform:translateY(-58%);color:{NAVY};"
            f"font:700 {size}px/1.02 {SG};letter-spacing:-.05em'>{rows}</div>")


def version(text, at, x, y, size=210, dark=False, anchor="left"):
    """Big version label (e.g. 'v0.22.5') — outlined mono with a lime fill sweeping in."""
    col = "#fff" if dark else NAVY
    tx = {"left": "0", "center": "-50%", "right": "-100%"}[anchor]
    return (f"<div style='position:absolute;left:{x}px;top:{y}px;transform:translateX({tx})'><div class='ldrop' style='--at:{ms(at)};font:700 {size}px/1 {MONO};"
            f"letter-spacing:-.06em;color:transparent;-webkit-text-stroke:3px {col};position:relative;white-space:nowrap'>{_h.escape(text)}"
            f"<span class='ledin' style='--at:{ms(at + .35)};position:absolute;left:0;top:0;color:{LIME};-webkit-text-stroke:3px {col}'>{_h.escape(text)}</span></div></div>")


def device(src, at, x, y, w, start=0.0, credit="Demo oficial · @conta", title="App"):
    """Real footage inside a dark app-window bezel (mono title bar). Wraps fv.clip."""
    bar = (f"<div style='height:44px;background:#0b1029;display:flex;align-items:center;gap:9px;padding:0 18px;border-radius:18px 18px 0 0'>"
           + "".join(f"<i style='width:12px;height:12px;border-radius:50%;background:{c}'></i>" for c in ("#ff5f57", "#febc2e", "#28c840"))
           + f"<span style='margin-left:16px;font:700 18px {MONO};color:#9aa3c7;letter-spacing:.06em'>{_h.escape(title.upper())}</span></div>")
    return (f"<div class='heroin' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;width:{w}px;box-shadow:0 40px 90px rgba(0,0,0,.4);border-radius:18px'>"
            f"{bar}<div style='position:relative'>{clip(src, at, 0, 0, w, start=start, credit=credit, frame=False, cls='')}</div></div>")


def step(n, text, at, x, y, dark=False, w=1500):
    """Numbered step row: big mono numeral in a lime square + Space Grotesk text."""
    fg = "#fff" if dark else NAVY
    return (f"<div class='lslide' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;width:{w}px;display:flex;align-items:center;gap:28px'>"
            f"<div style='width:96px;height:96px;border-radius:20px;background:{LIME};color:{NAVY};font:700 54px {MONO};display:flex;align-items:center;justify-content:center;flex:none'>{n}</div>"
            f"<div style='font:700 52px/1.1 {SG};color:{fg};letter-spacing:-.025em'>{em(text)}</div></div>")


def arrow(at, x0, y0, x1, y1, color=LIME, width=5):
    """Leader line that draws itself, with a dot at the end."""
    L = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** .5
    return (f"<svg style='position:absolute;left:0;top:0;z-index:35' width='1920' height='1080'><path d='M{x0} {y0} L{x1} {y1}' stroke='{color}' stroke-width='{width}' "
            f"fill='none' stroke-linecap='round' style='stroke-dasharray:{L:.0f};stroke-dashoffset:{L:.0f};animation:draw .6s ease {at:.3f}s forwards'/>"
            f"<circle cx='{x1}' cy='{y1}' r='11' fill='{color}' class='pop' style='--at:{ms(at + .5)};transform-origin:{x1}px {y1}px'/></svg>"
            f"<style>@keyframes draw{{to{{stroke-dashoffset:0}}}}</style>")


# ---- telas ilustradas do app (label scenes that use these with mono("illustration", …) — the real screen isn't captured)

def panel(inner, at, x, y, w, h=None, title="Settings · Delegation", dark=False):
    """Illustrated app panel (window chrome + content)."""
    bg, fg = ("#121a3d", "#fff") if dark else ("#fff", NAVY)
    hh = f"height:{h}px;" if h else ""
    return (f"<div class='heroin' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;width:{w}px;{hh}background:{bg};color:{fg};border-radius:22px;"
            f"box-shadow:0 30px 80px rgba(0,0,0,.25);overflow:hidden;border:1px solid {'rgba(255,255,255,.1)' if dark else 'rgba(13,19,48,.1)'}'>"
            f"<div style='height:52px;display:flex;align-items:center;gap:9px;padding:0 20px;background:{'#0b1029' if dark else '#ece8de'}'>"
            + "".join(f"<i style='width:12px;height:12px;border-radius:50%;background:{c}'></i>" for c in ("#ff5f57", "#febc2e", "#28c840"))
            + f"<span style='margin-left:14px;font:700 18px {MONO};letter-spacing:.05em;opacity:.7'>{_h.escape(title)}</span></div>"
            f"<div style='padding:34px 38px'>{inner}</div></div>")


def seg(options, at, active_at=(), dark=False, size=30):
    """Segmented mode picker. active_at=[(t, index)] moves the lime selection between options."""
    uid = next(_uid); n = len(options)
    kf = ""
    if active_at:
        t0 = active_at[0][0]; t1 = active_at[-1][0]; span = max(t1 - t0, .01)
        kf = "".join(f"{(t - t0) / span * 100:.1f}%{{left:{i / n * 100:.3f}%}}" for t, i in active_at)
        kf = f"<style>@keyframes sg{uid}{{{kf}}}.sg{uid}{{animation:sg{uid} {span:.3f}s steps(1,end) {t0:.3f}s both}}</style>"
    first = active_at[0][1] if active_at else 0
    opts = "".join(f"<div style='flex:1;text-align:center;position:relative;z-index:2;font:700 {size}px {SG};padding:18px 0;mix-blend-mode:difference;color:#fff'>{_h.escape(o)}</div>" for o in options)
    return (f"{kf}<div class='pop' style='--at:{ms(at)};position:relative;display:flex;background:{'#0b1029' if dark else '#ece8de'};border-radius:16px;padding:6px'>"
            f"<div class='sg{uid}' style='position:absolute;top:6px;bottom:6px;left:{first / n * 100:.3f}%;width:calc({100 / n:.3f}% - 4px);margin-left:2px;"
            f"background:{LIME};border-radius:12px;transition:none'></div>{opts}</div>")


def route_row(left, right, at, dark=False, size=28):
    """'quick jobs  →  cheaper model' row for the model route editor."""
    bg = "#0b1029" if dark else "#f6f3ec"
    return (f"<div class='lslide' style='--at:{ms(at)};display:flex;align-items:center;gap:22px;background:{bg};border-radius:14px;padding:18px 24px;margin-top:16px'>"
            f"<span style='font:700 {size}px {SG}'>{em(left)}</span><span style='flex:1;border-top:3px dashed {LIME if dark else '#b8b3a6'}'></span>"
            f"{icon('arrow-right', LIME if dark else NAVY, 30)}<span style='font:700 {size}px {MONO};background:{LIME};color:{NAVY};padding:8px 16px;border-radius:10px'>{_h.escape(right)}</span></div>")


def cost_prompt(tool, cost, at, x, y, w=760, limit=None, dark=False):
    """Approval prompt that shows what a paid MCP tool call will cost (illustration)."""
    lim = (f"<div style='margin-top:14px;font:600 22px {MONO};opacity:.7'>Chat spend limit: {_h.escape(limit)}</div>" if limit else "")
    inner = (f"<div style='font:700 20px {MONO};letter-spacing:.08em;opacity:.65'>APPROVAL NEEDED</div>"
             f"<div style='margin-top:12px;font:700 36px {SG}'>Run <span style='font-family:{MONO}'>{_h.escape(tool)}</span>?</div>"
             f"<div style='margin-top:18px;display:flex;align-items:center;gap:14px'><span style='font:700 22px {MONO};opacity:.7'>THIS CALL COSTS</span>"
             f"<span class='slam' style='--at:{ms(at + .6)};font:700 44px {MONO};background:{LIME};color:{NAVY};padding:4px 16px;border-radius:10px'>{_h.escape(cost)}</span></div>{lim}"
             f"<div style='display:flex;gap:16px;margin-top:26px'><div style='flex:1;text-align:center;font:700 26px {SG};padding:16px;border-radius:12px;background:{NAVY if not dark else LIME};color:{LIME if not dark else NAVY}'>Allow</div>"
             f"<div style='flex:1;text-align:center;font:700 26px {SG};padding:16px;border-radius:12px;border:2px solid currentColor;opacity:.6'>Deny</div></div>")
    return panel(inner, at, x, y, w, title="App · aprovação de ferramenta", dark=dark)


def gauge(label, pct, at, w=560, dark=False):
    """Plan usage gauge bar filling to pct."""
    uid = next(_uid)
    return (f"<style>@keyframes gg{uid}{{from{{width:0}}to{{width:{pct}%}}}}.gg{uid}{{animation:gg{uid} 1.1s cubic-bezier(.2,.7,.2,1) {at:.3f}s both}}</style>"
            f"<div style='width:{w}px;margin-top:20px'><div style='display:flex;justify-content:space-between;font:700 24px {MONO}'><span>{_h.escape(label)}</span><span>{pct}%</span></div>"
            f"<div style='height:22px;border-radius:11px;background:{'#0b1029' if dark else '#ece8de'};margin-top:10px;overflow:hidden'>"
            f"<div class='gg{uid}' style='height:100%;background:{LIME if pct < 85 else '#ff6b4a'};border-radius:11px'></div></div></div>")


def term(lines, at, x, y, w=980, step_s=0.5, title="zsh"):
    """Terminal window: lines = ['$ app update', 'output…'] typed one per step_s (or [(text, t)])."""
    rows = []
    for i, ln in enumerate(lines):
        tx, t = (ln if isinstance(ln, tuple) else (ln, at + .4 + i * step_s))
        col = LIME if tx.startswith("$") else "#c9cfe6"
        rows.append(f"<div class='ledin' style='--at:{ms(t)};font:700 30px/1.6 {MONO};color:{col};white-space:pre'>{_h.escape(tx)}</div>")
    return (f"<div class='heroin' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;width:{w}px;background:#080c20;border-radius:18px;overflow:hidden;"
            f"box-shadow:0 30px 80px rgba(0,0,0,.4);border:1px solid rgba(255,255,255,.1)'><div style='height:44px;background:#121a3d;display:flex;align-items:center;gap:9px;padding:0 18px'>"
            + "".join(f"<i style='width:12px;height:12px;border-radius:50%;background:{c}'></i>" for c in ("#ff5f57", "#febc2e", "#28c840"))
            + f"<span style='margin-left:14px;font:700 17px {MONO};color:#8f97b8'>{_h.escape(title)}</span></div><div style='padding:26px 32px'>{''.join(rows)}</div></div>")
