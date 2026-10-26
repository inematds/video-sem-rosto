"""Vídeo longo sem rosto (modelo). Tempos = segundos da narração (words.json).
ROUTINE: cream/dark alternate every scene; orange statement card ~1/min; real GitHub/news screencasts in browser frames;
telas ilustradas do app (pieces.py) for in-app features; 3D clay hero per idea; karaoke caption pill."""
import sys, os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/video-sem-rosto/scripts"))
J = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, J)
from fv import *
from pieces import *
from fv import _uid
I = lambda n: os.path.join(J, "img", n + ".png")
C = lambda n: os.path.join(J, "cap", n)
v = Video(J, os.path.basename(J))
for part in ("A", "B", "C", "D", "E"):
    f = os.path.join(J, f"_scenes_{part}.py")
    if os.path.exists(f): exec(open(f).read())

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["stills"]:
        rng = [float(x) for x in a[1:3]] if len(a) >= 3 else None
        keep = [s for s in v.scenes if not rng or (rng[0] <= s["s"] < rng[1])]
        v.scenes, allsc = keep, v.scenes
        print(v.stills(out=f"stills_{a[1] if rng else 'all'}.jpg"))
    elif a[:1] == ["check"]:
        sc = sorted(v.scenes, key=lambda s: s["s"]); gaps = []
        for p, q in zip(sc, sc[1:]):
            if abs(p["e"] - q["s"]) > 0.02: gaps.append((round(p["e"], 2), round(q["s"], 2)))
        print(len(sc), "scenes", "first", sc[0]["s"], "last end", sc[-1]["e"], "gaps/overlaps:", gaps[:20])
        bgs = [s["bg"] for s in sc]; rep = [i for i in range(1, len(bgs)) if bgs[i] == bgs[i - 1]]
        print("same bg twice in a row at scene idx:", rep[:30])
    else:
        v.scenes.sort(key=lambda s: s["s"]); print(v.render())
