"""
M' agapaei? - pixel-art windowsill flower  (9:16, made for TikTok)
------------------------------------------------------------------
Click a petal to pluck it (or SPACE)
R = new flower   L = Greek / English   H = hide hints   M = mute   ESC = quit
Requires:  pip install pygame
"""
import math
import random
import sys
from array import array

import pygame

# ---------------------------------------------------------------- settings
W, H = 160, 284          # low-res canvas (9:16)
SCALE = 3                # window = 480 x 852  (lower to 2 if it doesn't fit)
FPS = 60

WIN_CX, WIN_CY, WIN_R = 80, 100, 56     # arched window: semicircle centre/radius
WIN_L, WIN_R_X, WIN_B = 24, 136, 222    # window rectangle part
SILL_Y = 226

FLOWER_X, FLOWER_Y = 80, 130
CENTER_R = 7
PETAL_A, PETAL_B = 12.5, 5.4
PETAL_DIST = CENTER_R + 10

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

# ---- personal messages shown at the end (edit freely) ----
WIN_MSG = ["ΕΙΔΕΣ ΑΝΝΑ;", "Σ'ΑΓΑΠΑΩ ♥"]
LOSE_MSG = ["OOPS!", "ΞΑΝΑ", "ΠΡΟΣΠΑΘΗΣΕ"]

TEXTS = {
    "gr": {"yes": ["Μ'ΑΓΑΠΑΕΙ"], "no": ["ΔΕΝ", "Μ'ΑΓΑΠΑΕΙ"]},
    "en": {"yes": ["LOVES ME"], "no": ["LOVES ME", "NOT"]},
}
YES_COL = (255, 158, 192)
NO_COL = (185, 168, 255)
INK = (24, 12, 30)


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def dither(x, y, t):
    return t * 16 > BAYER[int(y) % 4][int(x) % 4] + 0.5


# ---------------------------------------------------------------- pixel font (5x7, variable width)
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["111", "010", "010", "010", "010", "010", "111"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "G": ["01111", "10000", "10000", "10011", "10001", "10001", "01111"],
    "Γ": ["11111", "10000", "10000", "10000", "10000", "10000", "10000"],
    "Δ": ["00100", "01010", "01010", "10001", "10001", "10001", "11111"],
    "Π": ["11111", "10001", "10001", "10001", "10001", "10001", "10001"],
    "'": ["11", "11", "01", "10", "00", "00", "00"],
    "?": ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    " ": ["000"] * 7,
    "Σ": ["11111", "10000", "01000", "00100", "01000", "10000", "11111"],
    "Ω": ["01110", "10001", "10001", "10001", "01010", "01010", "11011"],
    "Ξ": ["11111", "00000", "00000", "01110", "00000", "00000", "11111"],
    "Θ": ["01110", "10001", "10001", "11111", "10001", "10001", "01110"],
    "Λ": ["00100", "01010", "01010", "10001", "10001", "10001", "10001"],
    ";": ["00", "11", "11", "00", "11", "01", "10"],
    "!": ["1", "1", "1", "1", "1", "0", "1"],
    "♥": ["01010", "11111", "11111", "11111", "01110", "00100", "00000"],
}
# Greek capitals that look like Latin ones
for g, l in zip("ΑΕΗΙΚΜΝΟΡΤΒΖΥΧ", "AEHIKMNOPTBZYX"):
    FONT[g] = FONT.get(l, FONT[" "])
FONT["K"] = ["10001", "10010", "10100", "11000", "10100", "10010", "10001"]
FONT["Κ"] = FONT["K"]


def glyph(ch):
    return FONT.get(ch, FONT[" "])


def text_width(text, scale):
    return sum((len(glyph(c)[0]) + 1) * scale for c in text) - scale


def draw_text(surf, text, x, y, scale, color, outline=INK):
    pix = []
    cx = x
    for ch in text:
        g = glyph(ch)
        for gy, row in enumerate(g):
            for gx, c in enumerate(row):
                if c == "1":
                    pix.append((cx + gx * scale, y + gy * scale))
        cx += (len(g[0]) + 1) * scale
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1),
                   (0, 2), (1, 2), (-1, 2)):
        for px, py in pix:
            surf.fill(outline, (px + ox, py + oy, scale, scale))
    light = tuple(min(255, c + 50) for c in color)
    for px, py in pix:
        surf.fill(color, (px, py, scale, scale))
        if scale > 1:
            surf.fill(light, (px, py, scale, 1))


