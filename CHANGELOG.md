# CHANGELOG

## 1.0.1 — 26/10/2026
- 2º exemplo pronto: `templates/exemplo_ledger.py` (yt-pubx, look ledger, ~35 s).
- Correção: `pieces_ledger.py` calculava o `__all__` antes das funções, e o `from pieces_ledger import *` não trazia nenhuma peça.
- Guia e READMEs com os dois vídeos de exemplo tocando.

## 1.0.0 — 25/10/2026
- Kit de vídeo sem rosto 16:9 adaptado para o INEMA: voz local (Chatterbox `nei`) com tempo por palavra pelo Whisper local e nova geração da frase ruim; tema INEMA (preto/papel/amarelo, Sora/Inter); legenda karaokê escura; sem whoosh por padrão; loudnorm em 2 passadas com compressor (−14 LUFS); imagens pelo Codex da assinatura (flux local de reserva); `qc.py`; `setup.sh` com `.venv` próprio e autoteste; exemplo de ~40 s; modelo de roteiro longo em PT.
