"""Bölüm 10 (Evlilikte Aşk Biter mi?) detay çekimleri: yaşlı el, sıkışmış yüzük, sabun, yüzüğün iç yüzündeki yazılar."""
import sys, math, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_SERIF_B, FONT_HAND
import inserts as ins

BW, BH = 1440, 2560
SKIN = (222, 168, 132, 255)
SKIN_D = (196, 140, 106, 255)
GOLD = (214, 168, 64, 255)
ENGR = [("14.02.1996", "H & S"), ("1996", "İlk ev, tek oda"), ("1999", "Kızımız doğdu"),
        ("2020", "Hastanede elimi bırakmadı")]


def _capsule(d, a, b, r, fill):
    d.line([a, b], fill=fill, width=int(2 * r))
    for p in (a, b):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)


@functools.lru_cache(maxsize=64)
def hand_plate(ring_q=0, soap_q=0):
    """Old hand resting on the counter, ring finger pointing down. ring_q 0..20 slides the ring toward the tip
    (it never comes off); soap_q 0..20 adds soap foam."""
    img = ins.wood_top(121).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(obj)
    # cardigan sleeve from the top
    d.rounded_rectangle([420, -60, 1060, 520], radius=120, fill=(84, 48, 32, 255))
    for x in range(440, 1040, 28):
        d.line([(x, 0), (x, 500)], fill=(74, 42, 28, 255), width=8)
    d.rounded_rectangle([440, 430, 1040, 560], radius=60, fill=(70, 40, 26, 255))
    # palm/back of hand
    d.rounded_rectangle([470, 500, 1010, 1160], radius=230, fill=SKIN)
    # knuckle shading + veins
    for i, x in enumerate((560, 680, 800, 920)):
        d.ellipse([x - 55, 1060, x + 55, 1150], fill=SKIN_D)
        d.line([(x, 620), (x + 10 * (i - 1.5), 1000)], fill=(200, 150, 140, 255), width=6)
    # fingers: index, middle, ring, little (ring finger third from the left in this view)
    fingers = [((555, 1120), (520, 1720), 72), ((685, 1130), (680, 1860), 76), ((815, 1130), (830, 1800), 74), ((935, 1110), (975, 1580), 62)]
    for a, b, r in fingers:
        _capsule(d, a, b, r, SKIN)
        # finger joints
        for f in (0.45, 0.75):
            jx = a[0] + (b[0] - a[0]) * f; jy = a[1] + (b[1] - a[1]) * f
            d.arc([jx - r * 0.7, jy - 18, jx + r * 0.7, jy + 18], 200, 340, fill=SKIN_D, width=5)
        nx, ny = b
        d.ellipse([nx - r * 0.55, ny - r * 0.2, nx + r * 0.55, ny + r * 0.85], fill=(236, 200, 182, 255))
    # thumb
    _capsule(d, (480, 880), (330, 1300), 68, SKIN)
    d.ellipse([290, 1270, 370, 1360], fill=(236, 200, 182, 255))
    # the ring on the ring finger (finger index 2)
    a, b, r = fingers[2]
    k = 0.30 + 0.10 * ring_q / 20
    rx = a[0] + (b[0] - a[0]) * k; ry = a[1] + (b[1] - a[1]) * k
    if ring_q:  # skin bunching where the ring is pulled
        d.ellipse([rx - r * 1.08, ry - 40 - 30, rx + r * 1.08, ry - 40 + 30], fill=SKIN_D)
    d.rounded_rectangle([rx - r * 1.05, ry - 42, rx + r * 1.05, ry + 42], radius=34, fill=GOLD)
    d.rounded_rectangle([rx - r * 0.96, ry - 32, rx + r * 0.96, ry - 10], radius=10, fill=(246, 214, 120, 255))
    d.line([(rx - r * 1.02, ry + 28), (rx + r * 1.02, ry + 28)], fill=(160, 118, 40, 255), width=8)
    if soap_q:
        rng = np.random.default_rng(4)
        for _ in range(int(soap_q / 20 * 40)):
            bx = rx + rng.uniform(-r * 1.6, r * 1.6); by = ry + rng.uniform(-110, 130); br = rng.uniform(10, 30)
            d.ellipse([bx - br, by - br, bx + br, by + br], fill=(250, 250, 252, 220), outline=(210, 220, 235, 255), width=3)
        # soap bar on the counter
        d.rounded_rectangle([1060, 1880, 1340, 2040], radius=50, fill=(236, 214, 170, 255))
        d.text((1120, 1925), "SABUN", font=font(FONT_SERIF_B, 48), fill=(170, 140, 100, 255))
    ins.shadowed(img, obj, blur=30, off=(18, 30), alpha=150)
    return img


