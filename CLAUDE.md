# CLAUDE.md — video-sem-rosto

Kit de vídeo 16:9 sem rosto (sem câmera, sem avatar). Instruções de uso: `SKILL.md`. Perfil INEMA: `PROFILE.md`. Visão geral e passos: `README.md`.

- Conta/autor dos commits: `inematds <inematds@gmail.com>`. Repo: `inematds/video-sem-rosto`.
- Nenhuma API paga: voz = Chatterbox local (inemavox), tempo por palavra = Whisper local, imagens = Codex pela assinatura (flux local de reserva). ElevenLabs/OpenRouter não entram.
- Sem fonte: o kit não cita material de terceiros que serviu de base (README, SKILL, exemplos, posts).
- Visual segue `~/projetos/inema-design/DESIGN.md` + `video/style.md` (tema `inema` do `fv.py`). Sem whoosh por padrão.
- Render e captura com `TMPDIR=$(mktemp -d /tmp/fv.XXXX)` (Chromium aborta com caminho de socket longo).
- Mudou o fluxo? Atualizar a seção "O processo, do início ao fim" do README no mesmo commit.

## Self-learning
Quando eu for corrigido ou pegar um erro meu: antes de seguir, escrever a lição como regra de uma linha no TOPO de `## Lessons` abaixo.

## Lessons
- Loudnorm de 1 passada em voz sintética curta fica ~2 LU abaixo: usar `_loudnorm2` (compressor + 2 passadas) e sempre rodar `scripts/qc.py`. (25/10/2026)
