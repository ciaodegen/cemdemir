"""Static close-up plates (1440x2560) for insert shots, ticket and closing card."""
import math, random, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from engine import draw_rope, font, FONT_BOLD, FONT_SERIF_B, FONT_HAND

BW, BH = 1440, 2560


@functools.lru_cache(None)
def wood_top(seed=2, warmth=1.0):
    rng = np.random.default_rng(seed)
    y = np.arange(BH, dtype=np.float32)[:, None]
    x = np.arange(BW, dtype=np.float32)[None, :]
    plank_h = 430
    pid = (y // plank_h)
    warp = np.sin(x * 0.0017 + pid * 1.7) * 18 + np.sin(x * 0.0061 + pid) * 5
    yy = y + warp
    grain = 0.55 * np.sin(yy * 0.21) + 0.3 * np.sin(yy * 0.53 + 1.3) + 0.15 * np.sin(yy * 1.31)
    noise = rng.normal(0, 1, (BH // 4, BW // 32)).astype(np.float32)
    noise = np.asarray(Image.fromarray(noise).resize((BW, BH), Image.BICUBIC))
    tone = 0.62 + 0.05 * grain + 0.05 * noise + ((pid * 37) % 5) * 0.025
    seams = (np.abs(y % plank_h) < 4).astype(np.float32)
    col = np.stack([128 * tone, 80 * tone, 46 * tone], -1) * warmth
    col *= (1 - 0.55 * seams)[..., None]
    r = np.sqrt(((x - BW * 0.5) / (BW * 0.75)) ** 2 + ((y - BH * 0.42) / (BH * 0.5)) ** 2)
    col *= (1.25 - 0.85 * np.clip(r, 0, 1.2) ** 1.5)[..., None]
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")


def shadowed(img, obj, blur=18, off=(14, 22), alpha=150):
    a = obj.split()[3]
    sh = Image.new("RGBA", obj.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: v * alpha // 255))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(sh, (off[0], off[1]))
    img.alpha_composite(obj)


def phone(face_up=True, text_top="", text_main="", text_sub="", lit=True):
    img = wood_top(3).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(obj)
    box = [400, 760, 1040, 2060]
    if face_up:
        d.rounded_rectangle(box, radius=90, fill=(18, 18, 22, 255))
        scr = [box[0] + 28, box[1] + 28, box[2] - 28, box[3] - 28]
        if lit:
            d.rounded_rectangle(scr, radius=66, fill=(26, 40, 58, 255))
            g = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
            ImageDraw.Draw(g).ellipse([scr[0] - 60, scr[1] + 200, scr[2] + 60, scr[1] + 1000], fill=(70, 110, 150, 120))
            obj.alpha_composite(g.filter(ImageFilter.GaussianBlur(120)))
            d = ImageDraw.Draw(obj)
            if text_top:
                f = font(FONT_BOLD, 46); tw = d.textlength(text_top, font=f)
                d.text(((BW - tw) / 2, scr[1] + 170), text_top, font=f, fill=(190, 205, 220, 255))
            if text_main:
                d.ellipse([BW / 2 - 120, scr[1] + 300, BW / 2 + 120, scr[1] + 540], fill=(110, 130, 150, 255))
                f0 = font(FONT_BOLD, 120); ini = text_main[0]; tw = d.textlength(ini, font=f0)
                d.text(((BW - tw) / 2, scr[1] + 345), ini, font=f0, fill=(235, 240, 245, 255))
                f = font(FONT_BOLD, 92); tw = d.textlength(text_main, font=f)
                d.text(((BW - tw) / 2, scr[1] + 600), text_main, font=f, fill=(245, 248, 252, 255))
            if text_sub:
                f = font(FONT_BOLD, 50); tw = d.textlength(text_sub, font=f)
                d.text(((BW - tw) / 2, scr[1] + 730), text_sub, font=f, fill=(170, 190, 210, 255))
                # red end-call button + green
                d.ellipse([BW / 2 - 85, scr[3] - 260, BW / 2 + 85, scr[3] - 90], fill=(214, 64, 58, 255))
        else:
            d.rounded_rectangle(scr, radius=66, fill=(8, 8, 10, 255))
        d.rounded_rectangle([box[0] + 6, box[1] + 6, box[2] - 6, box[1] + 120], radius=80, outline=(80, 80, 90, 160), width=4)
    else:
        d.rounded_rectangle(box, radius=90, fill=(44, 46, 52, 255))
        d.rounded_rectangle([box[0] + 60, box[1] + 60, box[0] + 330, box[1] + 330], radius=60, fill=(30, 31, 36, 255))
        for cx, cy in ((box[0] + 140, box[1] + 140), (box[0] + 250, box[1] + 140), (box[0] + 140, box[1] + 250)):
            d.ellipse([cx - 44, cy - 44, cx + 44, cy + 44], fill=(12, 12, 14, 255), outline=(90, 92, 100, 255), width=5)
        g = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        ImageDraw.Draw(g).rounded_rectangle([box[0] + 40, box[1] + 30, box[0] + 180, box[3] - 30], radius=50, fill=(255, 255, 255, 30))
        obj.alpha_composite(g.filter(ImageFilter.GaussianBlur(30)))
    shadowed(img, obj, blur=30, off=(24, 36), alpha=170)
    return img


def _arc(cx, cy, r, a0, a1, n=24, sx=1.0):
    return [(cx + math.cos(math.radians(a0 + (a1 - a0) * i / n)) * r * sx,
             cy + math.sin(math.radians(a0 + (a1 - a0) * i / n)) * r) for i in range(n + 1)]


def reef_knot(obj, W=80, R=122, d=115, cx=720, cy=1290):
    """Two ropes joined with a reef knot: each bight passes through the other."""
    RB = R + W * 1.05
    A = [(-80, cy + R + 12), (260, cy + R + 4), (cx + d, cy + R)] + _arc(cx + d, cy, R, 90, -90, 30, sx=1.1)[1:] + \
        [(cx - 40, cy - R), (cx - d - RB * 1.1 - 60, cy - R - 12), (cx - d - RB * 1.1 - 200, cy - R - 85)]
    B_arc = _arc(cx - d, cy, RB, -90, -270, 36, sx=1.1)
    B_stand = [(1520, cy - RB - 12), (1180, cy - RB - 4), (cx - d + 30, cy - RB)] + B_arc[:3]
    B_tail = B_arc[-3:] + [(cx - d + 30, cy + RB), (cx + d + R * 1.1 + 60, cy + RB + 12), (cx + d + R * 1.1 + 200, cy + RB + 85)]
    draw_rope(obj, B_arc, W, "none", "none", seed=5)
    draw_rope(obj, A, W, "flat", "flat", seed=3)
    draw_rope(obj, B_stand, W, "flat", "none", seed=4)
    draw_rope(obj, B_tail, W, "none", "flat", seed=6)


def rope_halves(knotted=False, closeup=False):
    img = wood_top(5).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    if not knotted:
        a = [(-60, 1200), (200, 1180), (420, 1220), (600, 1200)]
        b = [(1500, 1390), (1250, 1360), (1030, 1400), (840, 1380)]
        draw_rope(obj, a, 80, end_a="flat", end_b="flat", seed=3)
        draw_rope(obj, b, 80, end_a="flat", end_b="flat", seed=4)
    else:
        reef_knot(obj)
    shadowed(img, obj, blur=22, off=(18, 28), alpha=160)
    return img


def rope_end(closeup_loupe=False):
    img = wood_top(7).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    pts = [(-200, 1600), (300, 1460), (650, 1330), (930, 1240)]
    draw_rope(obj, pts, 360, end_a="none", end_b="flat", seed=8)
    shadowed(img, obj, blur=40, off=(30, 50), alpha=170)
    if closeup_loupe:
        m = Image.new("L", (BW, BH), 0)
        ImageDraw.Draw(m).ellipse([BW / 2 - 640, 1280 - 640, BW / 2 + 640, 1280 + 640], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(26))
        dark = Image.new("RGBA", (BW, BH), (8, 5, 3, 255))
        lens = img.copy()
        # slight lens magnification + edge ring
        dark.paste(lens, (0, 0), m)
        ring = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse([BW / 2 - 650, 1280 - 650, BW / 2 + 650, 1280 + 650], outline=(20, 16, 12, 255), width=60)
        dark.alpha_composite(ring.filter(ImageFilter.GaussianBlur(14)))
        img = dark
    return img


def package(opened=0.0):
    """opened: 0 closed parcel, 1 fully unwrapped showing the other rope half + tag."""
    img = wood_top(9).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(obj)
    cx, cy = 720, 1300
    paper = (206, 200, 186, 255)
    def newsprint(box, seed):
        rnd = random.Random(seed)
        x0, y0, x1, y1 = box
        d.rectangle(box, fill=paper)
        y = y0 + 40
        hf = font(FONT_SERIF_B, 64)
        if seed % 2 == 0:
            d.text((x0 + 40, y), "GÜNÜN HABERLERİ", font=hf, fill=(60, 58, 54, 255)); y += 110
        cols = 3; cw = (x1 - x0 - 80) / cols
        for c in range(cols):
            yy = y
            while yy < y1 - 40:
                ln = cw - 30 - rnd.random() * 60
                d.rectangle([x0 + 40 + c * cw, yy, x0 + 40 + c * cw + ln, yy + 9], fill=(120, 116, 108, 255))
                yy += 26
    if opened < 0.5:
        k = opened / 0.5
        box = [cx - 420, cy - 300, cx + 420, cy + 300]
        newsprint(box, 2)
        # folds
        d.line([(box[0], box[1]), (cx, cy - 40), (box[2], box[1])], fill=(150, 144, 130, 255), width=6)
        if k < 0.6:
            d.line([(cx, box[1] - 10), (cx, box[3] + 10)], fill=(150, 110, 70, 255), width=14)
            d.line([(box[0] - 10, cy), (box[2] + 10, cy)], fill=(150, 110, 70, 255), width=14)
            d.ellipse([cx - 40, cy - 30, cx + 40, cy + 30], outline=(150, 110, 70, 255), width=14)
    else:
        k = (opened - 0.5) / 0.5
        spread = 0.6 + 0.4 * k
        box = [cx - 620 * spread, cy - 480 * spread, cx + 620 * spread, cy + 480 * spread]
        newsprint(box, 3)
        d.line([(cx, box[1]), (cx, box[3])], fill=(170, 164, 150, 255), width=5)
        d.line([(box[0], cy), (box[2], cy)], fill=(170, 164, 150, 255), width=5)
        # rope coil
        pts = []
        for i in range(0, 120):
            th = i / 119 * 2.6 * math.pi
            r = 330 - i * 1.6
            pts.append((cx + math.cos(th) * r * 1.15, cy + math.sin(th) * r * 0.85))
        draw_rope(obj, pts, 84, end_a="flat", end_b="flat", seed=31)
        # tag
        tag = Image.new("RGBA", (720, 300), (0, 0, 0, 0))
        td = ImageDraw.Draw(tag)
        td.polygon([(60, 0), (720, 0), (720, 300), (60, 300), (0, 150)], fill=(232, 214, 172, 255))
        td.ellipse([40, 128, 84, 172], fill=(120, 90, 60, 255))
        hf = font(FONT_HAND, 88)
        td.text((115, 96), "Murat — dün", font=hf, fill=(40, 44, 92, 255))
        tag = tag.rotate(-8, expand=True, resample=Image.BICUBIC)
        sh = Image.new("RGBA", obj.size, (0, 0, 0, 0)); sh.alpha_composite(tag, (int(cx - 260), int(cy + 380)))
        obj.alpha_composite(sh)
        ImageDraw.Draw(obj).line([(cx - 235, cy + 545), (cx - 60, cy + 290)], fill=(150, 110, 70, 255), width=8)
    shadowed(img, obj, blur=26, off=(20, 30), alpha=150)
    return img


def hand_text(d, xy, text, f, n_chars, color=(34, 40, 92, 255), seed=0):
    rnd = random.Random(seed)
    x, y = xy
    for i, ch in enumerate(text):
        if i >= n_chars:
            break
        dy = (rnd.random() - 0.5) * 5
        d.text((x, y + dy), ch, font=f, fill=color)
        x += d.textlength(ch, font=f) + (rnd.random() - 0.5) * 1.5
    return x


TICKET = [
    ("Arıza:", "İki taraf da diğerinin aramasını beklemiş."),
    ("Yapılan işlem:", "Düğüm."),
    ("Not:", "Kopan ip düğümlense de düğümü kalır derler. O düğüm, tutunacak yer olur."),
]


def ticket(progress, stamp=0.0, no="001"):
    """progress 0..1 reveals the handwriting; stamp 0..1 drops the stamp."""
    img = wood_top(11).copy()
    card = Image.new("RGBA", (1160, 1700), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, 1160, 1700], fill=(240, 230, 206, 255))
    # perforation top
    for x in range(20, 1160, 46):
        d.ellipse([x, -14, x + 24, 10], fill=(0, 0, 0, 0))
    f_small = font(FONT_SERIF_B, 40); f_head = font(FONT_SERIF_B, 92); f_lab = font(FONT_SERIF_B, 46)
    d.text((80, 90), "EŞREF USTA · TAMİR ATÖLYESİ", font=f_small, fill=(90, 60, 40, 255))
    d.line([(80, 160), (1080, 160)], fill=(120, 90, 60, 255), width=3)
    d.text((80, 200), "TAMİR FİŞİ", font=f_head, fill=(60, 36, 22, 255))
    d.text((800, 225), f"No: {no}", font=font(FONT_SERIF_B, 58), fill=(140, 40, 32, 255))
    fh = font(FONT_HAND, 60)
    total = sum(len(v) for _, v in TICKET)
    shown = int(progress * (total + 40))
    y = 400
    for i, (lab, val) in enumerate(TICKET):
        d.text((80, y), lab, font=f_lab, fill=(90, 60, 40, 255))
        y += 70
        lines = []
        cur = ""
        for w in val.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=fh) < 960:
                cur = t
            else:
                lines.append(cur); cur = w
        lines.append(cur)
        for ln in lines:
            d.line([(80, y + 78), (1080, y + 78)], fill=(190, 172, 140, 255), width=2)
            n = max(0, min(len(ln), shown))
            hand_text(d, (100, y), ln, fh, n, seed=i * 7 + len(ln))
            shown -= len(ln) + 1
            y += 92
        y += 50
    card = card.filter(ImageFilter.GaussianBlur(0.4))
    if stamp > 0:
        s = Image.new("RGBA", (700, 230), (0, 0, 0, 0))
        sd = ImageDraw.Draw(s)
        sd.rounded_rectangle([8, 8, 692, 222], radius=24, outline=(176, 42, 36, 255), width=12)
        ft = font(FONT_SERIF_B, 76); tw = sd.textlength("TAMİR EDİLDİ", font=ft)
        sd.text(((700 - tw) / 2, 66), "TAMİR EDİLDİ", font=ft, fill=(176, 42, 36, 255))
        rnd = np.random.default_rng(4).random((230, 700)) > 0.22
        a = np.asarray(s.split()[3]).copy(); a[~rnd] = (a[~rnd] * 0.3).astype(np.uint8)
        s.putalpha(Image.fromarray(a).point(lambda v: int(v * 0.85)))
        sc = 1.6 - 0.6 * min(1, stamp)
        s = s.resize((int(700 * sc), int(230 * sc))).rotate(12, expand=True, resample=Image.BICUBIC)
        a = s.split()[3].point(lambda v: int(v * min(1, stamp * 1.5)))
        s.putalpha(a)
        card.alpha_composite(s, (int(700 - s.size[0] / 2), int(1480 - s.size[1] / 2)))
    card = card.rotate(-2.2, expand=True, resample=Image.BICUBIC)
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    obj.alpha_composite(card, ((BW - card.size[0]) // 2, 400))
    shadowed(img, obj, blur=30, off=(20, 34), alpha=170)
    return img


def cta(lines=("Aramasını beklediğin", "kişiye gönder."), sub="Eşref Usta · Bölüm 1"):
    img = Image.new("RGBA", (BW, BH), (14, 10, 8, 255))
    d = ImageDraw.Draw(img)
    f = font(FONT_HAND, 112)
    y = 1080
    for ln in lines:
        tw = d.textlength(ln, font=f)
        d.text(((BW - tw) / 2, y), ln, font=f, fill=(244, 236, 220, 255)); y += 150
    fs = font(FONT_HAND, 54); tw = d.textlength(sub, font=fs)
    d.text(((BW - tw) / 2, y + 90), sub, font=fs, fill=(170, 150, 120, 255))
    return img
