"""Bölüm 5 (Sigaranın Üstündeki Yazılar) detay çekimleri."""
import sys, math, random, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_SERIF_B, FONT_HAND, FONT_BOLD
import inserts as ins

BW, BH = 1440, 2560
PACK = (78, 70, 44, 255)          # plain-packaging olive brown
NOTES = ("Kızının düğünü", "Torununu kucağına alman", "Emekli olunca o deniz kenarı")


def cigarette(length, width, text=None, burnt=0.0, seed=0):
    """Horizontal cigarette sprite; burnt > 0 shortens the paper and chars the tip."""
    im = Image.new("RGBA", (int(length + 40), int(width + 40)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, y0 = 20, 20
    filt = length * 0.28
    paper = (length - filt) * (1 - burnt)
    d.rounded_rectangle([x0, y0, x0 + filt, y0 + width], radius=width * 0.2, fill=(210, 140, 70, 255))
    rnd = random.Random(seed)
    for _ in range(int(filt * width / 60)):
        px = rnd.uniform(x0, x0 + filt); py = rnd.uniform(y0, y0 + width)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(180, 110, 52, 255))
    d.rectangle([x0 + filt, y0, x0 + filt + paper, y0 + width], fill=(246, 244, 238, 255))
    d.line([(x0 + filt + 4, y0), (x0 + filt + 4, y0 + width)], fill=(220, 200, 150, 255), width=3)
    if text:
        f = font(FONT_HAND, int(width * 0.62))
        d.text((x0 + filt + 22, y0 + width * 0.12), text, font=f, fill=(40, 44, 92, 255))
    if burnt > 0:
        ex = x0 + filt + paper
        d.rectangle([ex - 10, y0, ex + 6, y0 + width], fill=(60, 52, 46, 255))
        d.ellipse([ex - 4, y0 - 2, ex + 14, y0 + width + 2], fill=(110, 104, 98, 255))
        im = im.crop((0, 0, int(ex + 30), im.size[1]))
    # soft cylindrical shading
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.rectangle([0, y0 + width * 0.7, im.size[0], y0 + width], fill=(0, 0, 0, 40))
    sd.rectangle([0, y0, im.size[0], y0 + width * 0.18], fill=(255, 255, 255, 50))
    alpha = im.split()[3]
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
    im.putalpha(alpha)
    return im


def pack_img(w=520, h=720):
    im = Image.new("RGBA", (w + 40, h + 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 160, 20 + w, 160 + h], radius=18, fill=PACK)
    # open lid behind with filters peeking out
    d.rounded_rectangle([20, 10, 20 + w, 200], radius=18, fill=(64, 58, 36, 255))
    for k in range(6):
        cx = 70 + k * 80
        d.ellipse([cx - 32, 130, cx + 32, 194], fill=(210, 140, 70, 255), outline=(170, 104, 50, 255), width=3)
    # warning box
    d.rectangle([50, 360, 20 + w - 30, 760], fill=(244, 244, 240, 255))
    d.rectangle([50, 360, 20 + w - 30, 760], outline=(20, 20, 20, 255), width=10)
    f = font(FONT_BOLD, 74)
    for t, y in (("SİGARA", 430), ("ÖLDÜRÜR", 540)):
        tw = d.textlength(t, font=f); d.text((20 + w / 2 - tw / 2, y), t, font=f, fill=(20, 20, 20, 255))
    return im


@functools.lru_cache(maxsize=8)
def counter_cigs(stage=0):
    """Pack top-left; stage 1..3 lays out the cigarettes with their notes one by one."""
    img = ins.wood_top(47).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    p = pack_img().rotate(8, expand=True, resample=Image.BICUBIC)
    obj.alpha_composite(p, (120, 360))
    for i in range(min(stage, 3)):
        c = cigarette(1100, 92, NOTES[i], seed=i).rotate(-3 + i * 2, expand=True, resample=Image.BICUBIC)
        obj.alpha_composite(c, (150 + i * 20, 1320 + i * 260))
    ins.shadowed(img, obj, blur=26, off=(18, 28), alpha=170)
    return img


@functools.lru_cache(None)
def loupe_note():
    src = ins.wood_top(53).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    c = cigarette(2100, 330, None, seed=9)
    obj.alpha_composite(c, (-420, 1100))
    d = ImageDraw.Draw(obj)
    f = font(FONT_HAND, 150)
    t = "Kızının düğünü"
    tw = d.textlength(t, font=f)
    d.text((720 - tw / 2 + 120, 1150), t, font=f, fill=(40, 44, 92, 255))
    ins.shadowed(src, obj, blur=30, off=(18, 30), alpha=160)
    m = Image.new("L", (BW, BH), 0)
    ImageDraw.Draw(m).ellipse([BW / 2 - 640, 1280 - 640, BW / 2 + 640, 1280 + 640], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(26))
    out = Image.new("RGBA", (BW, BH), (8, 5, 3, 255)); out.paste(src, (0, 0), m)
    ring = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([BW / 2 - 650, 1280 - 650, BW / 2 + 650, 1280 + 650], outline=(20, 16, 12, 255), width=60)
    out.alpha_composite(ring.filter(ImageFilter.GaussianBlur(14)))
    return out


@functools.lru_cache(None)
def ashtray():
    img = ins.wood_top(59).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(obj)
    cx, cy = 720, 1300
    d.ellipse([cx - 470, cy - 380, cx + 470, cy + 380], fill=(120, 132, 138, 255))
    d.ellipse([cx - 400, cy - 320, cx + 400, cy + 320], fill=(84, 92, 96, 255))
    for a in (90, 210, 330):
        x = cx + math.cos(math.radians(a)) * 440; y = cy + math.sin(math.radians(a)) * 350
        d.ellipse([x - 60, y - 40, x + 60, y + 40], fill=(70, 76, 80, 255))
    ash = Image.effect_noise((BW, BH), 40).convert("L")
    ash_l = Image.new("RGBA", (BW, BH), (150, 146, 140, 0))
    m = Image.new("L", (BW, BH), 0); ImageDraw.Draw(m).ellipse([cx - 300, cy - 200, cx + 300, cy + 220], fill=150)
    ash_l.putalpha(Image.composite(ash.point(lambda v: min(255, v)), Image.new("L", (BW, BH), 0), m).filter(ImageFilter.GaussianBlur(6)))
    obj.alpha_composite(ash_l)
    for i, (frag, rot, pos) in enumerate((("…ğü…", 18, (cx - 360, cy - 170)), ("…kuc…", -24, (cx - 260, cy + 40)))):
        c = cigarette(560, 92, frag, burnt=0.55, seed=20 + i).rotate(rot, expand=True, resample=Image.BICUBIC)
        obj.alpha_composite(c, pos)
    ins.shadowed(img, obj, blur=34, off=(22, 36), alpha=180)
    return img


@functools.lru_cache(maxsize=4)
def drawer(filled=False):
    img = Image.new("RGBA", (BW, BH), (34, 22, 14, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([60, 700, 1380, 2300], fill=(92, 58, 32, 255))
    d.rectangle([120, 760, 1320, 2240], fill=(58, 36, 20, 255))
    d.rectangle([60, 2160, 1380, 2300], fill=(110, 70, 40, 255))
    d.rounded_rectangle([560, 2190, 880, 2270], radius=10, fill=(196, 156, 78, 255))
    f = font(FONT_SERIF_B, 58); t = "EMANET"; tw = d.textlength(t, font=f)
    d.text((720 - tw / 2, 2196), t, font=f, fill=(70, 46, 20, 255))
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    # a few things others have left here before
    od = ImageDraw.Draw(obj)
    od.ellipse([220, 860, 420, 1060], outline=(190, 190, 196, 255), width=22)   # old watch case
    od.rectangle([1000, 900, 1220, 1180], fill=(140, 40, 40, 255))              # a little red box
    od.line([(260, 1700), (520, 1600)], fill=(200, 170, 100, 255), width=18)    # a key
    od.ellipse([500, 1570, 580, 1650], outline=(200, 170, 100, 255), width=18)
    if filled:
        p = pack_img().rotate(-12, expand=True, resample=Image.BICUBIC)
        obj.alpha_composite(p, (480, 1080))
    ins.shadowed(img, obj, blur=24, off=(14, 24), alpha=170)
    return img


if __name__ == "__main__":
    ims = [counter_cigs(0), counter_cigs(3), loupe_note(), ashtray(), drawer(True)]
    sheet = Image.new("RGB", (300 * len(ims), 533))
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((300, 533)), (i * 300, 0))
    sheet.save(sys.argv[1])
