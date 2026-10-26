"""QC do vídeo final. Uso: python3 qc.py <video.mp4>
Confere 1920x1080, fps, bitrate ≥ 8 Mbps, loudness −14 LUFS ±1, true peak ≤ −1, quadros pretos; grava <video>_folha.jpg
(16 quadros) para OLHAR. Sai com código 1 se algo reprovar."""
import sys, json, re, subprocess

v = sys.argv[1]
pr = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
     "stream=codec_type,width,height,r_frame_rate:format=duration,bit_rate", "-of", "json", v]))
vs = next(s for s in pr["streams"] if s["codec_type"] == "video")
fps = eval(vs["r_frame_rate"]); dur = float(pr["format"]["duration"]); mbps = int(pr["format"]["bit_rate"]) / 1e6
ln = subprocess.run(["ffmpeg", "-hide_banner", "-i", v, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", ln)[-1]); tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", ln)[-1])
bd = subprocess.run(["ffmpeg", "-hide_banner", "-i", v, "-vf", "blackdetect=d=0.3:pix_th=0.05", "-an", "-f", "null", "-"],
                    capture_output=True, text=True).stderr
blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", bd)
folha = v.rsplit(".", 1)[0] + "_folha.jpg"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v, "-vf", f"fps=16/{dur:.2f},scale=480:-2,tile=4x4", "-frames:v", "1", folha], check=True)
checks = {
    "1920x1080": (vs["width"], vs["height"]) == (1920, 1080),
    f"fps {fps:.0f} (≥30)": fps >= 29.9,
    f"bitrate {mbps:.1f} Mbps (≥8)": mbps >= 8,
    f"loudness {lufs} LUFS (−14 ±1)": abs(lufs + 14) <= 1,
    f"true peak {tp} dBFS (≤ −1)": tp <= -0.9,
    f"quadros pretos: {len(blacks)}": not blacks,
}
for k, ok in checks.items(): print(("OK   " if ok else "FALHA") + " " + k)
print(f"duração {dur:.1f}s · folha: {folha}")
sys.exit(0 if all(checks.values()) else 1)
