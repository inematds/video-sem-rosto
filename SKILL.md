---
name: video-sem-rosto
description: Vídeo explicativo 16:9 SEM ROSTO (sem câmera, sem avatar) a partir de um link ou assunto — pesquisa a fonte oficial, roteiro aprovado pelo dono do canal, voz local clonada (Chatterbox, sem API; no INEMA, a voz do Nei), cenas de motion design no tema INEMA (preto/papel/amarelo, Sora) com print real do site, render 3D e legenda karaokê, 1080p60, QC, thumbs e descrição com capítulos. 30 s a 15 min. Gatilho: "vídeo sem rosto", "faceless", "vídeo sem avatar sobre <link>", "/video-sem-rosto". Com avatar do Nei = explicavideos; reel/short 9:16 = makeshorts/r7ex.
---

# Vídeo sem rosto (16:9, voz + motion design)

**Leia `PROFILE.md` primeiro** (voz, chamada, visual, palavras proibidas). Python do motor: `FVPY=~/projetos/video-sem-rosto/.venv/bin/python`.
Ponto de partida: `templates/exemplo_30s.py` (30 s). Roteiro longo: `templates/roteiro_longo_modelo.md`.

## Pipeline (pasta: `~/projetos/output/video-sem-rosto/<data>-<slug>/`)
Forma do vídeo longo: gancho (ferramenta nomeada na 1ª frase) → o que aconteceu → por que importa (antes × agora) →
recursos, um bloco cada, descritos como aparecem na ferramenta (onde clica, o que aparece) → chamada 1 (~3:00) → mais
recursos → como instalar/rodar → o primeiro uso, passo a passo → chamada 2. ~1.850 palavras ≈ 12 min.

1. **Pesquisa** — abrir a fonte primária (repo, docs, anúncio). Anotar cada número e nome que será dito, conferido.
   O que não dá para conferir não entra.
2. **Roteiro** → `<job>/<Título> - roteiro.md` (cabeçalhos `### m:ss — Seção` pela contagem a 150 palavras/min) +
   `script.txt` (só a fala, linha em branco entre batidas — vai para a voz).
   **PORTÃO: o dono do canal (no INEMA, o Nei) aprova o roteiro antes da voz e do render.** Mostrar com contagem de palavras, duração e onde caem as chamadas.
3. **Voz** — `python3 scripts/tts.py <job>` → `vo.mp3` + `words.json` + `vo_qc.json`. Chatterbox local com `FV_VOICE=nei`;
   Whisper local mede cada frase e gera de novo a que sair < 0,80. Erro em frase = reescrever a frase (número por extenso,
   sigla soletrada) e rodar de novo. ~150 palavras/min.
4. **Material, em paralelo com o passo 3:**
   - Renders 3D: `python3 scripts/images.py <job>/img c_nome="objeto…" d_nome="objeto…"` (`c_` fundo claro, `d_` escuro;
     UM objeto por render). Codex pela assinatura; `FV_IMG=flux` = reserva local. Um render a cada ~2 cenas, nunca repetido em seguida.
   - Prints: `TMPDIR=$(mktemp -d /tmp/fvc.XXXX) $FVPY scripts/capture.py <url> <job>/cap/x.png "texto a achar" …` → página
     inteira + caixa de cada texto (para mirar zoom e anel).
   - Logos: `logo_src("<slug do simple-icons>")` dentro de `tile()`.
   - Clipe oficial: baixar com `~/projetos/inemavox/baixar_v1.py --url <post> --outdir <job>/clips` (nunca yt-dlp avulso).
5. **Cenas** → `job.py` (copiar o exemplo). Um `v.scene(início, fim, fundo, corpo)` por batida, 2–6 s cada, tempos lidos do
   `words.json`. Peças em `scripts/fv.py`: `kicker head title hero chip tile browser stamp ring card cursor_click big_card
   icon logo_src clip offer_page reviews_wall`. `*palavra*` = destaque, `_palavra_` = destaque secundário.
6. **Conferir** — `$FVPY job.py stills` → `out/stills.jpg`. Ver sobreposição, ortografia, quadro vazio, zoom caindo no que
   a voz fala. Corrigir e ver de novo.
7. **Render** — `TMPDIR=$(mktemp -d /tmp/fvr.XXXX) $FVPY job.py` → `out/<nome>.mp4` (60 fps, 12 Mbps, voz −14 LUFS,
   trilha opcional `<job>/music.mp3` a −26 dB). `FV_FPS=30` para prévia rápida.
8. **QC** — `python3 scripts/qc.py out/<nome>.mp4` (1920x1080, 60 fps, ≥ 8 Mbps, −14 LUFS ±1, sem quadro preto,
   folha de contato) — e OLHAR a folha.
9. **Thumbs** — Codex image_gen com o gancho desenhado na arte (regra INEMA). Só logo oficial.
10. **Entrega** — vídeo + roteiro + descrição com capítulos + lista dos fatos usados e do que não foi conferido.
    No INEMA (opcional fora dele): publicar pelo `yt-pubx` (`--dry-run` antes), espanhol pela `fila_es.py`, aviso no bot com o link.

