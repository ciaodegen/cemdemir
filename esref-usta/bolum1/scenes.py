import sys, math, subprocess, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import (W, H, FPS, ROOT, talk_sprite, sprite, layer, emre_silhouette, draw_rope,
                    finish, subtitle, envelope, duration, smooth)
import inserts as ins

REP = f"{ROOT}/bolum1/replikler"
SFX = f"{ROOT}/efektler"

# ---------------- dialogue ----------------
LINES = [  # file, speaker, subtitle
    ("01_E", "E", "Usta… arkadaşlık tamiri yapıyor musunuz?"),
    ("02_D", "D", "Abi yenisini al ya. Değmez."),
    ("03_U", "U", "Deniz."),
    ("04_U", "U", "Kaç yıllık?"),
    ("05_E", "E", "On iki. Liseden."),
    ("06_U", "U", "Ne zaman koptu?"),
    ("07_E", "E", "Fark etmedim ki. Bir gün baktım… elimde sadece benim ucum kalmış."),
    ("08_U", "U", "Bu kopmamış."),
    ("09_E", "E", "Nasıl yani?"),
    ("10_U", "U", "Kopan ipin ucu püskül olur. Bu düz. Bu… bırakılmış."),
    ("11_E", "E", "O bıraktı. Ben hep aradım."),
    ("12_U", "U", "Dün geldi. O da “o bıraktı” dedi."),
    ("13_E", "E", "Ama… hiç aramadı."),
    ("14_U", "U", "Sen de aramamışsın."),
    ("15_D", "D", "İkisi de birbirini beklemiş…"),
    ("16_U", "U", "Çoğu ip böyle kopar evlat. Kimse çekmez, kimse bırakmaz. Herkes bekler."),
    ("17_E", "E", "Borcum ne?"),
    ("18_U", "U", "Düğümü ben attım. Sıkmak sana kalmış."),
]
START = {  # line index -> start time (s)
    0: 1.2, 1: 4.6, 2: 7.1, 3: 12.4, 4: 14.8, 5: 17.0, 6: 18.4, 7: 23.0, 8: 24.4, 9: 26.1,
    10: 32.6, 11: 44.0, 12: 47.5, 13: 49.9, 14: 52.6, 15: 55.3, 16: 67.2, 17: 69.8,
}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


def sub_at(t):
    for i, (f, s, txt) in enumerate(LINES):
        if START[i] - 0.05 <= t < START[i] + DUR[i] + 0.25:
            # long lines: split into halves by sentence
            parts = [p.strip() for p in split_sub(txt)]
            if len(parts) == 1:
                return txt
            k = (t - START[i]) / max(DUR[i], 0.1)
            # weight split by length
            L = [len(p) for p in parts]; acc = 0
            for p, l in zip(parts, L):
                acc += l / sum(L)
                if k < acc:
                    return p
            return parts[-1]
    return ""


def split_sub(txt):
    if len(txt) <= 44:
        return [txt]
    out, cur = [], ""
    for tok in txt.replace("… ", "…|").replace(". ", ".|").split("|"):
        if cur and len(cur) + len(tok) > 44:
            out.append(cur); cur = tok
        else:
            cur = (cur + " " + tok).strip()
    if cur:
        out.append(cur)
    return out


# ---------------- shop world ----------------
USTA_X, USTA_BOTTOM, USTA_S = 640, 2050, 2.3
DENIZ_X, DENIZ_BOTTOM, DENIZ_S = 1110, 2035, 1.8


CY = 220


def place(world, img, cx, bottom, scale, blur=0, darken=1.0):
    w, h = img.size
    im = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    if darken != 1.0:
        a = im.split()[3]
        im = Image.eval(im.convert("RGB"), lambda v: int(v * darken)).convert("RGBA"); im.putalpha(a)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    world.alpha_composite(im, (int(cx - im.size[0] / 2), int(bottom - im.size[1])))


