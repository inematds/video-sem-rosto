"""Job pieces: illustrated app screens (built from the docs — labels match the real UI names).
All times absolute seconds. Import after fv: `from pieces import *`."""
import random, html as _h
from fv import *
from fv import _uid

APP_NAV = ["Chat", "Agents", "Routines", "Approvals", "Settings"]
NAV_ICON = {"Chat": "message-square", "Agents": "bot", "Routines": "calendar-clock", "Approvals": "shield-check", "Settings": "settings"}


def app(at, body, active="Chat", x=160, y=110, w=1600, h=780, title="App"):
    """Desktop app window: traffic lights, left nav, content area (body positioned inside, origin = content top-left)."""
    nav = "".join(
        f"<div style='display:flex;align-items:center;gap:14px;padding:13px 18px;border-radius:12px;margin-bottom:6px;"
        f"font:700 22px Manrope;color:{'#16110f' if n == active else '#8a817a'};background:{'#fbe3d6' if n == active else 'transparent'}'>"
        f"{icon(NAV_ICON[n], '#e2622b' if n == active else '#a59d95', 24)}{n}</div>" for n in APP_NAV)
    return (f"<div class='heroin' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:22px;"
            f"overflow:hidden;background:#fff;box-shadow:0 34px 90px rgba(0,0,0,.30)'>"
            f"<div style='height:50px;background:#f3f1ee;display:flex;align-items:center;gap:9px;padding:0 20px;border-bottom:1px solid #e6e1db'>"
            + "".join(f"<i style='width:14px;height:14px;border-radius:50%;background:{c}'></i>" for c in ("#ff5f57", "#febc2e", "#28c840"))
            + f"<div style='flex:1;text-align:center;font:700 18px Manrope;color:#6b625b;margin-right:60px'>{title}</div></div>"
            f"<div style='position:absolute;left:0;top:50px;bottom:0;width:250px;background:#faf7f3;border-right:1px solid #eee8e1;padding:22px 16px'>"
            f"<div style='display:flex;align-items:center;gap:10px;font:800 24px Manrope;color:#16110f;margin:0 0 22px 8px'>"
            f"<span style='width:30px;height:30px;border-radius:9px;background:#e2622b;display:inline-block'></span>{title}</div>{nav}</div>"
            f"<div style='position:absolute;left:250px;top:50px;right:0;bottom:0;overflow:hidden'>{body}</div></div>")


def at_(x, y, inner, cls="", at=None, w=None):
    """Absolutely place inner content inside an app body."""
    a = f"class='{cls}' " if cls else ""
    st = f"--at:{ms(at)};" if at is not None else ""
    wd = f"width:{w}px;" if w else ""
    return f"<div {a}style='{st}position:absolute;left:{x}px;top:{y}px;{wd}'>{inner}</div>"


def typed(text, at, dur=None, size=24, color="#16110f", weight=600, font="Manrope"):
    """Typewriter: text revealed character by character from `at` over `dur` seconds."""
    uid = next(_uid); n = max(1, len(text)); dur = dur or min(1.6, 0.045 * n)
    return (f"<style>@keyframes ty{uid}{{from{{clip-path:inset(0 100% 0 0)}}to{{clip-path:inset(0 0 0 0)}}}}.ty{uid}{{display:inline-block;white-space:nowrap;"
            f"vertical-align:bottom;animation:ty{uid} {dur:.2f}s steps({n}) {at:.3f}s both}}</style>"
            f"<span class='ty{uid}' style='font:{weight} {size}px {font};color:{color}'>{_h.escape(text)}</span>")


def field(label, value, at, w=560, type_at=None, mono=False):
    """Form field: label + input box that types its value."""
    f = "ui-monospace, Menlo" if mono else "Manrope"
    return (f"<div class='rise' style='--at:{ms(at)};width:{w}px;margin-bottom:18px'>"
            f"<div style='font:700 17px Manrope;color:#8a817a;letter-spacing:.04em;text-transform:uppercase;margin-bottom:8px'>{label}</div>"
            f"<div style='border:2px solid #e6e1db;border-radius:12px;padding:12px 16px;min-height:52px;background:#fff'>"
            f"{typed(value, type_at if type_at is not None else at + .25, font=f)}</div></div>")


def pill_select(options, chosen, at, choose_at):
    """Segmented choice (e.g. approval mode); `chosen` gets highlighted at choose_at."""
    out = []
    for o in options:
        on = o == chosen
        out.append(f"<div class='{'selon' if on else ''}' style='--at:{ms(choose_at)};padding:12px 20px;border-radius:12px;border:2px solid #e6e1db;"
                   f"font:700 20px Manrope;color:#6b625b;white-space:nowrap'>{o}</div>")
    return f"<div class='rise' style='--at:{ms(at)};display:flex;gap:10px'>{''.join(out)}</div>"


