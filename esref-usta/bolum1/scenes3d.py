"""Bölüm 1 — 3D karakterlerle sahne düzeni ve render."""
import sys, math, subprocess, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import W, H, UI, FPS, ROOT, layer, draw_rope, finish, subtitle, envelope, duration, smooth
import inserts as ins
from scenes import LINES, START, DUR, sub_at, audio_mix, plate, _ins

import os
SPR = f"{ROOT}/3d/" + os.environ.get("SPRITES", "sprites")
SP_H = 1300
ZERO_ROW = SP_H - 0.1 / 1.45 * SP_H   # sprite row of the counter-top line (y = 0)
CY = 220
COUNTER_TOP = 1770 + CY

USTA_X, DENIZ_X, EMRE_X = 640, 1110, 720
S_USTA, S_DENIZ, S_EMRE = 0.92, 0.9, 0.95


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{ROOT}/bolum1/replikler/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


BLINKS = {"U": [2.6, 6.2, 11.1, 15.9, 20.3, 26.8, 31.0, 36.1, 40.7, 44.9, 50.8, 58.0, 62.5, 70.9],
          "D": [1.4, 5.1, 9.9, 13.6, 19.2, 24.9, 29.3, 34.4, 41.2, 46.6, 53.7, 59.4, 66.1, 71.8],
          "E": [3.0, 8.0, 14.2, 17.6, 21.9, 25.4, 33.4, 39.9, 43.2, 48.9, 56.5, 64.4, 68.4]}


def pose_name(base, who, t, mouth_level=None, can_blink=True):
    amp = speaking(t, who) if mouth_level is None else mouth_level
    lvl = int(round(min(1.0, amp * 1.15) * 4))
    if lvl == 0 and can_blink and base not in ("E_loupe", "E_soft"):
        for tb in BLINKS[who]:
            d = t - tb
            if 0 <= d < 3 / FPS:
                return f"{base}_{'h' if d < 1 / FPS or d >= 2 / FPS else 'b'}"
    return f"{base}_m{lvl}"


@functools.lru_cache(None)
def spr(name):
    im = Image.open(f"{SPR}/{name}.png").convert("RGBA")
    return im


@functools.lru_cache(maxsize=256)
def spr_scaled(name, scale, blur, darken):
    im = spr(name)
    k = scale * SP_H / im.size[1]   # scale is expressed for 1300px-tall sprites
    im = im.resize((int(im.size[0] * k), int(im.size[1] * k)), Image.LANCZOS)
    if darken != 1.0:
        a = im.split()[3]
        im = Image.eval(im.convert("RGB"), lambda v: int(v * darken)).convert("RGBA"); im.putalpha(a)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return im


def put(world, name, cx, scale, blur=0, darken=1.0, dy=0.0):
    im = spr_scaled(name, round(scale, 3), blur, darken)
    top = COUNTER_TOP - ZERO_ROW * scale + dy
    world.alpha_composite(im, (int(cx - im.size[0] / 2), int(top)))


def put_screen(frame, name, x, y_top, scale, blur, darken):
    x, y_top, scale, blur = x * UI, y_top * UI, scale * UI, blur * UI
    im = spr_scaled(name, round(scale, 3), round(blur, 2), darken)
    frame.alpha_composite(im, (int(x - im.size[0] / 2), int(y_top)))