@functools.lru_cache(None)
def contact_shadow():
    sh = Image.new("RGBA", (900, 900), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([150, 120, 750, 900], fill=(0, 0, 0, 120))
    return sh.filter(ImageFilter.GaussianBlur(70))


@functools.lru_cache(None)
def back_plate(bg_blur, deniz_pose, deniz_blur, show_deniz):
    world = layer("duvar", bg_blur).copy()
    if show_deniz:
        place(world, Image.fromarray(sprite(deniz_pose)), DENIZ_X, DENIZ_BOTTOM, DENIZ_S, blur=deniz_blur, darken=0.9)
    world.alpha_composite(contact_shadow(), (USTA_X - 450 + 40, USTA_BOTTOM - 900 - 40))
    return world


@functools.lru_cache(None)
def front_plate(rope="two", package=False):
    front = Image.new("RGBA", (1440, 2560), (0, 0, 0, 0)); front.alpha_composite(layer("tezgah"), (0, CY))
    if rope == "two":
        draw_rope(front, [(400, 1808 + CY), (480, 1800 + CY), (540, 1810 + CY)], 18, "flat", "flat", seed=2)
        draw_rope(front, [(840, 1815 + CY), (770, 1806 + CY), (700, 1812 + CY)], 18, "flat", "flat", seed=3)
    elif rope == "knot":
        draw_rope(front, [(400, 1808 + CY), (540, 1806 + CY), (700, 1810 + CY), (840, 1815 + CY)], 18, "flat", "flat", seed=2)
        d = ImageDraw.Draw(front); d.ellipse([604, 1794 + CY, 644, 1824 + CY], fill=(176, 140, 96, 255))
    if package:
        d = ImageDraw.Draw(front)
        d.rounded_rectangle([880, 1768 + CY, 1080, 1818 + CY], radius=8, fill=(150, 142, 126, 255))
        for yy in range(1776, 1814, 9):
            d.line([(892, yy + CY), (1068, yy + CY)], fill=(118, 112, 100, 255), width=3)
        d.line([(980, 1768 + CY), (980, 1818 + CY)], fill=(120, 86, 54, 255), width=5)
    return front


def shop(t, cam, usta_pose="esref_1", deniz_pose="deniz_2", bg_blur=2, deniz_blur=2.0, usta_blur=0,
         show_deniz=True, rope="two", package=False, emre=None, loupe=0.0, usta_amp=None, deniz_amp=None):
    cx, cy, cw = cam
    world = back_plate(bg_blur, deniz_pose, deniz_blur if deniz_amp is None else 0, show_deniz).copy()
    if show_deniz and deniz_amp is not None:
        place(world, talk_sprite(deniz_pose, deniz_amp), DENIZ_X, DENIZ_BOTTOM, DENIZ_S, darken=0.9)
    amp = speaking(t, "U") if usta_amp is None else usta_amp
    br = 1 + 0.006 * math.sin(t * 2 * math.pi / 3.8)
    us = talk_sprite(usta_pose, amp)
    place(world, us, USTA_X, USTA_BOTTOM + 3 * math.sin(t * 2 * math.pi / 3.8), USTA_S * br, blur=usta_blur)
    if loupe > 0:
        draw_loupe(world, usta_pose, loupe)
    world.alpha_composite(front_plate(rope, package))
    ch = cw * H / W
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    frame = world.crop(tuple(int(v) for v in box)).resize((W, H), Image.LANCZOS)
    if emre:
        ex, ey, es, eb = emre
        sil = emre_silhouette(eb)
        s = sil.resize((int(sil.size[0] * es), int(sil.size[1] * es)))
        frame.alpha_composite(s, (int(ex - s.size[0] / 2), int(ey - s.size[1] / 2)))
    return frame


EYE = {"esref_1": (229, 91), "esref_8": (178, 95), "esref_2": (232, 86)}


def draw_loupe(world, pose, k):
    ex, ey = EYE.get(pose, (235, 78))
    w, h = Image.fromarray(sprite(pose)).size
    s = USTA_S
    x = USTA_X - w * s / 2 + ex * s
    y = USTA_BOTTOM - h * s + ey * s - (1 - smooth(k)) * 220
    r = 30 * s / 1.85 * 1.3
    ov = Image.new("RGBA", world.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.ellipse([x - r * 1.05, y - r * 1.05, x + r * 1.05, y + r * 1.05], fill=(20, 18, 16, 255))
    d.ellipse([x - r * 0.78, y - r * 0.78, x + r * 0.78, y + r * 0.78], fill=(70, 80, 84, 255))
    d.ellipse([x - r * 0.62, y - r * 0.62, x + r * 0.62, y + r * 0.62], fill=(140, 150, 150, 200))
    d.ellipse([x - r * 0.45, y - r * 0.55, x - r * 0.05, y - r * 0.2], fill=(255, 255, 255, 120))
    a = ov.split()[3].point(lambda v: int(v * min(1, k * 2)))
    ov.putalpha(a)
    world.alpha_composite(ov)


def plate(img_fn, t0, t1, z0=1.0, z1=1.06, cx=0.5, cy=0.5):
    def f(t):
        img = img_fn(t)
        k = (t - t0) / max(t1 - t0, 0.01)
        z = z0 + (z1 - z0) * smooth(k)
        cw, chh = 1440 / z, 2560 / z
        x0 = (1440 - cw) * cx; y0 = (2560 - chh) * cy
        return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + chh))).resize((W, H), Image.LANCZOS)
    return f


# camera presets (world cx, cy, width)
WIDE = (720, 1390, 1240)
USTA_MCU = (USTA_X + 20, 1500, 760)
USTA_CU = (USTA_X + 30, 1420, 600)
DENIZ_MCU = (DENIZ_X - 40, 1640, 640)
OTS = (USTA_X - 40, 1520, 940)
EMRE_WIDE = (110, 1400, 1.2, 10)
EMRE_OTS = (60, 1240, 1.7, 20)