def button(text, at, primary=True, press_at=None, size=24):
    bg, fg, bd = ("#e2622b", "#fff", "#e2622b") if primary else ("#fff", "#6b625b", "#e3ddd6")
    pr = f" flash" if press_at else ""
    return (f"<div class='pop' style='--at:{ms(at)};display:inline-block'><div class='{pr.strip()}' style='--at:{ms(press_at or at)};padding:14px 28px;"
            f"border-radius:13px;background:{bg};color:{fg};border:2px solid {bd};font:800 {size}px Manrope;white-space:nowrap'>{text}</div></div>")


def msg(text, at, me=True, w=760):
    """Chat bubble: me = right/orange-tint, agent = left/white with bot avatar."""
    if me:
        return (f"<div class='rise' style='--at:{ms(at)};display:flex;justify-content:flex-end;margin-bottom:16px'><div style='max-width:{w}px;"
                f"background:#fbe3d6;border-radius:18px 18px 4px 18px;padding:16px 22px;font:600 24px/1.4 Manrope;color:#3b302b'>{em(text)}</div></div>")
    return (f"<div class='rise' style='--at:{ms(at)};display:flex;gap:14px;margin-bottom:16px'><div style='width:46px;height:46px;flex:none;border-radius:50%;"
            f"background:#16110f;display:flex;align-items:center;justify-content:center'>{icon('bot', '#fff', 26)}</div><div style='max-width:{w}px;"
            f"background:#f6f2ed;border-radius:18px 18px 18px 4px;padding:16px 22px;font:600 24px/1.4 Manrope;color:#3b302b'>{em(text)}</div></div>")


def tool_step(name, detail, at, open_at=None, out=None):
    """Tool-call step row; if open_at, it expands to show its output."""
    body = ""
    if open_at and out:
        body = (f"<div class='rise' style='--at:{ms(open_at)};margin-top:10px;font:500 19px/1.45 ui-monospace,Menlo;color:#5c524b;background:#f7f3ee;"
                f"border-radius:10px;padding:12px 14px;white-space:pre'>{_h.escape(out)}</div>")
    return (f"<div class='rise' style='--at:{ms(at)};margin:0 0 12px 60px;border:2px solid #ece6df;border-radius:14px;padding:12px 16px;background:#fff;width:720px'>"
            f"<div style='display:flex;align-items:center;gap:12px;font:700 21px Manrope;color:#3b302b'>{icon('wrench', '#e2622b', 22)}{_h.escape(name)}"
            f"<span style='font:500 19px ui-monospace,Menlo;color:#8a817a'>{_h.escape(detail)}</span>"
            f"<span style='margin-left:auto;color:#2f9e5b;font:800 18px Manrope'>✓ done</span></div>{body}</div>")


def recalled(text, at):
    return (f"<div class='pop' style='--at:{ms(at)};display:inline-flex;align-items:center;gap:10px;margin:0 0 14px 60px;padding:9px 16px;"
            f"border-radius:99px;background:#16110f;color:#fff;font:700 19px Manrope'>{icon('brain', '#e2622b', 20)}{_h.escape(text)}</div>")


def approval(cmd, at, allow_at=None, who="Researcher", x=0, y=0, w=700):
    """Approval card: exact command + Deny / Allow (+ 'Always allow this command')."""
    return (f"<div class='pop' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;width:{w}px'>"
            f"<div style='background:#fff;border-radius:22px;padding:30px;box-shadow:0 24px 70px rgba(0,0,0,.22);border:2px solid #f2ebe4'>"
            f"<div style='font:800 18px Manrope;color:#e2622b;letter-spacing:.08em'>⚠ APPROVAL NEEDED</div>"
            f"<div style='font:800 30px Manrope;color:#16110f;margin:10px 0 12px'>{who} wants to run</div>"
            f"<div style='font:600 24px ui-monospace,Menlo;background:#f4efe9;border-radius:12px;padding:16px 18px;color:#3b302b'>{_h.escape(cmd)}</div>"
            f"<div style='display:flex;gap:14px;margin-top:20px'>"
            f"<div style='flex:1;text-align:center;padding:16px;border-radius:13px;border:2px solid #e3ddd6;font:800 26px Manrope;color:#8a817a'>Deny</div>"
            f"<div class='flash' style='--at:{ms(allow_at or at + 99)};flex:1;text-align:center;padding:16px;border-radius:13px;background:#e2622b;"
            f"font:800 26px Manrope;color:#fff'>Allow</div></div>"
            f"<div style='margin-top:14px;font:700 19px Manrope;color:#8a817a;display:flex;align-items:center;gap:10px'>"
            f"<span style='width:22px;height:22px;border:2px solid #cfc6bd;border-radius:6px;display:inline-block'></span>Always allow this command</div>"
            f"</div></div>")


def engine_row(slug, name, status, at, ready=True, color=None):
    src = logo_src(slug, color) if slug else None
    lg = (f"<img src='{src}' style='width:34px;height:34px'>" if src else icon("server", "#16110f", 32))
    st = (f"<span style='color:#2f9e5b;background:#e3f4ea;padding:6px 14px;border-radius:99px;font:800 18px Manrope'>● {status}</span>" if ready
          else f"<span style='color:#a0743a;background:#f8eddc;padding:6px 14px;border-radius:99px;font:800 18px Manrope'>{status}</span>")
    return (f"<div class='rise' style='--at:{ms(at)};display:flex;align-items:center;gap:18px;padding:16px 22px;border:2px solid #eee8e1;border-radius:16px;"
            f"margin-bottom:12px;width:820px;background:#fff'>{lg}<span style='font:800 25px Manrope;color:#16110f'>{name}</span>"
            f"<span style='margin-left:auto'>{st}</span></div>")


