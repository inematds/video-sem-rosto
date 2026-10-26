# Remove repetição de imagem real (regras de reuso do YouTube): cada trecho de clipe aparece uma vez só.
# Scenes whose clip is tied to the line keep it; any later repeat is swapped for an unused segment of an official
# clipe oficial que combine com aquela parte do vídeo. Os nomes em POOL são exemplos: troque pelos seus clipes.
import re as _re, subprocess as _sp
_DUR = {}
def _dur(n):
    if n not in _DUR:
        _DUR[n] = float(_sp.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                          os.path.join(J, "clips", n + ".mp4")]))
    return _DUR[n]

POOL = {  # time range -> preferred fresh clips (in order)
    (0, 140): ["clipe_a", "clipe_b"],
    (140, 183.4): ["clipe_b", "clipe_a"],
    (183.4, 210): ["clipe_c", "clipe_b", "clipe_a"],
    (210, 268.6): ["clipe_d", "clipe_e", "clipe_b"],
    (268.6, 330): ["clipe_c", "clipe_e", "clipe_b", "clipe_a"],
    (330, 400): ["clipe_a", "clipe_d", "clipe_b", "clipe_e"],
}
_used = {}   # clip -> list of (a, b)
def _free(n, need, avoid_start=0.0):
    d = _dur(n); t = avoid_start
    while t + need <= d + 0.01:
        if all(not (t < b - 0.2 and a < t + need - 0.2) for a, b in _used.get(n, [])):
            return t
        t += 0.5
    return None

_pat = _re.compile(r"data-at='([\d.]+)' data-start='([\d.]+)' src='file://([^']*/)([^/']+)\.fv\.webm'")
for sc in sorted(v.scenes, key=lambda s: s["s"]):
    def _sub(m):
        at, st, base, name = float(m.group(1)), float(m.group(2)), m.group(3), m.group(4)
        need = max(1.0, sc["e"] - at)
        b = min(_dur(name), st + need)
        clash = any(st < bb - 0.3 and aa < b - 0.3 for aa, bb in _used.get(name, []))
        if not clash and (b - st) >= need - 0.6:
            _used.setdefault(name, []).append((st, b)); return m.group(0)
        pool = next(p for (lo, hi), p in POOL.items() if lo <= sc["s"] < hi)
        for n2 in pool + [name]:
            t = _free(n2, need, 2.8 if n2 == "clipe_c" and sc["s"] > 210 else 0.0)
            if t is not None:
                _used.setdefault(n2, []).append((t, t + need))
                prep_clip(os.path.join(J, "clips", n2 + ".mp4"))
                return f"data-at='{at}' data-start='{t:.2f}' src='file://{base}{n2}.fv.webm'"
        _used.setdefault(name, []).append((st, b)); return m.group(0)
    sc["body"] = _pat.sub(_sub, sc["body"])