def push(cam, t, t0, t1, amount=0.05):
    k = smooth((t - t0) / max(t1 - t0, 0.01))
    return (cam[0], cam[1], cam[2] * (1 - amount * k))


def S(t0, t1, fn):
    return (t0, t1, fn)


@functools.lru_cache(None)
def _ins(name, *a):
    return getattr(ins, name)(*a)


SHOTS = [
    # 1 wide: Emre walks in, rope already on the counter
    S(0.0, 4.4, lambda t: shop(t, push(WIDE, t, 0, 4.4, 0.04), emre=(110 - 160 * (1 - smooth(t / 1.4)), 1400, 1.2, 10))),
    # 2 Deniz, bored
    S(4.4, 6.9, lambda t: shop(t, push(DENIZ_MCU, t, 4.4, 6.9), deniz_pose="deniz_2", deniz_amp=speaking(t, "D"), bg_blur=8, usta_blur=6)),
    # 3 Usta looks at Deniz
    S(6.9, 8.4, lambda t: shop(t, push(USTA_MCU, t, 6.9, 8.4), usta_pose="esref_3", bg_blur=8, deniz_blur=6)),
    # 4 phone goes face-down
    S(8.4, 9.6, plate(lambda t: _ins("phone", t < 8.75, "", "", "", True), 8.4, 9.6, 1.0, 1.04)),
    # 5 loupe on
    S(9.6, 12.0, lambda t: shop(t, push(USTA_CU, t, 9.6, 12.0, 0.06), bg_blur=9, deniz_blur=8, loupe=smooth((t - 10.0) / 0.45))),
    # 6 through the loupe
    S(12.0, 14.6, plate(lambda t: _ins("rope_end", True), 12.0, 14.6, 1.0, 1.08)),
    # 7 OTS on Usta, Emre answers
    S(14.6, 16.8, lambda t: shop(t, push(OTS, t, 14.6, 16.8, 0.03), bg_blur=7, deniz_blur=6, loupe=1, emre=EMRE_OTS)),
    # 8 Usta
    S(16.8, 18.2, lambda t: shop(t, push(USTA_MCU, t, 16.8, 18.2), bg_blur=8, deniz_blur=6, loupe=1)),
    # 9 wide, slow push while Emre explains
    S(18.2, 22.6, lambda t: shop(t, push(WIDE, t, 18.2, 22.6, 0.12), loupe=1, emre=EMRE_WIDE)),
    # 10 loupe off: "Bu kopmamış."
    S(22.6, 24.2, lambda t: shop(t, push(USTA_CU, t, 22.6, 24.2, 0.03), bg_blur=9, deniz_blur=8, loupe=1 - smooth((t - 22.7) / 0.4))),
    # 11 wide "Nasıl yani?"
    S(24.2, 25.9, lambda t: shop(t, WIDE, emre=EMRE_WIDE)),
    # 12 rope end close-up
    S(25.9, 32.4, plate(lambda t: _ins("rope_end", False), 25.9, 32.4, 1.0, 1.12, cx=0.62)),
    # 13 OTS: "O bıraktı."
    S(32.4, 35.0, lambda t: shop(t, push(OTS, t, 32.4, 35.0, 0.03), bg_blur=7, deniz_blur=6, emre=EMRE_OTS)),
    # 14 silent beat
    S(35.0, 37.2, lambda t: shop(t, push(USTA_CU, t, 35.0, 37.2, 0.05), bg_blur=9, deniz_blur=8)),
    # 15 Usta turns to the shelf, comes back with a parcel
    S(37.2, 39.4, lambda t: shop(t, WIDE, usta_pose="esref_4" if t < 38.5 else "esref_1", package=t >= 38.5, emre=EMRE_WIDE)),
    # 16 parcel unwrapped
    S(39.4, 42.4, plate(lambda t: _ins("package", round(min(1, max(0, (t - 39.6) / 1.8)) * 12) / 12), 39.4, 42.4, 1.0, 1.05)),
    # 17 frozen wide
    S(42.4, 43.8, lambda t: shop(t, push(WIDE, t, 42.4, 43.8, 0.03), package=True, emre=EMRE_WIDE)),
    # 18 "Dün geldi…"
    S(43.8, 47.3, lambda t: shop(t, push(USTA_MCU, t, 43.8, 47.3, 0.05), bg_blur=8, deniz_blur=6, package=True)),
    # 19 OTS "Ama hiç aramadı."
    S(47.3, 49.7, lambda t: shop(t, push(OTS, t, 47.3, 49.7, 0.03), bg_blur=7, deniz_blur=6, package=True, emre=EMRE_OTS)),
    # 20 "Sen de aramamışsın."
    S(49.7, 52.4, lambda t: shop(t, push(USTA_CU, t, 49.7, 52.4, 0.05), bg_blur=9, deniz_blur=8, package=True)),
    # 21 Deniz whispers
    S(52.4, 55.0, lambda t: shop(t, push(DENIZ_MCU, t, 52.4, 55.0, 0.05), deniz_pose="deniz_1", deniz_amp=speaking(t, "D"), bg_blur=8, usta_blur=6, package=True)),
    # 22 the line
    S(55.0, 63.8, lambda t: shop(t, push(USTA_MCU, t, 55.0, 63.8, 0.16), bg_blur=8, deniz_blur=6, package=True)),
    # 23 knot
    S(63.8, 67.0, plate(lambda t: _ins("rope_halves", t >= 65.0), 63.8, 67.0, 1.0, 1.06)),
    # 24 wide "Borcum ne?"
    S(67.0, 69.6, lambda t: shop(t, push(WIDE, t, 67.0, 69.6, 0.03), rope="knot", package=True, emre=EMRE_WIDE)),
    # 25 smile
    S(69.6, 73.8, lambda t: shop(t, push(USTA_MCU, t, 69.6, 73.8, 0.07), usta_pose="esref_2", bg_blur=8, deniz_blur=6, rope="knot", package=True)),
    # 26 calling Murat
    S(73.8, 77.6, plate(lambda t: _ins("phone", True, "Arkadaşlık · 12 yıl", "Murat", "aranıyor…", True), 73.8, 77.6, 1.0, 1.07)),
    # 27 ticket
    S(77.6, 86.0, plate(lambda t: _ins("ticket", round(min(1, max(0, (t - 78.0) / 5.6)) * 60) / 60, round(min(1, max(0, (t - 84.2) / 0.35)) * 8) / 8), 77.6, 86.0, 1.04, 1.0)),
    # 28 closing card
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
    is_card = t >= 86.0
    img = finish(img, t, dust=not is_card, grain=True)
    if t < 86.0:
        img = subtitle(img, sub_at(t))
    # fade in / out
    if t < 0.4:
        img = Image.eval(img, lambda v, k=t / 0.4: int(v * k))
    if t > TOTAL - 0.6:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.6: int(v * max(k, 0)))
    if 85.7 <= t < 86.3:  # dip to black into the card
        k = abs(t - 86.0) / 0.3
        img = Image.eval(img, lambda v, k=k: int(v * min(1, k)))
    return img


