# Handoff — 2026-10-26 — video-sem-rosto: kit de vídeo sem rosto publicado (repo, guia, portal, Telegram); PRO pendente

## Projeto e escopo
Raiz `~/projetos/video-sem-rosto` (inematds/video-sem-rosto, público). Pedido do Nei (25/10): a partir de um kit de terceiro de "faceless video", criar repo, configurar tudo, README completo, publicar no INEMA.VIDEOS e no portal, e dizer onde é útil nos nossos projetos. Sessão aberta no `~/projetos/wifi`.

## Objetivo atual
Kit pronto e publicado. Falta só o PRO (inemabuscas + inemapro-mono) — pronto = `publica.sh "video-sem-rosto"` rodado com o item em `projetos.json`/`base.json`.

## Estado aceito
- [confirmed] Kit adaptado: voz local Chatterbox `nei` + Whisper local (`scripts/tts.py`, `scripts/_align.py`), tema INEMA e loudnorm 2 passadas (`scripts/fv.py`), imagens Codex/flux (`scripts/images.py`), `scripts/qc.py`, `setup.sh` com .venv — evidência: commit 535645b
- [confirmed] Teste ~40 s renderizado e QC verde — evidência: teste: `python3 scripts/qc.py .../out/video-sem-rosto-teste.mp4` → todos OK (−14,3 LUFS); release v1.0.0 com o mp4
- [confirmed] Guia PT/EN/ES no ar — evidência: urllib → 200 em /guia/, /guia/en/, /guia/es/; revisor independente 5 → 6 → 8 aprovado (`~/projetos/wifi/scripts/revisor-nota.py`)
- [confirmed] Portal: projeto em communityProjects + projectUpdatesData + EN/ES id 10165 + feeds-i18n — evidência: commit 493da6d no NeiMaldaner/portal (feito em worktree)
- [confirmed] INEMA.VIDEOS tópico 4987, MENU msg 5006 — evidência: saída do postar_topico.py

## Proposto / tentado, não confirmado
- nenhum

## Decisões
- Sem fonte do kit original em nada — regra feedback-projeto-sem-fonte.
- ElevenLabs e OpenRouter removidos; voz/whisper locais — regra de nenhuma API sem autorização.
- Whoosh desligado por padrão (FV_WHOOSH=1 liga) — regra D7 do inema-design.
- Portal feito em worktree e PRO adiado — `~/projetos/portal` tem lote "Cinema com IA" de outra sessão sem commit desde 25/10 01:27.

## Não fazer (restrições e travas)
- Não rodar `publica.sh` nem editar `~/projetos/portal` enquanto o lote Cinema com IA estiver sem commit — fonte: `~/projetos/wifi/pendencias.md`
- Não citar o autor/site de origem do kit — fonte: `~/.claude/projects/-home-nmaldaner-projetos-wifi/memory/feedback_projeto_sem_fonte.md`
- Não usar ElevenLabs/OpenRouter/qualquer API sem autorização — fonte: `CLAUDE.md`
- Não consultar Vercel — fonte: `~/.claude/CLAUDE.md`

## Arquivos alterados
- `SKILL.md`, `PROFILE.md`, `README.md`, `README.en.md`, `README.es.md`, `setup.sh`, `scripts/*`, `templates/*`, `guia/**`, `capa/capa.png`, `.github/workflows/pages.yml`, `CLAUDE.md`, `CHANGELOG.md`, `FALHAS.md`
- Fora do projeto: `~/projetos/output/video-sem-rosto/2026-10-25-teste-30s/` (job de teste), `~/projetos/output/posts-telegram/2026-10-26-video-sem-rosto.md`, `~/projetos/wifi/pendencias.md` (linha do PRO), `~/.claude/skills/video-sem-rosto` (symlink)

## Memória e regras duráveis tocadas
- `~/.claude/projects/-home-nmaldaner-projetos-wifi/memory/project_video_sem_rosto.md` — estado do projeto
- `~/.claude/projects/-home-nmaldaner-projetos-wifi/memory/MEMORY.md` — linha de índice

## Verificação
- Rodado: `bash setup.sh` → SELFTEST PASS (também com FV_VOICE=caminho .wav)
- Rodado: `python3 scripts/tts.py <job>` → 6/6 frases, semelhança média 0,932
- Rodado: `scripts/qc.py` no teste → todos OK
- Rodado: `npm test` no worktree do portal → 13 pass, 0 fail
- Não rodado: `publica.sh` / build do content-base — travado pelo portal sujo