# ---------------------------------------------------------------- sound (synthesised, no files)
class Sfx:
    def __init__(self):
        self.on = True
        self.ok = False
        try:
            pygame.mixer.init()
            self.rate, size, self.ch = pygame.mixer.get_init()
            self.ok = abs(size) == 16
        except Exception:
            pass
        if self.ok:
            self.pop = self._make(self._pop())
            self.yes = self._make(self._arp([523, 659, 784, 1047, 1319], 0.11, 0.35))
            self.no = self._make(self._arp([392, 349, 311, 262], 0.18, 0.3))
            self.thunder = self._make(self._thunder())

    def _make(self, samples):
        a = array("h")
        for s in samples:
            v = int(max(-1, min(1, s)) * 12000)
            for _ in range(self.ch):
                a.append(v)
        return pygame.mixer.Sound(buffer=a.tobytes())

    def _pop(self):
        n = int(self.rate * 0.09)
        out, ph = [], 0.0
        for i in range(n):
            t = i / n
            f = 1100 - 700 * t
            ph += 2 * math.pi * f / self.rate
            out.append(math.sin(ph) * (1 - t) ** 2)
        return out

    def _arp(self, notes, step, tail):
        n = int(self.rate * (step * len(notes) + tail))
        out = [0.0] * n
        for k, f in enumerate(notes):
            start = int(k * step * self.rate)
            for i in range(int((step + tail) * self.rate)):
                if start + i >= n:
                    break
                t = i / self.rate
                env = math.exp(-t * 7)
                out[start + i] += (math.sin(2 * math.pi * f * t) +
                                   0.3 * math.sin(4 * math.pi * f * t)) * env * 0.45
        return out

    def _thunder(self):
        n = int(self.rate * 1.2)
        out, v = [], 0.0
        rnd = random.Random(1)
        for i in range(n):
            v += (rnd.uniform(-1, 1) - v) * 0.04       # crude low-pass
            t = i / n
            out.append(v * 3.5 * (min(1, t * 20)) * (1 - t) ** 1.5)
        return out

    def play(self, name):
        if self.ok and self.on:
            getattr(self, name).play()


# ---------------------------------------------------------------- sprites
P_LIGHT = hexc("#fff0f5")
P_SOFT = hexc("#ffc6da")
P_MID = hexc("#ff93b8")
P_DEEP = hexc("#e25e90")
P_LINE = hexc("#9a3563")
P_GRAY = (hexc("#d9d0dc"), hexc("#b7aabd"), hexc("#958aa0"), hexc("#7a6d86"), hexc("#4b4058"))

_cache = {}


