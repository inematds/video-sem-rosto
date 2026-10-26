# FALHAS

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 2026-10-26 | setup.sh montava voice-refs/<caminho>.wav quando FV_VOICE era um caminho (instalação travava para quem é de fora) | `case *.wav)` + `FV_VOICE_DIR`, mesma regra no tts.py | prompt |
| 2026-10-25 | Teste de 40 s saiu a −16,2 LUFS (meta −14): loudnorm de 1 passada fica baixo e o pico da voz sintética segura o ganho | compressor leve + limitador antes do loudnorm em 2 passadas (`_loudnorm2`) → −14,3 | infra |
