"""
Capstone Dashboard - Make the Computer Draw a Box
Name: Ekta Singh   Roll no: 2501730327

Run:   python dashboard.py
Open:  http://localhost:8000
Uses ../PartB_Assembler/assembler.py and ../PartC_Box/Box.asm. No pip install needed.

The dashboard assembles Box.asm with YOUR assembler (assembler.py), loads the
result into a small Hack CPU emulator, and shows the 512x256 screen. Hold a key
(or the on-screen button) and the box appears; release and it disappears.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PART_B = os.path.join(ROOT, "PartB_Assembler")   # assembler.py, symbols.txt
PART_C = os.path.join(ROOT, "PartC_Box")         # Box.asm, Box.hack
sys.path.insert(0, PART_B)

from assembler import assemble, symbols_text, AsmError

NAME = "Ekta Singh"
ROLL_NO = "2501730327"
K = int(ROLL_NO[-2:])                       # K = last two digits of roll number
BOX_ROW = K
BOX_ROWS = 20
BOX_WIDTH = 16 * ((K % 4) + 1)

HERE = os.path.dirname(os.path.abspath(__file__))
SCREEN, KBD = 16384, 24576


# ---- Hack CPU emulator -------------------------------------------------------
class HackCPU:
    def __init__(self, rom):
        self.rom = rom
        self.reset()

    def reset(self):
        self.ram = [0] * (KBD + 1)
        self.pc = self.a = self.d = 0
        self.cycles = 0

    @staticmethod
    def _alu(x, y, c):
        zx, nx, zy, ny, f, no = c
        if zx: x = 0
        if nx: x = ~x
        if zy: y = 0
        if ny: y = ~y
        out = (x + y) if f else (x & y)
        if no: out = ~out
        out &= 0xFFFF
        return out - 0x10000 if out >= 0x8000 else out

    def run(self, n):
        rom, ram = self.rom, self.ram
        size = len(rom)
        for _ in range(n):
            if self.pc >= size:
                self.pc = 0
            ins = rom[self.pc]
            if ins >> 15 == 0:                      # A-instruction
                self.a = ins
                self.pc += 1
            else:                                   # C-instruction
                a = (ins >> 12) & 1
                c = [(ins >> s) & 1 for s in (11, 10, 9, 8, 7, 6)]
                dest, jump = (ins >> 3) & 7, ins & 7
                old_a = self.a
                y = ram[old_a % len(ram)] if a else old_a
                out = self._alu(self.d, y, c)
                if dest & 1: ram[old_a % len(ram)] = out   # M
                if dest & 2: self.d = out                  # D
                if dest & 4: self.a = out & 0xFFFF         # A
                take = (jump & 4 and out < 0) or (jump & 2 and out == 0) or (jump & 1 and out > 0)
                self.pc = old_a if take else self.pc + 1
            self.cycles += 1

    def screen_words(self):
        return [w & 0xFFFF for w in self.ram[SCREEN:KBD]]


# ---- assemble Box.asm with our own assembler ----------------------------------
with open(os.path.join(PART_C, "Box.asm")) as f:
    ASM_TEXT = f.read()
try:
    RESULT = assemble(ASM_TEXT)
except AsmError as e:
    raise SystemExit(f"Assembler error: {e}")
HACK_LINES = RESULT["binary"]
SYMBOLS = symbols_text(RESULT)
with open(os.path.join(PART_C, "Box.hack"), "w") as f:
    f.write("\n".join(HACK_LINES) + "\n")
with open(os.path.join(PART_B, "symbols.txt"), "w") as f:
    f.write(SYMBOLS)

CPU = HackCPU([int(line, 2) for line in HACK_LINES])


# ---- web page ------------------------------------------------------------------
PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Capstone Dashboard - __NAME__</title>
<style>
  :root { --bg:#f4f6fb; --card:#fff; --text:#1c2333; --muted:#6b7385; --accent:#4f46e5; --line:#e3e7f0; --ok:#16a34a; }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#0f1220; --card:#181c30; --text:#eef0f8; --muted:#9aa2ba; --accent:#818cf8; --line:#262b45; --ok:#4ade80; }
  }
  * { box-sizing:border-box; }
  body { margin:0; font-family:system-ui,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--text); }
  header { background:var(--accent); color:#fff; padding:18px 28px; font-size:20px; font-weight:600; }
  header small { display:block; font-weight:400; opacity:.85; font-size:13px; margin-top:2px; }
  main { max-width:1000px; margin:24px auto; padding:0 16px; display:grid; gap:20px; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:20px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:16px; }
  .label { font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); }
  .value { font-size:22px; font-weight:600; margin-top:4px; }
  h2 { margin:0 0 12px; font-size:16px; }
  .bar { display:flex; flex-wrap:wrap; gap:12px; align-items:center; margin-bottom:14px; }
  button { background:var(--accent); color:#fff; border:0; padding:11px 20px; border-radius:8px; cursor:pointer; font-weight:600; font-size:14px; user-select:none; }
  button.secondary { background:transparent; color:var(--accent); border:1px solid var(--accent); }
  .status { font-weight:600; }
  .status.on { color:var(--ok); }
  canvas { width:100%; max-width:1024px; background:#fff; border:2px solid var(--line); border-radius:6px; image-rendering:pixelated; display:block; }
  .tabs { display:flex; gap:8px; margin-bottom:10px; }
  .tabs button { padding:7px 14px; }
  pre { margin:0; padding:14px; background:var(--bg); border:1px solid var(--line); border-radius:8px; overflow:auto; max-height:360px; font-size:13px; line-height:1.45; }
  .meta { color:var(--muted); font-size:13px; margin-top:8px; }
</style>
</head>
<body>
<header>Capstone Dashboard<small>Nand to Tetris - I (ETCNTC301) | K.R. Mangalam University</small></header>
<main>
  <section class="card grid">
    <div><div class="label">Name</div><div class="value">__NAME__</div></div>
    <div><div class="label">Roll No</div><div class="value">__ROLL__</div></div>
    <div><div class="label">K</div><div class="value">__K__</div></div>
    <div><div class="label">Box</div><div class="value" style="font-size:16px">row __ROW__, __ROWS__ rows tall, __W__ px wide</div></div>
  </section>

  <section class="card">
    <h2>Hack Computer Screen (running Box.hack)</h2>
    <div class="bar">
      <button id="hold">Hold to press a key</button>
      <button class="secondary" id="reset">Reset computer</button>
      <span>Keyboard: <span class="status" id="status">no key</span></span>
    </div>
    <canvas id="screen" width="512" height="256"></canvas>
    <div class="meta" id="meta">Hold the button (or any key on your keyboard) to draw the box.</div>
  </section>

  <section class="card">
    <h2>Your files</h2>
    <div class="tabs">
      <button class="secondary" data-t="asm">Box.asm</button>
      <button class="secondary" data-t="hack">Box.hack</button>
      <button class="secondary" data-t="sym">symbols.txt</button>
    </div>
    <pre id="code"></pre>
  </section>
</main>
<script>
const $ = id => document.getElementById(id);
let pressed = false, busy = false, files = {};

function setKey(v) {
  pressed = v;
  $('status').textContent = v ? 'key pressed (75)' : 'no key';
  $('status').className = 'status' + (v ? ' on' : '');
}
const hold = $('hold');
['mousedown','touchstart'].forEach(e => hold.addEventListener(e, ev => { ev.preventDefault(); setKey(true); }));
['mouseup','mouseleave','touchend'].forEach(e => hold.addEventListener(e, () => setKey(false)));
window.addEventListener('keydown', () => setKey(true));
window.addEventListener('keyup', () => setKey(false));
$('reset').onclick = async () => { await fetch('/api/reset'); tick(); };

const ctx = $('screen').getContext('2d');
async function tick() {
  if (busy) return; busy = true;
  try {
    const r = await fetch('/api/run?key=' + (pressed ? 75 : 0) + '&cycles=12000');
    const d = await r.json();
    const img = ctx.createImageData(512, 256);
    let lit = 0;
    for (let i = 0; i < d.screen.length; i++) {
      const w = d.screen[i]; if (!w) continue;
      const base = (Math.floor(i / 32) * 512) + (i % 32) * 16;
      for (let b = 0; b < 16; b++) if ((w >> b) & 1) {
        const p = (base + b) * 4;
        img.data[p+3] = 255; lit++;
      }
    }
    ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, 512, 256);
    const off = document.createElement('canvas'); off.width = 512; off.height = 256;
    off.getContext('2d').putImageData(img, 0, 0);
    ctx.drawImage(off, 0, 0);
    $('meta').textContent = lit + ' pixels black | PC = ' + d.pc + ' | cycles run = ' + d.cycles;
  } catch (e) { $('meta').textContent = 'Server not reachable'; }
  busy = false;
}
setInterval(tick, 150);

function show(t) { $('code').textContent = files[t]; }
document.querySelectorAll('.tabs button').forEach(b => b.onclick = () => show(b.dataset.t));
fetch('/api/files').then(r => r.json()).then(d => { files = d; show('asm'); });
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, body, ctype):
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            html = (PAGE.replace("__NAME__", NAME).replace("__ROLL__", ROLL_NO)
                        .replace("__K__", str(K)).replace("__ROW__", str(BOX_ROW))
                        .replace("__ROWS__", str(BOX_ROWS)).replace("__W__", str(BOX_WIDTH)))
            self._send(html, "text/html; charset=utf-8")
        elif url.path == "/api/run":
            q = parse_qs(url.query)
            try:
                key = int(q.get("key", ["0"])[0])
                cycles = min(int(q.get("cycles", ["12000"])[0]), 50000)
            except ValueError:
                key, cycles = 0, 12000
            CPU.ram[KBD] = key
            CPU.run(cycles)
            self._send(json.dumps({"screen": CPU.screen_words(), "pc": CPU.pc,
                                   "cycles": CPU.cycles}), "application/json")
        elif url.path == "/api/reset":
            CPU.reset()
            self._send("{}", "application/json")
        elif url.path == "/api/files":
            self._send(json.dumps({"asm": ASM_TEXT, "hack": "\n".join(HACK_LINES),
                                   "sym": SYMBOLS}), "application/json")
        else:
            self.send_error(404)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"Assembled Box.asm -> Box.hack ({len(HACK_LINES)} instructions), symbols.txt saved")
    print("Dashboard running at http://localhost:8000  (Ctrl+C to stop)")
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
