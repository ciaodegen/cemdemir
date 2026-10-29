"""Bölüm 2 detay çekimleri: kadife kutudaki gülüş, büyüteç görüntüleri, yedek gülüşler kavanozu."""
import sys, math, random, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_SERIF_B
import inserts as ins

BW, BH = 1440, 2560
ROOT = "/home/user/cemdemir/esref-usta"


def smile_mask(size, cx, cy, w, h, asym=0.0, chip=False):
    """Crescent smile: upper and lower arcs meeting at the corners; asym lifts the right corner."""
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    top, bot = [], []
    for i in range(61):
        x = -1 + 2 * i / 60
        lift = asym * (x + 1) / 2 * h * 0.55
        e = (1 - x * x)
        bot.append((cx + x * w / 2, cy + h * (e ** 0.8) * 0.78 - lift))
        top.append((cx + x * w / 2, cy + h * (e ** 1.6) * 0.16 - h * 0.1 * (e ** 0.5) - lift))
    d.polygon(top + bot[::-1], fill=255)
    if chip:
        bx, by = bot[18]
        d.polygon([(bx - w * 0.035, by + 6), (bx + w * 0.005, by - h * 0.16), (bx + w * 0.045, by + 6)], fill=0)
    return m.filter(ImageFilter.GaussianBlur(2.0))


def porcelain(size, mask, cx, cy, w, h, base=(244, 238, 228), dimple=None):
    arr = np.zeros((size[1], size[0], 3), np.float32)
    y, x = np.mgrid[0:size[1], 0:size[0]].astype(np.float32)
    ny = np.clip((y - cy) / (h * 0.7), -1, 1)
    shade = 0.82 + 0.22 * (1 - ny) / 2
    band = np.exp(-((y - (cy + h * 0.16)) / (h * 0.06)) ** 2) * 0.18
    arr[..., 0] = base[0] * shade + 255 * band
    arr[..., 1] = base[1] * shade + 250 * band
    arr[..., 2] = base[2] * shade + 240 * band
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    # soft rim shading from the mask edges
    edge = ImageChopsDiff(mask)
    img = Image.composite(Image.new("RGBA", size, (190, 176, 160, 255)), img, edge)
    if dimple:
        dx, dy, r = dimple
        g = Image.new("RGBA", size, (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([dx - r, dy - r * 0.8, dx + r, dy + r * 0.8], fill=(150, 120, 100, 150))
        ImageDraw.Draw(g).ellipse([dx - r * 0.5, dy - r * 0.6, dx + r * 0.4, dy - r * 0.05], fill=(255, 255, 255, 90))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * 0.25)))
    img.putalpha(mask)
    return img


def ImageChopsDiff(mask):
    inner = mask.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(5))
    from PIL import ImageChops
    return ImageChops.subtract(mask, inner)


@functools.lru_cache(None)
def velvet_box(opened=True):
    img = ins.wood_top(13).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(obj)
    cx, cy = 720, 1380
    if opened:
        # lid, tilted back
        d.rounded_rectangle([cx - 400, cy - 560, cx + 400, cy - 150], radius=60, fill=(92, 18, 30, 255))
        d.rounded_rectangle([cx - 360, cy - 520, cx + 360, cy - 190], radius=40, fill=(70, 12, 22, 255))
        d.rectangle([cx - 400, cy - 175, cx + 400, cy - 150], fill=(150, 120, 60, 255))
    d.rounded_rectangle([cx - 420, cy - 160, cx + 420, cy + 330], radius=60, fill=(110, 24, 38, 255))
    if opened:
        d.rounded_rectangle([cx - 370, cy - 120, cx + 370, cy + 280], radius=40, fill=(84, 14, 28, 255))
        d.ellipse([cx - 300, cy - 40, cx + 300, cy + 200], fill=(64, 10, 22, 255))
        tex = Image.effect_noise((BW, BH), 18).convert("L")
        velvet = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); velvet.putalpha(tex.point(lambda v: max(0, v - 120) // 3))
        obj.alpha_composite(velvet)
    else:
        d.rounded_rectangle([cx - 420, cy - 200, cx + 420, cy - 20], radius=60, fill=(130, 30, 46, 255))
        d.rectangle([cx - 420, cy - 40, cx + 420, cy - 20], fill=(150, 120, 60, 255))
    ins.shadowed(img, obj, blur=30, off=(22, 34), alpha=170)
    if opened:
        sw, sh_ = 640, 300
        sx, sy = cx, cy - 30
        m = smile_mask((BW, BH), sx, sy, sw, sh_, asym=0.55, chip=True)
        sm = porcelain((BW, BH), m, sx, sy, sw, sh_, dimple=(sx + sw * 0.37, sy + sh_ * 0.02 - sw * 0.0, 22))
        ins.shadowed(img, sm, blur=14, off=(10, 16), alpha=170)
    return img


def loupe_view(src, cx, cy, zoom):
    """Circular magnified view centred on (cx, cy) of a 1440x2560 plate."""
    w, h = BW / zoom, BH / zoom
    crop = src.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))).resize((BW, BH), Image.LANCZOS)
    m = Image.new("L", (BW, BH), 0)
    ImageDraw.Draw(m).ellipse([BW / 2 - 640, 1280 - 640, BW / 2 + 640, 1280 + 640], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(26))
    out = Image.new("RGBA", (BW, BH), (8, 5, 3, 255))
    out.paste(crop, (0, 0), m)
    ring = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([BW / 2 - 650, 1280 - 650, BW / 2 + 650, 1280 + 650], outline=(20, 16, 12, 255), width=60)
    out.alpha_composite(ring.filter(ImageFilter.GaussianBlur(14)))
    return out


