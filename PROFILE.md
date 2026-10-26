# Perfil do criador (a skill lê antes de cada vídeo)

- **Criador:** Nei Maldaner — INEMA (voz e fatos dele: `~/projetos/wifi/PERFIL-NEI-MALDANER.md`; não inventar além).
- **Canal padrão:** publicação pelo `yt-pubx` (`~/projetos/yt-pubx`), canal escolhido pelo tema (`./yt-pubx canais`). Sem canal dito: `lives1` (só PT).
- **Voz:** local, Chatterbox do inemavox com a voz clonada `nei` (`FV_VOICE=nei`; também `nei2`, `nei3`, `nei4`). Nunca `rachel` em PT. Nenhuma API de voz.
- **Idioma:** PT-BR. EN/ES = traduzir o roteiro com `inema-traduz` e gerar de novo (`FV_LANG=en|es`); vídeo ES vai para a fila `fila_es.py`.
- **Chamada (≈3:00 e no fim), sempre ligada ao tema do vídeo:** "Se você quer o passo a passo de <tema>, como <o fluxo deste vídeo>, está tudo no **INEMA.CLUB**, de graça." Link: `https://inema.club` (`FV_OFFER_URL=inema.club`).
  - Fim: resumo curto + "tá tudo no inema.club". Sem "comenta X", sem preço, sem nota numérica.
- **Prova na tela (opcional):** prints reais em `assets/proof/review_01.png …` e `assets/proof/offer_page.png` (página do inema.club). Só print real, nada montado.
- **Imagens:** Codex CLI image_gen pela assinatura (padrão). Reserva: `FV_IMG=flux` (flux2-klein local). Luz neutra, sem amarelado; robô = humanoide industrial com visor escuro.
- **Visual:** tema `inema` (padrão do motor): preto `#0c0c10`, papel claro, amarelo `#FACC15` (no claro só como preenchimento/marca-texto), títulos Sora, corpo Inter. Regras completas: `~/projetos/inema-design/DESIGN.md` e `video/style.md`.
- **Som:** só voz (−14 LUFS) e, se houver, trilha baixa do inemavox. Sem whoosh nem efeito no meio (`FV_WHOOSH=1` só se o Nei pedir).
- **Fonte:** o vídeo não escreve "Fonte: …" de material de terceiros que tenha servido de base. Trecho de vídeo oficial de produto leva só o crédito curto do canal oficial no canto.
- **Palavras que não uso:** revolucionar, "Imagine que…", "Pense num…", "Se você…" na abertura, "Neste momento…", "deixa eu te contar", "isso muda tudo". Ver `~/projetos/inema-design/regras/texto.md`.
