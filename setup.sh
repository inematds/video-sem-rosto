#!/bin/bash
# video-sem-rosto — instalação única. Tem que terminar com "SELFTEST PASS".
# Não instala nada global: cria .venv dentro do repo e liga a skill em ~/.claude/skills/video-sem-rosto.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
command -v python3 >/dev/null || { echo "Falta Python 3"; exit 1; }
command -v ffmpeg  >/dev/null || { echo "Falta ffmpeg (sudo apt install ffmpeg)"; exit 1; }
command -v codex   >/dev/null || echo "aviso: Codex CLI ausente — sem renders 3D (use FV_IMG=flux ou só prints)"

# 1. ambiente Python do projeto (Playwright + Pillow)
[ -x "$DIR/.venv/bin/python" ] || python3 -m venv "$DIR/.venv"
"$DIR/.venv/bin/python" -m pip install --quiet --upgrade pip
"$DIR/.venv/bin/python" -m pip install --quiet -r "$DIR/requirements.txt"
"$DIR/.venv/bin/python" -m playwright install chromium

# 2. voz e Whisper locais (inemavox)
VOX="${INEMAVOX_DIR:-$HOME/projetos/inemavox}"
CB="${CHATTERBOX_PYTHON:-$HOME/miniconda3/envs/chatterbox/bin/python3}"
REF="$HOME/projetos/timesmkt3/media/voice-refs/${FV_VOICE:-nei}.wav"
for f in "$VOX/chatterbox_tts_worker.py" "$VOX/venv/bin/python" "$CB" "$REF"; do
  [ -e "$f" ] || { echo "Falta: $f (ver README › Instalação)"; exit 1; }
done
"$VOX/venv/bin/python" -c "import faster_whisper, soundfile" || { echo "faster-whisper ausente no venv do inemavox"; exit 1; }

# 3. skill visível para o Claude Code
mkdir -p "$HOME/.claude/skills"
if [ ! -e "$HOME/.claude/skills/video-sem-rosto" ]; then ln -s "$DIR" "$HOME/.claude/skills/video-sem-rosto"; fi

# 4. autoteste: importa o motor e desenha uma cena de verdade no Chromium
cd "$DIR"
TMPDIR="$(mktemp -d /tmp/fvst.XXXX)" "$DIR/.venv/bin/python" - <<PY
import sys, os, json, tempfile; sys.path.insert(0, "$DIR/scripts")
import fv
from playwright.sync_api import sync_playwright
job = tempfile.mkdtemp(prefix="fvself_")
json.dump([["teste", 0.0, 0.5], ["ok", 0.6, 1.0]], open(os.path.join(job, "words.json"), "w"))
v = fv.Video(job, "selftest"); v.scene(0, 1.2, "dark", fv.head("Teste *ok*", 0.0))
page = v.write_pages()[0]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.goto("file://" + page); pg.evaluate("__seek(1.0)")
    assert "TESTE" in pg.inner_text("body").upper(); b.close()
print("SELFTEST PASS")
PY
