"""Capture a real web page as a tall 1600-wide screenshot for animated 'screencast' scrolls, plus boxes of chosen text.
Usage: python3 capture.py <url> <out.png> ["text to locate" ...]  -> writes <out>.json {h, boxes:{text:[x,y,w,h]}}
Boxes are in page pixels, used to scroll to / zoom on / circle the exact thing the voice names."""
import sys, json
from playwright.sync_api import sync_playwright
url, out, finds = sys.argv[1], sys.argv[2], sys.argv[3:]
HIDE = """for (const el of document.querySelectorAll('body *')) { const s = getComputedStyle(el);
  if ((s.position==='fixed'||s.position==='sticky') && el.getBoundingClientRect().top > 120) el.remove();
  if (/consent|cookie|onetrust|gdpr|cmp|modal|newsletter/i.test((el.id||'')+' '+(el.className||'')) && s.position==='fixed') el.remove(); }"""
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1.5, color_scheme="light")
    try: pg.goto(url, wait_until="networkidle", timeout=25000)
    except Exception: pg.goto(url, wait_until="domcontentloaded", timeout=60000); pg.wait_for_timeout(5000)
    pg.wait_for_timeout(2500); pg.evaluate(HIDE)
    h = min(6000, pg.evaluate("document.documentElement.scrollHeight"))
    pg.screenshot(path=out, full_page=True, clip={"x": 0, "y": 0, "width": 1600, "height": h})
    boxes = {}
    for t in finds:
        b = pg.evaluate("""t => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            while (w.nextNode()) { const n = w.currentNode; if (n.textContent.trim() === t || n.textContent.includes(t)) {
              const r = document.createRange(); r.selectNodeContents(n); const b = r.getBoundingClientRect();
              if (b.width > 0 && b.height > 0) return [b.x, b.y + scrollY, b.width, b.height]; } } return null; }""", t)
        boxes[t] = b
    json.dump({"w": 1600, "h": h, "scale": 1.5, "boxes": boxes}, open(out.rsplit(".", 1)[0] + ".json", "w"), indent=1)
    print(h, boxes); br.close()