@functools.lru_cache(None)
def contact_shadow(w=900):
    sh = Image.new("RGBA", (w, w), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([w * 0.18, w * 0.15, w * 0.82, w], fill=(0, 0, 0, 110))
    return sh.filter(ImageFilter.GaussianBlur(w * 0.08))


@functools.lru_cache(None)
def front_plate(rope="two", package=False):
    front = Image.new("RGBA", (1440, 2560), (0, 0, 0, 0))
    front.alpha_composite(layer("tezgah"), (0, CY))
    if rope == "two":
        draw_rope(front, [(330, 1810 + CY), (420, 1802 + CY), (500, 1812 + CY)], 18, "flat", "flat", seed=2)
        draw_rope(front, [(860, 1815 + CY), (790, 1806 + CY), (720, 1812 + CY)], 18, "flat", "flat", seed=3)
    elif rope == "knot":
        draw_rope(front, [(330, 1810 + CY), (500, 1806 + CY), (680, 1810 + CY), (860, 1815 + CY)], 18, "flat", "flat", seed=2)
        ImageDraw.Draw(front).ellipse([585, 1794 + CY, 625, 1826 + CY], fill=(176, 140, 96, 255))
    elif rope == "box":
        d = ImageDraw.Draw(front)
        d.rounded_rectangle([560, 1752 + CY, 760, 1818 + CY], radius=14, fill=(110, 24, 38, 255))
        d.rectangle([560, 1772 + CY, 760, 1778 + CY], fill=(150, 120, 60, 255))
    if package:
        d = ImageDraw.Draw(front)
        d.rounded_rectangle([900, 1768 + CY, 1090, 1818 + CY], radius=8, fill=(150, 142, 126, 255))
        for yy in range(1776, 1814, 9):
            d.line([(912, yy + CY), (1078, yy + CY)], fill=(118, 112, 100, 255), width=3)
        d.line([(995, 1768 + CY), (995, 1818 + CY)], fill=(120, 86, 54, 255), width=5)
    return front


@functools.lru_cache(None)
def back_plate(bg, blur):
    w = layer(bg, blur).copy()
    return w


def crop(world, cam):
    cx, cy, cw = cam
    ch = cw * H / W
    box = (int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))
    return world.crop(box).resize((W, H), Image.LANCZOS)


def breathe(t, period=3.8, amp=4.0):
    return amp * math.sin(t * 2 * math.pi / period)


def shop(t, cam, usta="E_front", deniz="D_listen", bg_blur=2, usta_blur=0, deniz_blur=2, show_deniz=True,
         rope="two", package=False, emre_back=None, usta_mouth=None, usta_blinks=True):
    world = back_plate("duvar", bg_blur).copy()
    if show_deniz:
        dn = pose_name(deniz, "D", t) if deniz.startswith("D_") else deniz
        put(world, dn, DENIZ_X, S_DENIZ, blur=deniz_blur, darken=0.88, dy=breathe(t + 1.3, 3.3, 3))
    world.alpha_composite(contact_shadow(), (USTA_X - 450, COUNTER_TOP - 1000))
    un = usta if usta.startswith("E_loupe_in") or usta in ("E_back", "E_turn") else pose_name(usta, "U", t, usta_mouth, usta_blinks)
    put(world, un, USTA_X, S_USTA, blur=usta_blur, dy=breathe(t))
    world.alpha_composite(front_plate(rope, package))
    frame = crop(world, cam)
    if emre_back:
        x, ytop, sc, bl = emre_back[:4]
        put_screen(frame, emre_back[4] if len(emre_back) > 4 else "M_back", x, ytop, sc, bl, 0.62)
    return frame


def door(t, cam, emre="M_front", bg_blur=6, rope="two", package=False, usta_back=None, emre_mouth=None):
    world = back_plate("kapi", bg_blur).copy()
    world.alpha_composite(contact_shadow(800), (EMRE_X - 400, COUNTER_TOP - 950))
    en = pose_name(emre, "E", t, emre_mouth)
    put(world, en, EMRE_X, S_EMRE, dy=breathe(t + 0.7, 4.2, 3))
    world.alpha_composite(front_plate(rope, package))
    frame = crop(world, cam)
    if usta_back:
        x, ytop, sc, bl = usta_back
        put_screen(frame, "E_back", x, ytop, sc, bl, 0.6)
    return frame


def push(cam, t, t0, t1, amount=0.05):
    k = smooth((t - t0) / max(t1 - t0, 0.01))
    return (cam[0], cam[1], cam[2] * (1 - amount * k))


