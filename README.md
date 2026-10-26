# video-sem-rosto

[![video-sem-rosto](guia/assets/banner.jpg)](https://inematds.github.io/video-sem-rosto/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

O video-sem-rosto é um kit (uma "skill") que ensina o Claude Code a fazer vídeos explicativos na horizontal sem gravar nada: sem câmera, sem avatar. Serve para quem quer explicar uma ferramenta, um repositório ou uma novidade em vídeo sem aparecer e sem pagar serviço de voz. A voz é gerada no seu computador com uma voz clonada, e as cenas mostram a página real do site, imagens 3D e legenda sincronizada. Para usar, você precisa do Claude Code, ffmpeg, Python e do inemavox (que faz a voz e a transcrição) rodando na máquina.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/video-sem-rosto/guia/** · Vídeo de teste: [release 1.0.1](https://github.com/inematds/video-sem-rosto/releases/tag/v1.0.1)


## 🎬 Exemplos

| Exemplo 1 — look reel: o próprio kit (~40 s) | Exemplo 2 — look ledger: yt-pubx (~35 s) |
|---|---|
| [![Exemplo 1 — look reel: o próprio kit (~40 s)](guia/assets/exemplo-reel.jpg)](https://inematds.github.io/video-sem-rosto/guia/assets/exemplo-reel.mp4) | [![Exemplo 2 — look ledger: yt-pubx (~35 s)](guia/assets/exemplo-ledger.jpg)](https://inematds.github.io/video-sem-rosto/guia/assets/exemplo-ledger.mp4) |

Clique na imagem para abrir o vídeo. Em 1080p60: [release 1.0.1](https://github.com/inematds/video-sem-rosto/releases/tag/v1.0.1). Os dois saem de `templates/exemplo_30s.py` e `templates/exemplo_ledger.py`.

---

**Vídeo explicativo 16:9 sem câmera e sem avatar, feito pelo Claude Code a partir de um link ou assunto.**
O agente pesquisa a fonte oficial, escreve o roteiro, você aprova, a voz é gerada **na sua máquina** e cada frase vira uma cena de motion design — título, print real do site, imagem 3D e legenda palavra por palavra — em 1080p a 60 quadros.

- 🎙️ **Voz local** (Chatterbox, voz clonada) com tempo de cada palavra medido por Whisper local — **nenhuma API paga**.
- 🎨 **Tema INEMA**: preto `#0c0c10`, papel claro, amarelo `#FACC15`, títulos Sora, corpo Inter.
- 🖼️ **Prints reais**: abre a página, acha o texto que a voz cita e dá zoom nele.
- 🎬 **3 looks** (reel, cinema, ledger) para os vídeos não parecerem todos iguais.
- ✅ **Portões**: roteiro aprovado antes da voz; frase mal falada é gerada de novo; QC técnico no fim.

Teste incluído: um vídeo de ~40 s sobre o próprio kit (`templates/exemplo_30s.py`).

---

## O processo, do início ao fim

Quem faz: 🧠 sessão com o Nei · ⚙️ script · 🤖 agente (Claude Code seguindo o `SKILL.md`)

| # | Passo | Comando / ação | Quem |
|---|---|---|---|
| 1 | Pedir o vídeo | "faz um vídeo sem rosto sobre `<link>`, uns 8 minutos" | 🧠 |
| 2 | Pesquisar a fonte oficial e anotar cada fato | lê repo/docs/anúncio; o que não confere fica fora | 🤖 |
| 3 | Escrever o roteiro | `<job>/<Título> - roteiro.md` + `script.txt` (modelo: `templates/roteiro_longo_modelo.md`) | 🤖 |
| 4 | **Aprovar o roteiro** (portão) | o agente mostra palavras, duração e onde caem as chamadas; nada é gerado antes do "ok" | 🧠 |
| 5 | Gerar a voz com tempo por palavra | `python3 scripts/tts.py <job>` → `vo.mp3`, `words.json`, `vo_qc.json` | ⚙️ |
| 6 | Imagens 3D (em paralelo com o 5) | `python3 scripts/images.py <job>/img c_x="…" d_y="…"` (Codex pela assinatura) | ⚙️ |
| 7 | Prints dos sites (em paralelo com o 5) | `$FVPY scripts/capture.py <url> <job>/cap/x.png "texto"` | ⚙️ |
| 8 | Escrever as cenas pelos tempos das palavras | `job.py` copiado de `templates/` (longo: `job_full_template.py` + subagentes por faixa) | 🤖 |
| 9 | Conferir a folha de cenas | `$FVPY job.py stills` → `out/stills.jpg`; corrige e confere de novo | 🤖 |
| 10 | Render 1080p60 | `$FVPY job.py` → `out/<nome>.mp4` | ⚙️ |
| 11 | QC técnico + olhar a folha | `python3 scripts/qc.py out/<nome>.mp4` | ⚙️ + 🤖 |
| 12 | Thumbs + descrição com capítulos | Codex image_gen com o gancho desenhado; capítulos tirados do roteiro | 🤖 |
| 13 | Publicar | `yt-pubx publicar … --dry-run` → olhar → publicar; ES vai para `fila_es.py` | 🧠 aprova · ⚙️ publica |

`$FVPY` = `~/projetos/video-sem-rosto/.venv/bin/python` (criado pelo `setup.sh`). Rode render e captura com
`TMPDIR=$(mktemp -d /tmp/fv.XXXX)` na frente: o Chromium aborta com caminho de socket longo demais.

---

## Instalação (uma vez, ~5 min)

Pré-requisitos (o `setup.sh` confere e diz o que falta):

| O quê | Para quê | Como instalar |
|---|---|---|
| Python 3 + ffmpeg | motor e encode | `sudo apt install python3-venv ffmpeg` |
| [inemavox](https://github.com/inematds/inemavox) | worker do Chatterbox + `venv` com faster-whisper (tempo por palavra) | `git clone https://github.com/inematds/inemavox ~/projetos/inemavox && cd ~/projetos/inemavox && python3 -m venv venv && venv/bin/pip install faster-whisper soundfile numpy` |
| Chatterbox (conda `chatterbox`) | modelo aberto que clona a voz de um áudio curto (GPU recomendada) | `conda create -n chatterbox python=3.11 -y && ~/miniconda3/envs/chatterbox/bin/pip install chatterbox-tts soundfile` |
| Voz de referência | a voz que narra: 10 s de fala limpa, `.wav` 24 kHz mono | `ffmpeg -i gravacao.m4a -ss 2 -t 10 -ac 1 -ar 24000 ~/minha-voz.wav && export FV_VOICE=~/minha-voz.wav` |
| Codex CLI logado (opcional) | imagens 3D pela assinatura do ChatGPT | `codex login` — sem ele, use só prints/logos ou `FV_IMG=flux` se tiver um servidor flux2-klein local |

Caminhos diferentes? `INEMAVOX_DIR`, `CHATTERBOX_PYTHON`, `FV_VOICE` (nome em `FV_VOICE_DIR` ou caminho `.wav`). No INEMA, `FV_VOICE=nei` usa a voz já gravada em `~/projetos/timesmkt3/media/voice-refs/`.

```bash
git clone https://github.com/inematds/video-sem-rosto ~/projetos/video-sem-rosto
cd ~/projetos/video-sem-rosto
bash setup.sh          # cria .venv, instala Playwright+Chromium, confere voz/Whisper, liga a skill
                       # tem que terminar com: SELFTEST PASS
```

Deixe a voz fixa no shell (`echo 'export FV_VOICE=~/minha-voz.wav' >> ~/.bashrc`) e edite o `PROFILE.md`: ele vem com o perfil do INEMA (chamada para o inema.club, publicação pelo yt-pubx, avisos no bot) — troque nome, chamada, canal e regras pelos seus. Na 1ª execução o Whisper large-v3 (~3 GB) e o Chatterbox baixam os pesos. Se o Playwright pedir bibliotecas do sistema: `sudo .venv/bin/python -m playwright install-deps chromium`.

O `setup.sh` cria o link `~/.claude/skills/video-sem-rosto → este repo`. A partir daí, no Claude Code:

```
faz um vídeo sem rosto sobre https://github.com/dono/projeto — uns 8 minutos, me mostra o roteiro antes
```

### Teste de 30–40 s

```bash
J=~/projetos/output/video-sem-rosto/teste; mkdir -p $J/img $J/cap
cp templates/exemplo_30s.py $J/job.py
cp templates/exemplo_30s.txt $J/script.txt
python3 scripts/tts.py $J                                         # voz + words.json
python3 scripts/images.py $J/img d_clap="a film clapperboard beside an empty tripod" d_monitor="a widescreen monitor with a play button"
TMPDIR=$(mktemp -d /tmp/fv.XXXX) .venv/bin/python scripts/capture.py https://github.com/inematds/yt-pubx $J/cap/gh.png
TMPDIR=$(mktemp -d /tmp/fv.XXXX) .venv/bin/python $J/job.py stills   # olhe out/stills.jpg
TMPDIR=$(mktemp -d /tmp/fv.XXXX) .venv/bin/python $J/job.py          # render
python3 scripts/qc.py $J/out/video-sem-rosto-teste.mp4
```

O exemplo espera `img/d_clap.png`, `img/d_monitor.png` e `cap/gh.png` (os comandos acima geram com esses nomes). Os tempos das cenas são os da voz gerada aqui; com outra voz, ajuste os `v.scene(início, fim, …)` lendo o `words.json`.

---

## Como funciona por dentro

### Voz (`scripts/tts.py` + `scripts/_align.py`)
1. O `script.txt` é dividido em **batidas** (linha em branco) e **frases** (até 160 caracteres).
2. O worker do Chatterbox (inemavox) gera todas as frases numa carga só do modelo, com a voz de `FV_VOICE` (padrão `nei`, cfg 0,6 / exageração 0,6).
3. O Whisper large-v3 local (mesmo lock do explicavideos, um por vez na GPU) corta o silêncio da ponta, ouve cada frase e compara com o texto.
4. Frase com semelhança < `FV_MIN_SIM` (0,80) é **gerada de novo** (até 2 vezes). Se continuar ruim, o script para e aponta a frase em `vo_qc.json` — reescreva (número por extenso, sigla soletrada).
5. Junta com pausas (0,28 s entre frases, 0,55 s entre batidas). O `words.json` leva a **grafia do roteiro** com o tempo ouvido pelo Whisper; palavra sem par é interpolada entre as vizinhas.

| Variável | Padrão | O que faz |
|---|---|---|
| `FV_VOICE` | `nei` | `nei`, `nei2`, `nei3`, `nei4` ou caminho de um `.wav` de referência (10 s, 24 kHz mono) |
| `FV_LANG` | `pt` | idioma da voz e do Whisper (`en`, `es`…) |
| `FV_ATEMPO` | `1.0` | acelera a voz (máx. 1,15) |
| `FV_MIN_SIM` | `0.80` | semelhança mínima por frase |
| `FV_CFG` / `FV_EXAG` | `0.6` / `0.6` | ajuste do Chatterbox |

### Cenas (`scripts/fv.py`)
Cada cena é **uma página HTML** com animações CSS em segundos absolutos da narração. O Chromium headless (Playwright) avança quadro a quadro com `document.getAnimations()` e manda os quadros para o ffmpeg em pedaços de 4 s em paralelo; no fim, mistura a voz (−14 LUFS) e a trilha opcional.

Peças disponíveis:

| Peça | O que desenha |
|---|---|
| `kicker(texto, t)` | pílula no topo com a origem ("GitHub · dono/repo") |
| `head(texto, t, per_word=[…])` | título em caixa alta, palavras entrando no tempo da fala |
| `title(texto, t)` | título em frase normal |
| `hero(img, t)` | render 3D com borda esfumada e flutuação leve |
| `chip(texto, t, x, y, ico=, accent=)` | etiqueta com ícone Lucide; `accent` = amarela |
| `tile(logo_src("github"), t, x, y, label=)` | ícone de app com logo oficial (Simple Icons) |
| `browser(print, t, x, y, w, h, scroll=, zoom=)` | print real numa janela de navegador, com rolagem e zoom |
| `stamp(texto, t, x, y)` | carimbo vermelho de número grande |
| `ring(t, x, y, w, h)` | anel destacando um trecho |
| `card(html, t, x, y, w)` | cartão branco |
| `cursor_click(t0, t1, x0, y0, x1, y1)` | cursor que anda e clica |
| `big_card([(texto, t), …])` | cartão amarelo de tela cheia (uma afirmação forte) |
| `clip(mp4, t, x, y, w, start=, credit=)` | trecho mudo de vídeo oficial, com crédito curto |
| `offer_page(t)` / `reviews_wall(t, dur)` | print da página do inema.club / depoimentos (opcional, em `assets/proof/`) |

No texto: `*palavra*` = destaque (amarelo no escuro, marca-texto no claro), `_palavra_` = destaque secundário.

### Looks
- **reel** (padrão): papel ↔ preto, chips, render 3D, legenda karaokê.
- **cinema**: `Video(job, look="cinema")` + `templates/pieces_cinema.py` — imagem real primeiro, Ken Burns lento, letterbox, chamadas apontando para o produto.
- **ledger**: `Video(job, look="ledger")` + `templates/pieces_ledger.py` — notas de versão, contadores, linhas de changelog.

`FV_THEME=inema` (padrão) aplica as cores e fontes INEMA nos três. `FV_THEME=original` volta para a paleta creme/laranja do kit de base.

### Som
Só voz, a −14 LUFS, e trilha opcional (`<job>/music.mp3`, do inemavox) a −26 dB. **Sem whoosh** nos cortes (regra INEMA); `FV_WHOOSH=1` liga se for pedido.

### Imagens 3D (`scripts/images.py`)
Codex CLI `image_gen` pela assinatura do ChatGPT (sem API), 3 em paralelo, ~1–2 min cada. Estilo da casa acrescentado sozinho: render fosco premium, luz neutra (sem amarelado), um objeto, fundo liso (`c_` papel / `d_` preto), robô só humanoide industrial. Reserva: `FV_IMG=flux` usa o flux2-klein local (`localhost:8000`).

### Prints (`scripts/capture.py`)
Abre a página em 1600 px (escala 1,5), remove barras fixas e avisos de cookie, salva a página inteira (até 6000 px) e um `.json` com a caixa de cada texto pedido — para mirar `zoom`, `scroll` e `ring` exatamente no que a voz fala. Sites que bloqueiam headless (Hugging Face, X) precisam de print manual.

---

## Regras do roteiro (resumo do `SKILL.md`)
- A 1ª frase nomeia a ferramenta e diz o que ela é.
- Uma ideia por frase; explicar como funciona **dentro** da ferramenta, sem caso de uso genérico.
- Antes × agora = contra a limitação do produto original.
- Sem hype, sem número inventado, sem "o README diz", sem narrar rede social.
- Chamada para o **INEMA.CLUB** em ~3:00 e no fim, ligada ao tema do vídeo.
- Trecho de vídeo oficial: 3–8 s, mudo, com crédito curto, no máximo 30 % do vídeo.

---

## Onde isso é útil nos nossos projetos

O que o kit traz de novo em relação ao que já temos: **voz local com tempo por palavra conferido**, **print real com zoom no texto que a voz cita** (`capture.py` devolve a caixa do texto), **três looks rotativos** e **política de clipe oficial** (curto, mudo, ≤ 30 %). Candidatos, do mais direto ao mais distante:

| Projeto | Como o kit ajuda | Observação |
|---|---|---|
| **explicavideos** (perfil `sem_avatar`, 2.23.11) | Versão sem avatar sem depender de gravar no HeyGen: a voz sai do Chatterbox local em minutos | Hoje a versão sem avatar ainda usa a voz do avatar gravado; aqui não há gravação nenhuma |
| **Vídeo de projeto/guia no portal** (repos `inematds/*`) | Cada repo novo ganha um vídeo de 2–5 min com prints reais do GitHub e do guia, sem custo de HeyGen | Encaixa no fim do `projetos-landing-guia` / `atualiza-portal` |
| **refazvideo** | Alternativa quando não há OK para avatar: mesmo roteiro, voz `nei` local, look `cinema` | Vídeo de base continua sem crédito escrito |
| **Notícia de ferramenta (INEMA.VIDEOS, lives4)** | "Saiu X" vira vídeo de 5–8 min no mesmo dia: pesquisa → roteiro → render, com print do anúncio | Bom para o volume diário sem gastar crédito de avatar |
| **Versões EN/ES** | `inema-traduz` no `script.txt` + `FV_LANG=en|es` — refaz voz e legenda sem regravar nada | ES segue a fila `fila_es.py` |
| **videos-cursos-inema** | Vídeo de trilha/módulo com print da página do curso e zoom no passo | Looks `ledger`/`reel` combinam com aula |
| **docflow / finviral (versão longa)** | Peças `stamp`, contador e `big_card` para números | Só onde o tema é ferramenta ou dado; documentário segue no docflow |
| **video-explicativo / faceless-explainer** | Mesma família (HTML → MP4); vale portar `capture.py` + caixas de texto para lá | Não substitui: esses são 1–3 min de conceito sem site para mostrar |

Não substitui: **r7ex / makeshorts / reel-edita** (9:16 com avatar e 7 etapas) nem o **explicavideo com avatar** quando o rosto do Nei é a proposta do vídeo.

---

## Estrutura

```
SKILL.md                    instruções que o Claude Code segue
PROFILE.md                  voz, chamada, visual e palavras proibidas do INEMA
setup.sh / requirements.txt instalação + autoteste (SELFTEST PASS)
scripts/fv.py               motor de cenas, tema INEMA, render e mixagem
scripts/tts.py, _align.py   voz local + tempo por palavra + nova geração da frase ruim
scripts/images.py           renders 3D (Codex pela assinatura; flux local de reserva)
scripts/capture.py          print de página inteira + caixas de texto
scripts/qc.py               QC técnico + folha de contato
templates/                  exemplo de 30 s, modelo de roteiro longo, job longo, peças dos looks cinema/ledger, telas de app
sfx/                        whoosh/pop/tick (desligados por padrão)
assets/proof/               prints opcionais para a chamada (página do inema.club, depoimentos)
```

## Pastas de trabalho
Cada vídeo fica em `~/projetos/output/video-sem-rosto/<data>-<slug>/` com `script.txt`, `vo.mp3`, `words.json`, `img/`, `cap/`, `clips/`, `job.py` e `out/`.

## Versão
`1.0.1` — 26/10/2026. Histórico em `CHANGELOG.md`.