## Imagem real (mostrar a coisa)
- Se o tema tem teaser/demo oficial, MOSTRAR: `clip(src, at, x, y, w, start=<s>, credit="Oficial · @conta")`.
- Seguro: trechos curtos (3–8 s, sem repetir), crédito curto do canal oficial, mudo (só a voz), com comentário e grafismo
  em volta, fonte oficial primeiro. Material de terceiros ≤ 30 % do vídeo. Depois de cenas escritas em paralelo, rodar o
  passo de não repetir clipe (`templates/dedupe_footage_example.py`).
- Vídeo de outra pessoa que serviu de BASE (refazvideo) não aparece nem é citado.

## Nunca o mesmo molde duas vezes
Três looks — alternar entre vídeos e variar o layout dentro de cada um (nunca o mesmo layout 3× seguidas):
- **LOOK 1 "reel"** (padrão): papel ↔ preto, Sora + palavra amarela, render 3D, chips, legenda karaokê.
- **LOOK 2 "cinema"**: `Video(..., look="cinema")` + `templates/pieces_cinema.py` — imagem real primeiro, Ken Burns lento,
  letterbox, chamadas apontando para o produto, legenda de rodapé.
- **LOOK 3 "ledger"**: `Video(..., look="ledger")` + `templates/pieces_ledger.py` — cara de notas de versão, contadores,
  linhas de changelog, marca-texto amarelo.
O tema INEMA (`FV_THEME=inema`, padrão) troca cores e fontes nos três.

## Estilo do roteiro
- **1ª frase nomeia a ferramenta e diz o que ela é.** A pergunta-gancho vem depois do nome, nunca antes.
- Frases curtas, uma ideia cada. Nomear a origem na tela (pílula: "GitHub · dono/repo").
- **Ficar na ferramenta**: explicar como funciona por dentro ("você clica em Agentes, depois em Novo agente…").
  Sem conceito genérico, sem caso de uso genérico.
- Antes × agora = contra a limitação do produto ORIGINAL (fila de espera, região, plano pago, um só fornecedor).
- Não narrar rede social (posts, enquetes, opiniões) — post só serve de fonte de fato.
- Nunca "o README diz" — dizer o fato com as próprias palavras. Simples, sem hype, sem número inventado.
- Proibido: "Não é X. É Y.", "isso muda tudo", "revolucionar", abrir com "Imagine que…/Pense num…/Se você…/Neste momento…".
- **Chamada (PROFILE) em ~3:00 e no fim, ligada ao tema**: "Se você quer o passo a passo de <tema>, como <o fluxo deste
  vídeo>, está tudo no INEMA.CLUB, de graça." Fim = resumo curto + "tá tudo no inema.club".

## Regras visuais
- Fundo alterna a cada cena (papel ↔ preto); cartão amarelo (`big_card`) ~1× por minuto.
- Algo grande na tela no 1º quadro de cada cena; um elemento novo a cada batida falada. Uma palavra em destaque por título.
- Print real pelo menos a cada ~45 s: página de verdade, zoom no número/linha que a voz fala, com anel. Zoom não corta texto.
- Legenda karaokê sempre, 1–3 palavras por bloco.
- Área segura x 110–1810, y 40–1000; legenda ocupa y ≈ 925–1000, chips acima de ~860.

## Dicas para vídeo longo
- Copiar `templates/job_full_template.py` → `job.py` (executa `_scenes_A/B/C.py`; `$FVPY job.py check` = cobertura sem buraco
  + alternância de fundo, `$FVPY job.py stills <de> <até>`) e `templates/pieces_app_screens.py` → `pieces.py` (janela de app
  ilustrada). Trocar os rótulos pelos nomes reais da interface.
- Voz primeiro, depois cenas em paralelo (subagentes por faixa de tempo, cada um com os fatos conferidos e o `words.json`).
- Renders e prints em segundo plano enquanto a voz gera.

## Armadilhas
- `capture.py` cai para `domcontentloaded` quando a página não sossega; alguns sites (Hugging Face, X) bloqueiam headless.
- Chromium do Playwright aborta com "Socket path too long" se TMPDIR for o scratchpad: usar `TMPDIR=$(mktemp -d /tmp/fv.XXXX)`.
- Encode final usa `-x264-params nal-hrd=cbr` (grafismo chapado continua acima de 8 Mbps).
- Modelo de imagem às vezes redesenha logo — pedir "copy EXACTLY: <descrição da marca>" ou usar `tile(logo_src())`.
- Simple Icons não tem logo da `openai` — usar ícone.
- Cada cena = uma página HTML avançada com `document.getAnimations()`; todo atraso de animação é em segundos absolutos.
- Chatterbox erra sigla e número escrito com dígito: escrever por extenso no `script.txt` ("mil e oitenta pê") quando a frase reprovar.