WIDE = (720, 1420, 1240)
USTA_MCU = (USTA_X + 10, 1500, 780)
USTA_CU = (USTA_X + 10, 1380, 600)
DENIZ_MCU = (DENIZ_X - 30, 1560, 680)
EMRE_MCU = (EMRE_X, 1470, 780)
EMRE_CU = (EMRE_X, 1400, 620)
EMRE_BACK_WIDE = (120, 560, 0.95, 5)
EMRE_BACK_OTS = (40, 420, 1.35, 12)
USTA_BACK_OTS = (690, 380, 1.3, 12)


def loupe_in(t, t0, dur=0.45):
    k = (t - t0) / dur
    if k < 0:
        return None
    i = int(k * 4)
    return f"E_loupe_in{i}" if i < 4 else "E_loupe"


def loupe_out(t, t0, dur=0.4):
    k = (t - t0) / dur
    if k < 0:
        return "E_loupe"
    i = 3 - int(k * 4)
    return f"E_loupe_in{i}" if i >= 0 else None


def shot5(t):
    p = loupe_in(t, 10.0)
    if p is None:
        return shop(t, push(USTA_CU, t, 9.6, 12.0, 0.06), usta="E_front", bg_blur=9, deniz_blur=8)
    return shop(t, push(USTA_CU, t, 9.6, 12.0, 0.06), usta=p, bg_blur=9, deniz_blur=8)


def shot10(t):
    p = loupe_out(t, 22.65)
    if p is None:
        return shop(t, push(USTA_CU, t, 22.6, 24.2, 0.03), usta="E_serious", bg_blur=9, deniz_blur=8)
    return shop(t, push(USTA_CU, t, 22.6, 24.2, 0.03), usta=p, usta_mouth=0, bg_blur=9, deniz_blur=8)


def shot15(t):
    if t < 37.55:
        u = "E_turn"
    elif t < 38.45:
        u = "E_back"
    elif t < 38.75:
        u = "E_turn"
    else:
        u = "E_serious"
    return shop(t, WIDE, usta=u, package=t >= 38.6, emre_back=EMRE_BACK_WIDE)


def S(t0, t1, fn):
    return (t0, t1, fn)