def petal_sprite(angle, squash=1.0, gray=False):
    key = (round(angle / (2 * math.pi) * 64) % 64, squash, gray)
    if key in _cache:
        return _cache[key]
    ang = key[0] / 64 * 2 * math.pi
    a, b = PETAL_A, PETAL_B * squash
    size = int(a * 2 + 4)
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size / 2
    ca, sa = math.cos(ang), math.sin(ang)
    light, soft, mid, deep, line = P_GRAY if gray else (P_LIGHT, P_SOFT, P_MID, P_DEEP, P_LINE)

    def shape(dx, dy):
        u = dx * ca + dy * sa
        v = -dx * sa + dy * ca
        # teardrop: narrower near the flower centre
        bb = b * (0.55 + 0.45 * min(1, (u + a) / (a * 1.1)))
        d = (u / a) ** 2 + (v / bb) ** 2
        # little notch at the tip (cosmos-style)
        if u > a * 0.7 and abs(v) < (u - a * 0.7) * 1.1:
            d = 2
        return d, u, v

    for py in range(size):
        for px in range(size):
            dx, dy = px + 0.5 - c, py + 0.5 - c
            d, u, v = shape(dx, dy)
            if d > 1:
                continue
            if any(shape(dx + ox, dy + oy)[0] > 1 for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                col = line
            else:
                t = (u + a) / (2 * a)          # 0 at base, 1 at tip
                if t < 0.3:
                    col = light
                elif t < 0.5:
                    col = soft if dither(px, py, (t - 0.3) / 0.2) else light
                elif t < 0.75:
                    col = mid if dither(px, py, (t - 0.5) / 0.25) else soft
                else:
                    col = mid
                if d > 0.72 and v > 0:
                    col = deep
            s.set_at((px, py), col)
    _cache[key] = s
    return s


def heart_sprite(rows, col, hi, line=None):
    s = pygame.Surface((len(rows[0]), len(rows)), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "X":
                s.set_at((x, y), col)
            elif ch == "H":
                s.set_at((x, y), hi)
            elif ch == "O" and line:
                s.set_at((x, y), line)
    return s


SMALL_HEART = [".XX.XX.", "XHXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]
BIG_HEART = [".OOO...OOO.",
             "OXXXO.OXXXO",
             "OXHHXOXXXXO",
             "OXHXXXXXXXO",
             "OXXXXXXXXXO",
             ".OXXXXXXXO.",
             "..OXXXXXO..",
             "...OXXXO...",
             "....OXO....",
             ".....O....."]


# ---------------------------------------------------------------- scenery
def in_window(x, y, grow=0):
    if WIN_L - grow <= x <= WIN_R_X + grow and WIN_CY <= y <= WIN_B + grow:
        return True
    return y < WIN_CY and math.hypot(x - WIN_CX, y - WIN_CY) <= WIN_R + grow


def build_outside():
    s = pygame.Surface((W, H))
    sky = [hexc(c) for c in ("#22113f", "#3b1a5c", "#62276f", "#963878",
                             "#c94e74", "#ea7262", "#ffa463")]
    top, bot = 40, 215
    for y in range(H):
        t = max(0, min(1, (y - top) / (bot - top))) * (len(sky) - 1)
        i = min(int(t), len(sky) - 2)
        for x in range(W):
            s.set_at((x, y), sky[i + 1] if dither(x, y, t - i) else sky[i])
    # setting sun + glow
    sx, sy, sr = 108, 182, 15
    for y in range(sy - 34, sy + 1):
        for x in range(sx - 34, sx + 35):
            d = math.hypot(x - sx, y - sy)
            if d <= sr:
                col = hexc("#ffe6a0") if d < sr - 3 else hexc("#ffc977")
                if d > sr - 3 and (y // 2) % 2 == 0 and y > sy - 9:
                    col = hexc("#ff9a5c")      # retro stripes on the sun
                s.set_at((x, y), col)
            elif d < 34 and dither(x, y, (1 - (d - sr) / 19) ** 1.7 * 0.7):
                s.set_at((x, y), hexc("#ffb27a"))
    # wispy clouds
    rnd = random.Random(5)
    for cy, cx, ln in ((88, 40, 50), (120, 95, 40), (150, 30, 36), (70, 92, 30)):
        for k in range(ln):
            for dy in range(3):
                x = cx + k - ln // 2 + dy * 2
                if 0 <= x < W and dither(x, cy + dy, 0.6 - abs(k - ln / 2) / ln):
                    s.set_at((x, cy + dy), hexc("#e47a8e") if dy == 0 else hexc("#b44f7f"))
    # skyline: back layer then front layer
    lights = []
    for layer, (col, lo, hi, lit) in enumerate(((hexc("#4a2052"), 168, 196, hexc("#c97a7a")),
                                                 (hexc("#1d0f2b"), 182, 210, hexc("#ffcf7a")))):
        x = rnd.randint(-10, 0)
        while x < W:
            w = rnd.randint(9, 20)
            top_y = rnd.randint(lo, hi)
            for xx in range(max(0, x), min(W, x + w)):
                for yy in range(top_y, WIN_B + 2):
                    s.set_at((xx, yy), col)
            if rnd.random() < 0.3:          # antenna
                ax = x + w // 2
                for yy in range(top_y - 6, top_y):
                    if 0 <= ax < W:
                        s.set_at((ax, yy), col)
            for wy in range(top_y + 3, WIN_B, 4):
                for wx in range(x + 2, x + w - 2, 3):
                    if 0 <= wx < W and rnd.random() < 0.35:
                        s.set_at((wx, wy), lit)
                        if layer == 1:
                            lights.append((wx, wy))
            x += w + rnd.randint(0, 3)
    return s, lights


def build_room():
    """Wall + window frame + sill, with the glass area transparent."""
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    wall, wall2, wall_d = hexc("#2c1c36"), hexc("#35233f"), hexc("#1d1226")
    frame, frame_hi, frame_lo = hexc("#e6d1b6"), hexc("#fff1dc"), hexc("#a88d75")
    for y in range(H):
        for x in range(W):
            if in_window(x, y):
                continue
            if in_window(x, y, 4):
                # frame ring: highlight on the inner edge, shadow on the outer edge
                if not in_window(x, y, 1):
                    col = frame_hi if (x < WIN_CX) else frame
                else:
                    col = frame
                if not in_window(x, y, 3):
                    col = frame_lo
                s.set_at((x, y), col)
                continue
            # striped wallpaper + vignette
            col = wall2 if (x // 4) % 3 == 0 and dither(x, y, 0.5) else wall
            edge = max(abs(x - W / 2) / (W / 2), abs(y - H / 2) / (H / 2))
            if dither(x, y, max(0, edge - 0.6) * 2.2):
                col = wall_d
            s.set_at((x, y), col)
    # warm light spilling on the wall under the window
    for y in range(SILL_Y + 8, H):
        for x in range(W):
            f = max(0, 1 - abs(x - 80) / 70) * max(0, 1 - (y - SILL_Y - 8) / 50) * 0.45
            if dither(x, y, f):
                s.set_at((x, y), hexc("#4a2b46"))
    # sill
    for x in range(10, W - 10):
        s.set_at((x, SILL_Y - 1), frame_hi)
        for y in range(SILL_Y, SILL_Y + 3):
            s.set_at((x, y), frame)
        for y in range(SILL_Y + 3, SILL_Y + 9):
            s.set_at((x, y), frame_lo if not dither(x, y, 0.3) else frame)
        s.set_at((x, SILL_Y + 9), hexc("#5f4b46"))
        for y in range(SILL_Y + 10, SILL_Y + 13):   # shadow under sill
            if dither(x, y, 0.6 - (y - SILL_Y - 10) * 0.2):
                s.set_at((x, y), wall_d)
    return s


def build_pot():
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    rim, body, shade, hi, dark = (hexc(c) for c in ("#e9875a", "#c95f39", "#9b4529", "#f6aa7c", "#6e2d1c"))
    top, bot = 203, SILL_Y
    for y in range(top, bot):
        t = (y - top) / (bot - top)
        half = 14 - 4 * t
        for x in range(int(80 - half), int(80 + half) + 1):
            rel = (x - (80 - half)) / (2 * half)
            col = body
            if rel > 0.68 and dither(x, y, (rel - 0.68) * 3):
                col = shade
            if 0.15 < rel < 0.24:
                col = hi
            if rel > 0.93 or y == bot - 1:
                col = dark
            s.set_at((x, y), col)
    for y in range(top - 5, top):
        for x in range(63, 98):
            col = rim
            if y == top - 5:
                col = hi
            elif y == top - 1 or x in (63, 97):
                col = shade
            s.set_at((x, y), col)
    # little heart painted on the pot
    hs = heart_sprite(SMALL_HEART, hexc("#fff0dc"), hexc("#ffffff"))
    s.blit(hs, (77, 212))
    return s


# ---------------------------------------------------------------- game objects
class Petal:
    def __init__(self, angle):
        self.angle = angle
        self.x = self.y = 0.0
        self.state = "on"
        self.t = 0
        self.phase = random.random() * 6.28
        self.vx = self.vy = self.spin = 0.0
        self.land_y = 0.0

    def hit(self, mx, my):
        dx, dy = mx - self.x, my - self.y
        u = dx * math.cos(self.angle) + dy * math.sin(self.angle)
        v = -dx * math.sin(self.angle) + dy * math.cos(self.angle)
        return (u / (PETAL_A + 1)) ** 2 + (v / (PETAL_B + 1.5)) ** 2 <= 1

    def pluck(self):
        self.state = "fall"
        self.vx = math.cos(self.angle) * 1.1
        self.vy = math.sin(self.angle) * 0.8 - 1.0
        self.spin = random.choice((-1, 1)) * random.uniform(0.05, 0.1)
        self.land_y = SILL_Y - random.uniform(1, 3)

    def update(self):
        if self.state != "fall":
            return
        self.t += 1
        self.vy = min(self.vy + 0.03, 0.75)
        self.vx *= 0.975
        self.x += self.vx + math.sin(self.t * 0.07 + self.phase) * 0.5
        self.x = max(16, min(W - 16, self.x))
        self.y += self.vy
        self.angle += self.spin
        if self.y >= self.land_y:
            self.state = "ground"
            self.y = self.land_y
            self.angle = random.uniform(-0.25, 0.25) + random.choice((0, math.pi))

    def draw(self, surf, gray=False):
        spr = petal_sprite(self.angle, 0.6 if self.state == "ground" else 1.0, gray)
        surf.blit(spr, (round(self.x - spr.get_width() / 2), round(self.y - spr.get_height() / 2)))


class Game:
    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption("loves me?")
        self.win = pygame.display.set_mode((W * SCALE, H * SCALE))
        self.buf = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        self.sfx = Sfx()
        self.outside, self.city_lights = build_outside()
        self.room = build_room()
        self.pot = build_pot()
        self.small_hearts = [heart_sprite(SMALL_HEART, hexc("#ff5d8f"), hexc("#ffd3e0")),
                             heart_sprite(SMALL_HEART, hexc("#ff9fbf"), hexc("#fff2f6"))]
        self.big_heart = heart_sprite(BIG_HEART, hexc("#ff4f86"), hexc("#ffd3e0"), hexc("#7a1f45"))
        self.lang = "en"
        self.show_hints = True
        self.frame = 0
        self.reset()

    def reset(self):
        n = random.randint(7, 12)
        off = random.random() * 6.28
        self.petals = [Petal(off + i * 2 * math.pi / n + random.uniform(-0.07, 0.07)) for i in range(n)]
        self.plucked = 0
        self.loves = None
        self.text_t = 0
        self.done = False
        self.end_t = 0
        self.sparks = []
        self.floaters = []
        self.flash = 0
        self.glass = [[random.uniform(WIN_L, WIN_R_X), random.uniform(50, WIN_B),
                       random.uniform(0.02, 0.15), random.randint(0, 200)] for _ in range(28)]
        self.rain = [[random.uniform(0, W), random.uniform(40, WIN_B)] for _ in range(45)]
        self.rain_amount = 45

    def remaining(self):
        return [p for p in self.petals if p.state == "on"]

    def pluck(self, p):
        p.pluck()
        self.plucked += 1
        self.loves = self.plucked % 2 == 1
        self.text_t = 0
        self.sfx.play("pop")
        for _ in range(8):
            a = random.random() * 6.28
            sp = random.uniform(0.4, 1.3)
            self.sparks.append([p.x, p.y, math.cos(a) * sp, math.sin(a) * sp, random.randint(12, 24)])
        if not self.remaining():
            self.done = True
            self.end_t = 0

    def click(self, mx, my):
        if self.done:
            self.reset()
            return
        for p in reversed(self.remaining()):
            if p.hit(mx, my):
                self.pluck(p)
                return

    # ------------------------------------------------------------
    def update(self):
        self.frame += 1
        self.text_t += 1
        for p in self.petals:
            p.update()
        for s in self.sparks:
            s[0] += s[2]; s[1] += s[3]; s[2] *= 0.92; s[3] *= 0.92; s[4] -= 1
        self.sparks = [s for s in self.sparks if s[4] > 0]

        # weather
        if self.done:
            self.end_t += 1
            if self.end_t == 25:
                self.sfx.play("yes" if self.loves else "no")
            if self.loves:
                self.rain_amount = max(0, self.rain_amount - 0.5)
                if self.end_t > 20 and self.frame % 7 == 0:
                    self.floaters.append([FLOWER_X + random.uniform(-10, 10), FLOWER_Y,
                                          random.random() * 6.28, random.uniform(.3, .55),
                                          random.randint(0, 1)])
            else:
                self.rain_amount = min(110, self.rain_amount + 1)
                if self.end_t > 40 and random.random() < 0.006 and self.flash <= 0:
                    self.flash = 10
                    self.sfx.play("thunder")
        self.flash -= 1
        while len(self.rain) < self.rain_amount:
            self.rain.append([random.uniform(0, W + 40), random.uniform(30, 60)])
        heavy = 1 + (self.rain_amount > 60)
        for r in self.rain:
            r[0] -= 0.8 * heavy
            r[1] += 3.2 * heavy
        self.rain = [r for r in self.rain if r[1] < WIN_B][:int(self.rain_amount)]

        for g in self.glass:      # drops on the glass: stick, then slide
            g[3] -= 1
            if g[3] < 0:
                g[1] += g[2] * 6
                if random.random() < 0.02:
                    g[3] = random.randint(20, 120)
            if g[1] > WIN_B:
                g[0], g[1], g[3] = random.uniform(WIN_L, WIN_R_X), random.uniform(45, 120), random.randint(0, 150)

        for f in self.floaters:
            f[1] -= f[3]
            f[0] += math.sin(self.frame * 0.05 + f[2]) * 0.4
        self.floaters = [f for f in self.floaters if f[1] > -8]

    # ------------------------------------------------------------
    def draw_plant(self, b):
        sway = math.sin(self.frame * 0.025) * 0.8
        droop = 0.0
        if self.done and not self.loves:
            droop = min(self.end_t / 80, 1)
        cx = FLOWER_X + sway + droop * 9
        cy = FLOWER_Y + droop * 14
        stem, stem_d, stem_l = hexc("#4aa34a"), hexc("#2a6b33"), hexc("#86d66b")
        base_y = 199
        # stem as quadratic curve from pot to flower
        for i in range(140):
            t = i / 139
            x = (1 - t) ** 2 * 80 + 2 * (1 - t) * t * (78 - droop * 2) + t * t * cx
            y = (1 - t) ** 2 * base_y + 2 * (1 - t) * t * 165 + t * t * cy
            b.set_at((int(x) - 1, int(y)), stem_d)
            b.set_at((int(x), int(y)), stem)
            b.set_at((int(x) + 1, int(y)), stem_l if int(y) % 4 else stem)
        # two leaves, heart-ish
        for ly, side in ((185, -1), (172, 1)):
            for i in range(16):
                w = math.sin(i / 15 * math.pi) ** 0.8 * 4
                x0 = 79 + side * (i + 1)
                y0 = ly - i * 0.45 + (i / 15) ** 2 * 3 * (1 + droop)
                for k in range(-int(w), int(w) + 1):
                    col = stem_l if k < 0 else stem
                    if abs(k) == int(w) or k == 0 and i > 2:
                        col = stem_d
                    b.set_at((int(x0), int(y0 + k)), col)

        gray = self.done and not self.loves
        for p in self.petals:
            if p.state == "on":
                p.x = cx + math.cos(p.angle) * PETAL_DIST
                p.y = cy + math.sin(p.angle) * PETAL_DIST
                last = len(self.remaining()) == 1
                if last and (self.frame // 8) % 2 == 0:       # last petal glows
                    for a in range(0, 360, 30):
                        gx = p.x + math.cos(math.radians(a)) * (PETAL_A + 2)
                        gy = p.y + math.sin(math.radians(a)) * (PETAL_B + 3)
                        b.set_at((int(gx), int(gy)), (255, 240, 200))
                p.draw(b)

        # centre: heart when she loves you, grey when not
        if self.done and self.loves and self.end_t > 15:
            pulse = 1 + (0.25 if (self.end_t // 12) % 2 == 0 else 0)
            spr = pygame.transform.scale(self.big_heart, (int(11 * pulse), int(10 * pulse)))
            b.blit(spr, (int(cx - spr.get_width() / 2), int(cy - spr.get_height() / 2)))
            return
        if gray:
            c1, c2, c3, c4 = (hexc(c) for c in ("#7d6a6a", "#5d4d55", "#3e3140", "#a89a94"))
        else:
            c1, c2, c3, c4 = (hexc(c) for c in ("#ffcf4a", "#e89a22", "#8a3d2a", "#fff3a8"))
        for y in range(-CENTER_R - 1, CENTER_R + 2):
            for x in range(-CENTER_R - 1, CENTER_R + 2):
                d = math.hypot(x, y)
                if d > CENTER_R + 0.4:
                    continue
                px, py = int(cx + x), int(cy + y)
                if d > CENTER_R - 0.8:
                    col = c3
                elif d > CENTER_R - 3:
                    col = c2 if dither(px, py, 0.5) else c1
                else:
                    col = c1 if (x + 2 * y) % 4 else c2
                if -4 < x < 0 and -4 < y < 0 and (x + y) % 2 == 0:
                    col = c4
                b.set_at((px, py), col)

    def render(self):
        b = self.buf
        b.blit(self.outside, (0, 0))
        # twinkling city windows
        for i, (x, y) in enumerate(self.city_lights):
            if math.sin(self.frame * 0.01 + i * 1.7) > 0.93:
                b.set_at((x, y), hexc("#1d0f2b"))
        # rain outside
        for r in self.rain:
            for k in range(4):
                b.set_at((int(r[0] + k * 0.25), int(r[1] - k)), (214, 170, 214) if k else (240, 210, 240))
        if self.flash > 0 and self.flash % 4 != 1:
            b.fill((236, 226, 255))
        # drops on the glass
        for x, y, _, _ in self.glass:
            if in_window(int(x), int(y)):
                b.set_at((int(x), int(y)), (255, 230, 245))
                b.set_at((int(x), int(y) + 1), (170, 120, 170))
                for k in range(2, 6):
                    if dither(x, y + k, 0.5 - k * 0.08):
                        b.set_at((int(x), int(y) - k), (200, 150, 200))
        b.blit(self.room, (0, 0))

        # fairy lights along the arch
        for i, ang in enumerate(range(195, 346, 10)):
            a = math.radians(ang)
            x = WIN_CX + math.cos(a) * (WIN_R + 8)
            y = WIN_CY + math.sin(a) * (WIN_R + 8) + 2
            b.set_at((int(x), int(y) - 1), (60, 45, 60))
            on = math.sin(self.frame * 0.06 + i * 1.3) > -0.2
            col = [(255, 210, 120), (255, 150, 190), (170, 220, 255)][i % 3]
            if on:
                b.fill(col, (int(x), int(y), 2, 2))
                if dither(x, y, 0.5):
                    b.set_at((int(x) - 1, int(y)), tuple(c // 2 for c in col))
            else:
                b.fill(tuple(c // 3 for c in col), (int(x), int(y), 2, 2))

        gray = self.done and not self.loves
        for p in self.petals:
            if p.state == "ground":
                p.draw(b, gray)
        self.draw_plant(b)
        b.blit(self.pot, (0, 0))
        for p in self.petals:
            if p.state == "fall":
                p.draw(b)
        for s in self.sparks:
            b.set_at((int(s[0]), int(s[1])), (255, 255, 255) if s[4] > 10 else (255, 170, 205))
        for f in self.floaters:
            b.blit(self.small_hearts[f[4]], (int(f[0]) - 3, int(f[1]) - 3))

        # typewriter text
        if self.loves is not None:
            lines = TEXTS[self.lang]["yes" if self.loves else "no"]
            col = YES_COL if self.loves else NO_COL
            shown = self.text_t // 2
            y = 8 if len(lines) == 2 else 18
            for line in lines:
                part = line[:max(0, shown)]
                shown -= len(line)
                x = (W - text_width(line, 2)) // 2
                if part:
                    draw_text(b, part, x, y, 2, col)
                y += 18
        if self.done and self.end_t > 70:
            self.draw_card(b, WIN_MSG if self.loves else LOSE_MSG)
        if self.show_hints:
            hint = "PRESS R" if self.done else ("TAP A PETAL" if self.plucked == 0 else "")
            if hint and (self.frame // 30) % 2 == 0:
                draw_text(b, hint, (W - text_width(hint, 1)) // 2, H - 22, 1, (240, 225, 240))

        pygame.transform.scale(b, self.win.get_size(), self.win)
        pygame.display.flip()

    def draw_card(self, b, lines):
        t = self.end_t - 70
        h = len(lines) * 16 + 10
        top = 76 - h // 2 + max(0, 12 - t)          # slides up a bit as it appears
        x0, x1 = 12, W - 12
        border = YES_COL if self.loves else NO_COL
        b.fill(INK, (x0, top, x1 - x0, h))
        b.fill((44, 24, 56), (x0 + 2, top + 2, x1 - x0 - 4, h - 4))
        for x in range(x0, x1):
            b.set_at((x, top), border)
            b.set_at((x, top + h - 1), border)
        for y in range(top, top + h):
            b.set_at((x0, y), border)
            b.set_at((x1 - 1, y), border)
        shown = t // 3
        y = top + 6
        for line in lines:
            part = line[:max(0, shown)]
            shown -= len(line)
            if part:
                draw_text(b, part, (W - text_width(line, 2)) // 2, y, 2, (255, 240, 246))
            y += 16

    # ------------------------------------------------------------
    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.click(e.pos[0] / SCALE, e.pos[1] / SCALE)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r:
                        self.reset()
                    elif e.key == pygame.K_l:
                        self.lang = "en" if self.lang == "gr" else "gr"
                    elif e.key == pygame.K_h:
                        self.show_hints = not self.show_hints
                    elif e.key == pygame.K_m:
                        self.sfx.on = not self.sfx.on
                    elif e.key == pygame.K_SPACE:
                        if self.done:
                            self.reset()
                        elif self.remaining():
                            self.pluck(random.choice(self.remaining()))
            self.update()
            self.render()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