def proposal(quote, at, accept_at=None, reject=False):
    act = "Reject" if reject else "Accept"
    return (f"<div class='rise' style='--at:{ms(at)};display:flex;align-items:center;gap:18px;padding:18px 22px;border:2px solid #eee8e1;border-radius:16px;"
            f"margin-bottom:14px;width:1080px;background:#fff'><div style='flex:1'><div style='font:700 17px Manrope;color:#8a817a'>The person said:</div>"
            f"<div style='font:700 26px Manrope;color:#16110f'>“{_h.escape(quote)}”</div></div>"
            f"<div style='padding:12px 20px;border-radius:12px;border:2px solid #e3ddd6;font:800 21px Manrope;color:#8a817a'>Reject</div>"
            f"<div class='flash' style='--at:{ms(accept_at or at + 99)};padding:12px 20px;border-radius:12px;background:{'#e2622b' if not reject else '#fff'};"
            f"font:800 21px Manrope;color:{'#fff' if not reject else '#8a817a'}'>Accept</div></div>")


def qr(at, size=300, seed=7):
    r = random.Random(seed); n = 25; c = size / n
    cells = "".join(f"<rect x='{i * c:.1f}' y='{j * c:.1f}' width='{c:.1f}' height='{c:.1f}'/>" for i in range(n) for j in range(n)
                    if r.random() < .45 and not ((i < 8 and j < 8) or (i > 16 and j < 8) or (i < 8 and j > 16)))
    finder = lambda x, y: (f"<rect x='{x}' y='{y}' width='{7 * c}' height='{7 * c}' fill='none' stroke='#16110f' stroke-width='{c}'/>"
                           f"<rect x='{x + 2 * c}' y='{y + 2 * c}' width='{3 * c}' height='{3 * c}'/>")
    svg = (f"<svg width='{size}' height='{size}' viewBox='0 0 {size} {size}' fill='#16110f'>{cells}{finder(c / 2, c / 2)}"
           f"{finder(size - 7.5 * c, c / 2)}{finder(c / 2, size - 7.5 * c)}</svg>")
    return f"<div class='pop' style='--at:{ms(at)};background:#fff;padding:22px;border-radius:20px;display:inline-block'>{svg}</div>"


def terminal(lines, at, x, y, w=900, step=0.55):
    """Dark terminal; lines = [(text, t)] typed in."""
    rows = "".join(f"<div style='margin-bottom:10px'><span style='color:#e2622b'>$ </span>{typed(t, a, color='#f3ede6', font='ui-monospace, Menlo', size=26)}</div>"
                   for t, a in lines)
    return (f"<div class='heroin' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;width:{w}px;border-radius:18px;overflow:hidden;"
            f"background:#16110f;box-shadow:0 30px 80px rgba(0,0,0,.4)'><div style='height:42px;background:#241c19;display:flex;align-items:center;gap:8px;padding:0 16px'>"
            + "".join(f"<i style='width:12px;height:12px;border-radius:50%;background:{c}'></i>" for c in ("#ff5f57", "#febc2e", "#28c840"))
            + f"</div><div style='padding:26px 30px'>{rows}</div></div>")


def numbered(n, text, at, x, y, w=1300):
    """Big step row for the step-by-step section."""
    return (f"<div class='rise' style='--at:{ms(at)};position:absolute;left:{x}px;top:{y}px;width:{w}px;display:flex;align-items:center;gap:28px'>"
            f"<div style='width:96px;height:96px;flex:none;border-radius:26px;background:#e2622b;color:#fff;font:400 60px Anton;display:flex;"
            f"align-items:center;justify-content:center'>{n}</div><div style='font:800 52px/1.15 Manrope;letter-spacing:-.03em;color:#16110f'>{em(text)}</div></div>")


EXTRA_CSS = ".selon{animation:selon .3s ease var(--at) both}@keyframes selon{to{background:#e2622b;color:#fff;border-color:#e2622b}}"
import fv as _fv
if EXTRA_CSS not in _fv.CSS: _fv.CSS += EXTRA_CSS


def push(inner, t0, t1, scale=1.6, ox=960, oy=540):
    """Slow camera push-in on a region (frame px origin ox,oy) from t0 to t1 — use to make app text readable.
    Wrap an app(...) or browser(...) in it. Max one push per scene."""
    uid = next(_uid)
    return (f"<style>@keyframes pu{uid}{{from{{transform:scale(1)}}to{{transform:scale({scale})}}}}"
            f".pu{uid}{{position:absolute;inset:0;transform-origin:{ox}px {oy}px;animation:pu{uid} {max(t1 - t0, .1):.2f}s cubic-bezier(.65,0,.35,1) {t0:.3f}s both}}</style>"
            f"<div class='pu{uid}'>{inner}</div>")
