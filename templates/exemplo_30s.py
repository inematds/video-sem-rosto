"""Vídeo sem rosto — teste de ~40 s (o próprio kit). Tempos = segundos da narração (words.json)."""
import sys, os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/video-sem-rosto/scripts"))
from fv import *
J = os.path.dirname(os.path.abspath(__file__)); I = lambda n: os.path.join(J, "img", n + ".png"); C = lambda n: os.path.join(J, "cap", n)
v = Video(J, "video-sem-rosto-teste")

# 1 gancho — escuro: nome do kit + claquete sem câmera
v.scene(0, 7.2, "dark",
    kicker("Kit INEMA · open source", 0.05, y=46, dark=True)
    + head("Vídeo *sem rosto*", 0.0, y=120, size=124, per_word=[0, .4, .5])
    + hero(I("d_clap"), 0.2, cy=600, w=900, dark=True)
    + chip("Sem câmera", 4.8, 470, 720, ico="video-off", size=40)
    + chip("Sem *avatar*", 5.96, 1450, 720, ico="user-x", accent=True, size=40))

# 2 link -> fonte oficial -> roteiro: print real + chips à direita
v.scene(7.2, 14.3, "cream",
    kicker("Exemplo · github.com/inematds/yt-pubx", 7.3, y=40)
    + browser(C("gh.png"), 7.3, 110, 130, 1040, 740, url="github.com/inematds/yt-pubx",
              scroll=[(10.4, 0), (12.2, 900)], zoom=[(7.6, 1, 0, 0), (9.6, 1.18, 0, 0)])
    + chip("O *link* da ferramenta", 8.2, 1250, 260, ico="link", anchor="left")
    + chip("Lê a fonte *oficial*", 10.49, 1250, 420, ico="book-open", anchor="left")
    + chip("Escreve o *roteiro*", 11.96, 1250, 580, ico="file-text", anchor="left"))

# 3 portão — cartão amarelo
v.scene(14.3, 21.4, "orange", big_card([("Você aprova.", 14.5), ("Depois, a *voz*.", 15.9), ("Na sua máquina.", 18.2)]))

# 4 cada frase vira uma cena — claro, quatro peças
v.scene(21.4, 29.2, "cream",
    title("Cada frase, *uma cena*", 21.6, y=120, size=100, per_word=[21.72, 21.88, 22.78, 22.86])
    + chip("Título", 23.48, 640, 400, ico="type", size=54)
    + chip("Print *real*", 24.10, 1280, 400, ico="monitor", size=54)
    + chip("Imagem 3D", 25.58, 640, 600, ico="box", size=54)
    + chip("Legenda *karaokê*", 27.0, 1280, 600, ico="captions", size=54))

# 5 saída — escuro, monitor + carimbo
v.scene(29.2, 36.6, "dark",
    head("Pronto para *publicar*", 29.3, y=110, size=104)
    + hero(I("d_monitor"), 29.2, cy=590, w=900, dark=True)
    + stamp("1080p · 60 FPS", 31.1, 1500, 760, size=70))

# 6 chamada — claro
v.scene(36.6, 42.6, "cream",
    title("Tá tudo no *inema.club*", 36.7, y=150, size=110)
    + tile(logo_src("github", "0c0c10"), 37.89, 760, 420, label="Kit no GitHub", dark=False)
    + chip("De *graça*", 40.89, 1200, 520, ico="gift", accent=True, size=44))

if __name__ == "__main__":
    if sys.argv[1:] == ["stills"]: print(v.stills())
    else: print(v.render())
