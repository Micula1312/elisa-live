from __future__ import annotations

import argparse
import math
import random
import sys
import time
from pathlib import Path
import tkinter as tk

try:
    from PIL import Image, ImageTk, ImageOps
except ImportError:
    print("Manca Pillow. Installa con: py -m pip install pillow")
    raise

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
DEFAULT_SOURCE = Path(__file__).resolve().parents[1] / "web" / "public" / "feed"

class FloatingImage:
    def __init__(self, app, path: Path, index: int):
        self.app = app
        self.path = path
        self.win = tk.Toplevel(app.root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="black")
        self.phase = random.random() * math.tau
        self.speed = random.uniform(.65, 1.55)
        self.vx = random.choice([-1, 1]) * random.uniform(0.7, 2.4)
        self.vy = random.choice([-1, 1]) * random.uniform(0.55, 1.9)
        self.base_w = random.randint(180, 430)
        self.x = random.randint(0, max(1, app.sw - self.base_w))
        self.y = random.randint(0, max(1, app.sh - 300))
        self.label = tk.Label(self.win, bd=0, highlightthickness=0, bg="black")
        self.label.pack()
        self.src = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        self.photo = None
        self.last_size = (0, 0)
        self.win.bind("<Escape>", lambda _e: app.kill())
        self.win.bind("<Button-1>", lambda _e: self.kick())
        self.render(1.0)

    def kick(self):
        self.vx += random.uniform(-4, 4)
        self.vy += random.uniform(-4, 4)

    def render(self, scale: float):
        w = max(90, int(self.base_w * scale))
        ratio = self.src.height / max(1, self.src.width)
        h = max(70, int(w * ratio))
        max_h = int(self.app.sh * .72)
        if h > max_h:
            h = max_h
            w = max(90, int(h / ratio))
        size = (w, h)
        if size != self.last_size:
            img = self.src.copy()
            img.thumbnail(size, Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            self.label.configure(image=self.photo)
            self.last_size = size
        self.win.geometry(f"{self.last_size[0]}x{self.last_size[1]}+{int(self.x)}+{int(self.y)}")

    def update(self, t: float, chaos: float):
        pulse = 1 + math.sin(t * self.speed * 2.1 + self.phase) * (.025 + chaos * .12)
        jitter = chaos * 1.8
        self.x += self.vx * (1 + chaos * 1.8) + random.uniform(-jitter, jitter)
        self.y += self.vy * (1 + chaos * 1.8) + random.uniform(-jitter, jitter)
        w, h = self.last_size
        if self.x < 0 or self.x + w > self.app.sw:
            self.vx *= -1
            self.x = min(max(0, self.x), max(0, self.app.sw - w))
        if self.y < 0 or self.y + h > self.app.sh:
            self.vy *= -1
            self.y = min(max(0, self.y), max(0, self.app.sh - h))
        self.render(pulse)

    def close(self):
        try:
            self.win.destroy()
        except tk.TclError:
            pass

class ForestInvasion:
    def __init__(self, source: Path, max_images: int, interval: float):
        self.source = source
        self.max_images = max_images
        self.interval = interval
        self.root = tk.Tk()
        self.root.withdraw()
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        self.items: list[FloatingImage] = []
        self.paths = self.collect()
        random.shuffle(self.paths)
        self.started = time.perf_counter()
        self.next_spawn = self.started
        self.chaos = 0.12
        self.running = True
        self.root.bind_all("<Escape>", lambda _e: self.kill())
        self.root.bind_all("<space>", lambda _e: self.burst())
        self.root.bind_all("<Up>", lambda _e: self.more_chaos())
        self.root.bind_all("<Down>", lambda _e: self.less_chaos())

    def collect(self):
        if not self.source.exists():
            raise FileNotFoundError(f"Cartella non trovata: {self.source}")
        return [p for p in self.source.rglob("*") if p.is_file() and p.suffix.lower() in EXTS]

    def spawn(self):
        if not self.paths or len(self.items) >= self.max_images:
            return
        path = self.paths[len(self.items) % len(self.paths)]
        try:
            self.items.append(FloatingImage(self, path, len(self.items)))
        except Exception as exc:
            print(f"skip {path.name}: {exc}")

    def burst(self):
        for _ in range(min(8, self.max_images - len(self.items))):
            self.spawn()
        self.chaos = min(1.0, self.chaos + .12)

    def more_chaos(self):
        self.chaos = min(1.0, self.chaos + .1)

    def less_chaos(self):
        self.chaos = max(0.0, self.chaos - .1)

    def tick(self):
        if not self.running:
            return
        now = time.perf_counter()
        if now >= self.next_spawn and len(self.items) < self.max_images:
            self.spawn()
            # invasion accelerates gradually
            progress = len(self.items) / max(1, self.max_images)
            self.next_spawn = now + max(.12, self.interval * (1 - progress * .72))
        t = now - self.started
        for item in self.items:
            item.update(t, self.chaos)
        self.root.after(16, self.tick)

    def kill(self):
        self.running = False
        for item in self.items:
            item.close()
        self.root.destroy()

    def run(self):
        if not self.paths:
            print(f"Nessuna immagine trovata in {self.source}")
            return 1
        print(f"FOREST INVASION — {len(self.paths)} media trovati")
        print("SPACE = burst | ↑/↓ = chaos | ESC = KILL")
        self.tick()
        self.root.mainloop()
        return 0

def main():
    parser = argparse.ArgumentParser(description="ELISA — Forest Invasion")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--max", type=int, default=42)
    parser.add_argument("--interval", type=float, default=1.6)
    args = parser.parse_args()
    return ForestInvasion(args.source, max(1, args.max), max(.1, args.interval)).run()

if __name__ == "__main__":
    sys.exit(main())