@functools.lru_cache(None)
def _band():
    """Unrolled inner surface of the ring with all engravings spaced along it."""
    w, h = 6200, 560
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    v = y / h
    shade = 0.62 + 0.5 * np.sin(v * math.pi) ** 1.3
    col = np.stack([214 * shade, 168 * shade, 64 * shade], -1)
    # brushed metal
    rng = np.random.default_rng(2)
    n = np.repeat(rng.normal(0, 6, (h, 1)).astype(np.float32), w, 1)
    col += n[..., None]
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")
    return img


def _engrave(base, lines, cx, cy, alpha=1.0):
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for text, size, y in ((lines[0], 120, cy - 150), (lines[1], 78, cy + 10)):
        f = font(FONT_SERIF_B, size)
        tw = d.textlength(text, font=f)
        d.text((cx - tw / 2 + 3, y + 3), text, font=f, fill=(255, 236, 170, int(170 * alpha)))
        d.text((cx - tw / 2, y), text, font=f, fill=(92, 60, 18, int(255 * alpha)))
    base.alpha_composite(lay)


SLOT = 1240   # px between engravings on the band


@functools.lru_cache(maxsize=96)
def loupe_plate(pos_q, shown, glow_q=0):
    """Loupe view of the ring's inner surface. pos_q: band offset (x10 px); shown: how many engravings are cut so far."""
    band = _band().copy()
    for i in range(shown):
        _engrave(band, ENGR[i], 720 + i * SLOT, 270)
    view = band.crop((pos_q * 10, 0, pos_q * 10 + 1440, 560))
    out = Image.new("RGBA", (BW, BH), (10, 7, 4, 255))
    # ring band seen through the loupe, slightly curved
    v2 = view.resize((1440, 900), Image.LANCZOS)
    y, x = np.mgrid[0:900, 0:1440].astype(np.float32)
    curve = (1 - ((x - 720) / 900) ** 2) * 0.25 + 0.75
    a = np.asarray(v2).astype(np.float32)
    a[..., :3] *= curve[..., None]
    v2 = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    out.alpha_composite(v2, (0, 830))
    if glow_q:
        g = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([320, 1080, 1120, 1480], fill=(255, 236, 170, int(120 * glow_q / 20)))
        out.alpha_composite(g.filter(ImageFilter.GaussianBlur(70)))
    m = Image.new("L", (BW, BH), 0)
    ImageDraw.Draw(m).ellipse([BW / 2 - 660, 1280 - 660, BW / 2 + 660, 1280 + 660], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(26))
    res = Image.new("RGBA", (BW, BH), (8, 5, 3, 255)); res.paste(out, (0, 0), m)
    ring = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([BW / 2 - 670, 1280 - 670, BW / 2 + 670, 1280 + 670], outline=(20, 16, 12, 255), width=60)
    res.alpha_composite(ring.filter(ImageFilter.GaussianBlur(14)))
    return res


if __name__ == "__main__":
    ims = [hand_plate(0), hand_plate(20), hand_plate(14, 20), loupe_plate(0, 1), loupe_plate(SLOT * 2 // 10, 3, 12)]
    sheet = Image.new("RGB", (270 * len(ims), 480))
    for i, x in enumerate(ims):
        sheet.paste(x.convert("RGB").resize((270, 480)), (i * 270, 0))
    sheet.save(sys.argv[1])