@functools.lru_cache(None)
def loupe_dimple():
    return loupe_view(velvet_box(True), 720 + 640 * 0.33, 1380 - 30 - 300 * 0.05, 2.6)


@functools.lru_cache(None)
def loupe_chip():
    return loupe_view(velvet_box(True), 720 - 640 / 2 + 18 / 60 * 640, 1380 - 30 + 300 * 0.62, 2.6)


@functools.lru_cache(None)
def jar():
    bg = Image.open(f"{ROOT}/dukkan/src/duvar.png").convert("RGBA").crop((0, 600, 1440, 2000)).resize((BW, BH), Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
    img = bg
    d = ImageDraw.Draw(img)
    # shelf
    d.rectangle([0, 2050, BW, 2110], fill=(92, 60, 36, 255)); d.rectangle([0, 2110, BW, 2150], fill=(52, 32, 18, 255))
    jx0, jx1, jy0, jy1 = 330, 1110, 720, 2050
    inside = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    m_one = smile_mask((300, 170), 150, 50, 230, 110, asym=0.0)
    one = porcelain((300, 170), m_one, 150, 50, 230, 110, base=(250, 248, 244))
    rnd = random.Random(3)
    rows = 0
    y = jy1 - 150
    while y > jy0 + 260:
        x = jx0 + 40 + (rows % 2) * 60
        while x < jx1 - 260:
            inside.alpha_composite(one, (int(x + rnd.uniform(-6, 6)), int(y + rnd.uniform(-5, 5))))
            x += 150
        y -= 78; rows += 1
    jm = Image.new("L", (BW, BH), 0)
    ImageDraw.Draw(jm).rounded_rectangle([jx0, jy0 + 120, jx1, jy1], radius=90, fill=255)
    inside.putalpha(Image.fromarray(np.minimum(np.asarray(inside.split()[3]), np.asarray(jm))))
    img.alpha_composite(inside)
    glass = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); gd = ImageDraw.Draw(glass)
    gd.rounded_rectangle([jx0, jy0 + 120, jx1, jy1], radius=90, fill=(200, 225, 215, 40), outline=(230, 240, 235, 140), width=8)
    gd.rounded_rectangle([jx0 + 50, jy0 + 170, jx0 + 120, jy1 - 80], radius=35, fill=(255, 255, 255, 60))
    gd.rounded_rectangle([jx0 + 30, jy0, jx1 - 30, jy0 + 140], radius=20, fill=(176, 136, 70, 255))
    gd.rectangle([jx0 + 30, jy0 + 100, jx1 - 30, jy0 + 140], fill=(120, 88, 40, 255))
    img.alpha_composite(glass)
    # label
    lab = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); ld = ImageDraw.Draw(lab)
    ld.rectangle([jx0 + 120, 1260, jx1 - 120, 1520], fill=(239, 226, 196, 255))
    f = font(FONT_SERIF_B, 92)
    for t, yy in (("YEDEK", 1290), ("GÜLÜŞLER", 1400)):
        tw = ld.textlength(t, font=f); ld.text(((BW - tw) / 2, yy), t, font=f, fill=(60, 36, 22, 255))
    img.alpha_composite(lab)
    return img


if __name__ == "__main__":
    out = sys.argv[1]
    ims = [velvet_box(False), velvet_box(True), loupe_dimple(), loupe_chip(), jar()]
    sheet = Image.new("RGB", (360 * len(ims), 640))
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((360, 640)), (i * 360, 0))
    sheet.save(out)
