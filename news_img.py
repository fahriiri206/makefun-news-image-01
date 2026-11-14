#!/usr/bin/env python3
"""Draw a 1024x1024 news montage for Friday 13 November 2026."""

import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
SS = 2
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

BG = "#0A0F1A"
CARD = "#121A2C"
BORDER = "#243352"
INK = "#F4F7FC"
MUTED = "#8A97AD"
RED = "#E0303B"

PAD = 28
ACCENT_W = 8
TAG_SIZE = 15
ICON = 48
MAX_LINES = 3


class Canvas:
    def __init__(self, w, h, bg):
        self.img = Image.new("RGB", (w * SS, h * SS), bg)
        self.d = ImageDraw.Draw(self.img)
        self.fonts = {}

    def font(self, name, size):
        key = (name, size)
        if key not in self.fonts:
            self.fonts[key] = ImageFont.truetype(FONT_DIR + name, size * SS)
        return self.fonts[key]

    def box(self, b):
        return [round(v * SS) for v in b]

    def rrect(self, b, r, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(
            self.box(b), radius=r * SS, fill=fill, outline=outline,
            width=max(1, round(width * SS)),
        )

    def rect(self, b, fill):
        self.d.rectangle(self.box(b), fill=fill)

    def poly(self, pts, fill=None, outline=None, width=1):
        self.d.polygon(
            [(round(x * SS), round(y * SS)) for x, y in pts], fill=fill,
            outline=outline, width=max(1, round(width * SS)),
        )

    def line(self, pts, fill, width=1):
        self.d.line(
            [(round(x * SS), round(y * SS)) for x, y in pts], fill=fill,
            width=max(1, round(width * SS)), joint="curve",
        )

    def ellipse(self, b, fill=None, outline=None, width=1):
        self.d.ellipse(
            self.box(b), fill=fill, outline=outline,
            width=max(1, round(width * SS)),
        )

    def text(self, xy, s, size, fill, name="DejaVuSans.ttf", anchor="la", track=0):
        f = self.font(name, size)
        if not track:
            self.d.text((round(xy[0] * SS), round(xy[1] * SS)), s, font=f,
                        fill=fill, anchor=anchor)
            return
        x, y = xy
        for ch in s:
            self.d.text((round(x * SS), round(y * SS)), ch, font=f, fill=fill,
                        anchor=anchor)
            x += self.d.textlength(ch, font=f) / SS + track

    def measure(self, s, size, name="DejaVuSans-Bold.ttf"):
        return self.d.textlength(s, font=self.font(name, size)) / SS

    def save(self, path):
        self.img.resize((W, H), Image.LANCZOS).save(path, optimize=True)


def wrap(cv, text, width, size, name="DejaVuSans-Bold.ttf"):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if cv.measure(trial, size, name) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def icon_chip(cv, b, c):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    body = (x0 + w * .22, y0 + h * .22, x1 - w * .22, y1 - h * .22)
    cv.rrect(body, w * .06, outline=c, width=2.6)
    cv.rrect((x0 + w * .38, y0 + h * .38, x1 - w * .38, y1 - h * .38),
             w * .03, fill=c)
    for t in (.32, .50, .68):
        cv.line([(x0 + w * .10, y0 + h * t), (x0 + w * .22, y0 + h * t)], c, 2.4)
        cv.line([(x1 - w * .22, y0 + h * t), (x1 - w * .10, y0 + h * t)], c, 2.4)
        cv.line([(x0 + w * t, y0 + h * .10), (x0 + w * t, y0 + h * .22)], c, 2.4)
        cv.line([(x0 + w * t, y1 - h * .22), (x0 + w * t, y1 - h * .10)], c, 2.4)


def icon_grid(cv, b, c):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    gap = w * .10
    s = (w - gap) / 2
    for i in range(2):
        for j in range(2):
            sq = (x0 + i * (s + gap), y0 + j * (s + gap),
                  x0 + i * (s + gap) + s, y0 + j * (s + gap) + s)
            if i == j:
                cv.rrect(sq, w * .04, fill=c)
            else:
                cv.rrect(sq, w * .04, outline=c, width=2.4)


def icon_missile(cv, b, c):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0

    def p(u, v):
        return (x0 + u * w, y0 + v * h)

    cv.poly([p(.42, .62), p(.58, .62), p(.58, .30), p(.50, .12), p(.42, .30)],
            fill=c)
    cv.poly([p(.42, .62), p(.24, .84), p(.42, .84)], fill=c)
    cv.poly([p(.58, .62), p(.76, .84), p(.58, .84)], fill=c)
    cv.rect((x0 + w * .30, y0 + h * .62, x0 + w * .70, y0 + h * .70), c)
    for dx in (-.13, 0, .13):
        cv.line([p(.50 + dx, .78), p(.50 + dx * 1.5, .93)], c, 2.4)


def icon_ship(cv, b, c):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    cv.poly([(x0 + w * .08, y0 + h * .62), (x0 + w * .92, y0 + h * .62),
             (x0 + w * .80, y0 + h * .79), (x0 + w * .20, y0 + h * .79)], fill=c)
    cv.rect((x0 + w * .36, y0 + h * .44, x0 + w * .62, y0 + h * .62), c)
    cv.rect((x0 + w * .66, y0 + h * .50, x0 + w * .72, y0 + h * .62), c)
    cv.rect((x0 + w * .18, y0 + h * .30, x0 + w * .22, y0 + h * .44), c)
    for k in range(3):
        yy = y0 + h * (.87 + k * .04)
        cv.line([(x0 + w * (.10 + k * .04), yy), (x0 + w * (.40 + k * .04), yy)], c, 2.0)
        cv.line([(x0 + w * (.52 + k * .04), yy), (x0 + w * (.82 + k * .04), yy)], c, 2.0)


def icon_flag(cv, b, c):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    cv.line([(x0 + w * .24, y0 + h * .14), (x0 + w * .24, y0 + h * .88)], c, 3.2)
    cv.poly([(x0 + w * .26, y0 + h * .15), (x0 + w * .82, y0 + h * .22),
             (x0 + w * .72, y0 + h * .31), (x0 + w * .82, y0 + h * .40),
             (x0 + w * .26, y0 + h * .47)], fill=c)
    cv.line([(x0 + w * .12, y0 + h * .88), (x0 + w * .48, y0 + h * .88)], c, 3.0)


def icon_plane(cv, b, c):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    cv.poly([(x0 + w * .50, y0 + h * .06), (x0 + w * .57, y0 + h * .32),
             (x0 + w * .57, y0 + h * .80), (x0 + w * .50, y0 + h * .94),
             (x0 + w * .43, y0 + h * .80), (x0 + w * .43, y0 + h * .32)], fill=c)
    cv.poly([(x0 + w * .50, y0 + h * .44), (x0 + w * .08, y0 + h * .62),
             (x0 + w * .08, y0 + h * .70), (x0 + w * .50, y0 + h * .60),
             (x0 + w * .92, y0 + h * .70), (x0 + w * .92, y0 + h * .62)], fill=c)
    cv.poly([(x0 + w * .50, y0 + h * .80), (x0 + w * .26, y0 + h * .90),
             (x0 + w * .26, y0 + h * .94), (x0 + w * .50, y0 + h * .87),
             (x0 + w * .74, y0 + h * .94), (x0 + w * .74, y0 + h * .90)], fill=c)


ICONS = {
    "chip": icon_chip,
    "grid": icon_grid,
    "missile": icon_missile,
    "ship": icon_ship,
    "flag": icon_flag,
    "plane": icon_plane,
}

CARDS = [
    ("TECH", "Nvidia CEO Jensen Huang steps down", "#35C9E0", "chip"),
    ("TECH", "Microsoft outage hits worldwide", "#35C9E0", "grid"),
    ("MIDDLE EAST", "US downs Iranian drones; radar hit in Bahrain", "#F08A2C", "missile"),
    ("US", "Tanker strikes cruise ship, 129 aboard (New Orleans)", "#E8464A", "ship"),
    ("EUROPE", "EU forms Ukraine peace-talks team", "#3FBF7F", "flag"),
    ("US", "FAA grounds all US flights", "#E0B34A", "plane"),
]


def main():
    cv = Canvas(W, H, BG)

    cv.text((44, 40), "WORLD NEWS", 58, INK, "DejaVuSans-Bold.ttf")
    cv.text((980, 74), "Friday 13 November 2026", 21, MUTED,
            anchor="ra")
    cv.rect((44, 128, 980, 133), RED)

    margin, gap = 44, 18
    top, bottom = 176, 44
    cw = (W - 2 * margin - gap) // 2
    ch = (H - top - bottom - 2 * gap) // 3

    text_w = cw - PAD - ACCENT_W - ICON - 34
    size = 30
    while size > 20 and any(
        len(wrap(cv, h, text_w, size)) > MAX_LINES for _, h, _, _ in CARDS
    ):
        size -= 1
    lh = round(size * 1.16)

    for i, (tag, headline, color, icon) in enumerate(CARDS):
        col, row = i % 2, i // 2
        x = margin + col * (cw + gap)
        y = top + row * (ch + gap)

        cv.rrect((x, y, x + ACCENT_W + 18, y + ch), 14, fill=color)
        cv.rrect((x + ACCENT_W, y, x + cw, y + ch), 14, fill=CARD)
        cv.rrect((x, y, x + cw, y + ch), 14, outline=BORDER, width=1.4)

        lines = wrap(cv, headline, text_w, size)
        block = TAG_SIZE + 13 + len(lines) * lh
        ty = y + round((ch - block) / 2)
        tx = x + ACCENT_W + PAD

        cv.text((tx, ty), tag, TAG_SIZE, color, "DejaVuSans-Bold.ttf", track=1.4)
        for n, ln in enumerate(lines):
            cv.text((tx, ty + TAG_SIZE + 13 + n * lh), ln, size, INK,
                    "DejaVuSans-Bold.ttf")

        ib = (x + cw - PAD - ICON, ty - 4, x + cw - PAD, ty - 4 + ICON)
        ICONS[icon](cv, ib, color)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    cv.save(out)
    print(f"{out}  {os.path.getsize(out) / 1024:.1f} KiB")


if __name__ == "__main__":
    main()