SHOTS = [
    S(0.0, 4.4, lambda t: shop(t, push(WIDE, t, 0, 4.4, 0.04), deniz="D_phone",
                               emre_back=(120 - 220 * (1 - smooth(t / 1.4)), 560, 0.95, 5))),
    S(4.4, 6.9, lambda t: shop(t, push(DENIZ_MCU, t, 4.4, 6.9), deniz="D_phone", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(6.9, 8.4, lambda t: shop(t, push(USTA_MCU, t, 6.9, 8.4), usta="E_side", deniz="D_phone", bg_blur=8, deniz_blur=6)),
    S(8.4, 9.6, plate(lambda t: _ins("phone", t < 8.75, "", "", "", True), 8.4, 9.6, 1.0, 1.04)),
    S(9.6, 12.0, shot5),
    S(12.0, 14.6, plate(lambda t: _ins("rope_end", True), 12.0, 14.6, 1.0, 1.08)),
    S(14.6, 16.8, lambda t: door(t, push(EMRE_MCU, t, 14.6, 16.8, 0.03), emre="M_front", usta_back=USTA_BACK_OTS)),
    S(16.8, 18.2, lambda t: shop(t, push(USTA_MCU, t, 16.8, 18.2), usta="E_loupe", bg_blur=8, deniz_blur=6, usta_blinks=False)),
    S(18.2, 22.6, lambda t: door(t, push(EMRE_MCU, t, 18.2, 22.6, 0.12), emre="M_down")),
    S(22.6, 24.2, shot10),
    S(24.2, 25.9, lambda t: door(t, EMRE_CU, emre="M_stun")),
    S(25.9, 32.4, plate(lambda t: _ins("rope_end", False), 25.9, 32.4, 1.0, 1.12, cx=0.62)),
    S(32.4, 35.0, lambda t: door(t, push(EMRE_MCU, t, 32.4, 35.0, 0.03), emre="M_front", usta_back=USTA_BACK_OTS)),
    S(35.0, 37.2, lambda t: shop(t, push(USTA_CU, t, 35.0, 37.2, 0.05), usta="E_serious", bg_blur=9, deniz_blur=8)),
    S(37.2, 39.4, shot15),
    S(39.4, 42.4, plate(lambda t: _ins("package", round(min(1, max(0, (t - 39.6) / 1.8)) * 12) / 12), 39.4, 42.4, 1.0, 1.05)),
    S(42.4, 43.8, lambda t: door(t, push(EMRE_CU, t, 42.4, 43.8, 0.04), emre="M_stun", package=False)),
    S(43.8, 47.3, lambda t: shop(t, push(USTA_MCU, t, 43.8, 47.3, 0.05), usta="E_serious", bg_blur=8, deniz_blur=6, package=True)),
    S(47.3, 49.7, lambda t: door(t, push(EMRE_MCU, t, 47.3, 49.7, 0.04), emre="M_down", usta_back=USTA_BACK_OTS)),
    S(49.7, 52.4, lambda t: shop(t, push(USTA_CU, t, 49.7, 52.4, 0.05), usta="E_front", bg_blur=9, deniz_blur=8, package=True)),
    S(52.4, 55.0, lambda t: shop(t, push(DENIZ_MCU, t, 52.4, 55.0, 0.05), deniz="D_whisper", deniz_blur=0, bg_blur=8, usta_blur=6, package=True)),
    S(55.0, 63.8, lambda t: shop(t, push(USTA_MCU, t, 55.0, 63.8, 0.16), usta="E_soft", bg_blur=8, deniz_blur=6, package=True, usta_blinks=False)),
    S(63.8, 67.0, plate(lambda t: _ins("rope_halves", t >= 65.0), 63.8, 67.0, 1.0, 1.06)),
    S(67.0, 69.6, lambda t: door(t, push(EMRE_MCU, t, 67.0, 69.6, 0.03), emre="M_soft", rope="knot")),
    S(69.6, 73.8, lambda t: shop(t, push(USTA_MCU, t, 69.6, 73.8, 0.07), usta="E_soft", bg_blur=8, deniz_blur=6, rope="knot", package=True, usta_blinks=False)),
    S(73.8, 77.6, plate(lambda t: _ins("phone", True, "Arkadaşlık · 12 yıl", "Murat", "aranıyor…", True), 73.8, 77.6, 1.0, 1.07)),
    S(77.6, 86.0, plate(lambda t: _ins("ticket", round(min(1, max(0, (t - 78.0) / 5.6)) * 60) / 60, round(min(1, max(0, (t - 84.2) / 0.35)) * 8) / 8), 77.6, 86.0, 1.04, 1.0)),
    S(86.0, 90.0, plate(lambda t: _ins("cta"), 86.0, 90.0, 1.0, 1.0)),
]
TOTAL = 90.0


def frame_at(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            img = fn(t)
            break
    else:
        img = Image.new("RGB", (W, H))
    img = finish(img, t, dust=t < 86.0, grain=True)
    if t < 86.0:
        img = subtitle(img, sub_at(t))
    if t < 0.4:
        img = Image.eval(img, lambda v, k=t / 0.4: int(v * k))
    if t > TOTAL - 0.6:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.6: int(v * max(k, 0)))
    if 85.7 <= t < 86.3:
        k = abs(t - 86.0) / 0.3
        img = Image.eval(img, lambda v, k=k: int(v * min(1, k)))
    return img


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        for tt in sys.argv[3:]:
            frame_at(float(tt)).save(f"{sys.argv[2]}/still_{float(tt):05.1f}.jpg", quality=88)
    elif mode == "video":
        out = sys.argv[2]
        a, b = float(sys.argv[3]), float(sys.argv[4])
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for n in range(int(round(a * FPS)), int(round(b * FPS))):
            p.stdin.write(frame_at(n / FPS).convert("RGB").tobytes())
        p.stdin.close(); p.wait()