## Estado em execução
- Processos em segundo plano: nenhum
- Servidores / portas: nenhum
- Worktrees / branches abertos: nenhum (worktree do portal removida)

## Perguntas abertas e adiados
- Aberta: o lote "Cinema com IA" (cursos 375+) em `~/projetos/portal` é do Nei? commitar, descartar ou esperar?
- Adiado: PRO do video-sem-rosto — depende da resposta acima

## Pela metade
- PRO — parou em: portal publicado, publica.sh não rodado — falta: enrichment `projeto:video-sem-rosto-guia` + `publica.sh`

## Próxima ação exata
Quando o Nei responder sobre o lote do portal e ele estiver commitado/descartado: classificar `projeto:video-sem-rosto-guia` no `~/projetos/inemapro-mono/packages/content-base/enrichment.json` e rodar `bash ~/.claude/skills/atualiza-portal/scripts/publica.sh "video-sem-rosto"`.

## Mapa de retomada
- `README.md` — o que o kit faz e onde usar
- `SKILL.md` — fluxo que o agente segue
- `~/projetos/wifi/pendencias.md` — pendência do PRO
- `FALHAS.md` — falhas corrigidas

## Perguntas-teste
1. Qual é a tarefa atual e o critério de pronto? → publicar no PRO via publica.sh — fonte: `~/projetos/wifi/pendencias.md` — chave: `publica.sh`
2. Qual foi a última decisão e por quê? → portal via worktree e PRO adiado pelo lote sujo — fonte: `~/projetos/wifi/pendencias.md` — chave: `Cinema com IA`
3. O que não pode mudar? → não citar fonte do kit; sem API — fonte: `CLAUDE.md` — chave: `fonte`
4. O que está pela metade? → PRO (inemabuscas + inemapro-mono) — fonte: `~/projetos/wifi/pendencias.md` — chave: `PRO`
5. Qual é a próxima ação, por quê, e precisa de aprovação? → enrichment + publica.sh depois da resposta do Nei sobre o lote — fonte: `~/projetos/wifi/pendencias.md` — chave: `enrichment`

## Checagem de compartilhamento
- Sem segredos, tokens, cookies, dados pessoais ou endpoints privados: sim


<!-- handoff-estado:inicio -->
## Estado gravado pelo script (não editar)

Gravado por handoff-grava.py no momento do handoff. `--conferir` compara com o projeto agora.

- commit: 10340b2e0cb6bb18fcb9b1b4cc984572b5dfd2a9 · branch: main
- arquivos sujos fora de handoffs/: 0
- `scripts/tts.py` · sha256:42af83f1176b · citado
- `scripts/_align.py` · sha256:b083a64e492a · citado
- `scripts/fv.py` · sha256:316986ee11de · citado
- `scripts/images.py` · sha256:b698db0498df · citado
- `scripts/qc.py` · sha256:9ef45f885938 · citado
- `setup.sh` · sha256:97af6690955e · citado
- `CLAUDE.md` · sha256:883629486156 · citado
- `SKILL.md` · sha256:572d02a75af9 · citado
- `PROFILE.md` · sha256:21f0be1a6154 · citado
- `README.md` · sha256:2fd44d4d0cbd · citado
- `README.en.md` · sha256:665c0e19a256 · citado
- `README.es.md` · sha256:e7f3d2d9b646 · citado
- `capa/capa.png` · sha256:6ab7cf686936 · citado
- `.github/workflows/pages.yml` · sha256:475e621919e3 · citado
- `CHANGELOG.md` · sha256:3d01c14cafa2 · citado
- `FALHAS.md` · sha256:0af5fd38f192 · citado

### Repo do trabalho: /home/nmaldaner/projetos/portal
- commit: 5c074ebe88871f4cbb8bef64742df350a654f059 · branch: main
- arquivos sujos: 6
- impressão de todos os sujos: 788b4ccc96c4fe9b
- `next-env.d.ts` · sha256:1862ac4bbbc5 · sujo
- `src/components/Portal.tsx` · sha256:2aab4d8ede3d · sujo
- `src/data/courses.data.json` · sha256:f07c75e116b4 · sujo
- `src/data/courses.ts` · sha256:79bfe584d42e · sujo
- `src/data/translated-courses.ts` · sha256:c1c45acf6b49 · sujo
- `tsconfig.tsbuildinfo` · sha256:e9b77764350e · sujo
<!-- handoff-estado:fim -->