def audio_mix(out):
    inputs, filters, labels = [], [], []
    def add(path, at, vol=1.0, extra=""):
        idx = len(inputs) // 2; inputs.extend(["-i", path])
        ms = int(at * 1000)
        filters.append(f"[{idx}:a]aresample=44100,aformat=channel_layouts=stereo{extra},volume={vol},adelay={ms}|{ms}[a{idx}]")
        labels.append(f"[a{idx}]")
    for i, (f, _, _) in enumerate(LINES):
        add(f"{REP}/{f}.mp3", START[i], 1.0)
    add(f"{SFX}/ortam.mp3", 0.0, 0.32, ",aloop=loop=4:size=2e6,atrim=0:90,afade=t=out:st=86:d=3")
    add(f"{SFX}/cingirak.mp3", 0.0, 0.6)
    add(f"{SFX}/ip.mp3", 0.9, 0.5)
    add(f"{SFX}/telefon_cevir.mp3", 8.7, 0.7)
    add(f"{SFX}/loupe.mp3", 10.25, 0.8)
    add(f"{SFX}/loupe.mp3", 22.8, 0.5)
    add(f"{SFX}/gazete.mp3", 39.5, 0.7)
    add(f"{SFX}/dugum.mp3", 64.0, 0.7)
    add(f"{SFX}/telefon.mp3", 74.4, 0.45)
    add(f"{SFX}/cingirak_cikis.mp3", 76.2, 0.45)
    add(f"{SFX}/kalem.mp3", 78.0, 0.7)
    add(f"{SFX}/damga.mp3", 84.2, 0.8)
    add(f"{SFX}/muzik.mp3", 50.0, 0.30, ",afade=t=in:st=0:d=3,afade=t=out:st=36.5:d=3.5")
    n = len(labels)
    fc = ";".join(filters) + ";" + "".join(labels) + f"amix=inputs={n}:normalize=0:duration=longest,atrim=0:{TOTAL},alimiter=limit=0.95[out]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-c:a", "pcm_s16le", out], check=True)


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
        n0, n1 = int(round(a * FPS)), int(round(b * FPS))
        for n in range(n0, n1):
            p.stdin.write(frame_at(n / FPS).convert("RGB").tobytes())
        p.stdin.close(); p.wait()
    elif mode == "audio":
        audio_mix(sys.argv[2])
