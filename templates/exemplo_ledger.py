"""Exemplo 2 — yt-pubx em ~35 s, look "ledger". Tempos = segundos da narração (words.json)."""
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/video-sem-rosto/scripts"))
sys.path.insert(0, os.path.expanduser("~/.claude/skills/video-sem-rosto/templates"))
from pieces_ledger import *
J = os.path.dirname(os.path.abspath(__file__)); C = lambda n: os.path.join(J, "cap", n)
v = Video(J, "exemplo-ytpubx-ledger", look="ledger")

# 1 nome da ferramenta
v.scene(0, 6.2, "navy",
    mono("GitHub · inematds/yt-pubx", 0.05, 110, 90, dark=True)
    + version("yt-pubx", 0.1, 110, 190, size=200, dark=True)
    + lhead("Publica no YouTube com *um comando*", 1.7, y=520, size=92, dark=True, per_word=[1.78, 3.0, 3.22, 3.52, 3.94, 4.08]))

# 2 o comando
v.scene(6.2, 11.0, "paper",
    lhead("Arquivo ou link + *contexto*", 6.3, y=100, size=92, per_word=[7.24, 7.82, 8.08, 8.4, 9.88])
    + term([("$ yt-pubx publicar aula.mp4 \\", 6.9), ('    --contexto "Aula 3 do curso X"', 9.3)], 6.5, 110, 330, w=1500, title="terminal"))

# 3 o que o Codex escreve
v.scene(11.0, 16.6, "navy",
    mono("Codex · pela assinatura", 11.05, 110, 90, dark=True)
    + lhead("Ele escreve *tudo*", 11.1, y=150, size=92, dark=True)
    + loglist([("Título", 12.35, "feat"), ("Descrição", 13.01, "feat"), ("Tags", 13.89, "feat"), ("Arte da *thumb*", 15.23, "feat")],
              110, 330, w=1100, dark=True, size=40))

# 4 publica — cartão de afirmação
v.scene(16.6, 23.6, "lime", statement([("Publica no canal.", 16.9), ("Público, não listado,", 19.3), ("privado ou *agendado*.", 21.14)], size=112))

# 5 na sua máquina
v.scene(23.6, 29.7, "paper",
    lhead("Sem chave de *API*", 23.7, y=100, size=92)
    + step(1, "Roda na *sua máquina*", 24.66, 110, 330)
    + step(2, "Usa a assinatura do Codex", 26.16, 110, 470)
    + step(3, "Nenhuma chave de *API* de modelo", 27.38, 110, 610))

# 6 chamada
v.scene(29.7, 35.4, "navy",
    lhead("Passo a passo no *inema.club*", 29.8, y=110, size=92, dark=True)
    + mono("Projeto aberto · GitHub", 30.8, 110, 260, dark=True)
    + browser(C("guia.png"), 30.2, 700, 330, 1100, 560, url="inematds.github.io/yt-pubx/guia/", scroll=[(31.5, 0), (34.5, 700)]))

if __name__ == "__main__":
    if sys.argv[1:] == ["stills"]: print(v.stills())
    else: print(v.render())
