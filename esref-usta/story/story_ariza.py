"""Story: 'Arızanı Eşref Usta'ya bırak, çözüm bulalım.' (1080x1920, soru kutusu için boş alan)."""
import sys, os
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
os.environ.setdefault("RES_W", "1080")
os.environ.setdefault("SPRITES", "sprites_hd")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import W, H, font, FONT_BOLD, FONT_SERIF_B, FONT_HAND
import scenes3d as s3

s3.speaking = lambda t, who: 0.0
INK = (30, 40, 110, 255)
BROWN = (70, 44, 24, 255)
RED = (176, 36, 36)


def centered(d, y, text, f, fill, x0=0, x1=W):
    tw = d.textlength(text, font=f)
    d.text((x0 + (x1 - x0 - tw) / 2, y), text, font=f, fill=fill)


def card(w=900, h=800):
    p = Image.new("RGBA", (w, h), (246, 234, 205, 255))
    d = ImageDraw.Draw(p)
    # torn top edge
    for x in range(0, w, 26):
        d.ellipse([x, -12, x + 18, 8], fill=(0, 0, 0, 0))
    d.text((50, 46), "EŞREF USTA · TAMİR ATÖLYESİ", font=font(FONT_SERIF_B, 30), fill=BROWN)
    d.line([(50, 92), (w - 50, 92)], fill=(120, 90, 60, 255), width=3)
    d.text((50, 112), "ARIZA KABUL FİŞİ", font=font(FONT_SERIF_B, 58), fill=(40, 26, 16, 255))
    fn = font(FONT_SERIF_B, 36)
    t = "No: Sen"
    d.text((w - 50 - d.textlength(t, font=fn), 128), t, font=fn, fill=(150, 30, 30, 255))
    fh = font(FONT_HAND, 66)
    centered(d, 218, "Arızanı Eşref Usta'ya bırak,", fh, INK, 0, w)
    centered(d, 296, "çözüm bulalım.", fh, INK, 0, w)
    d.text((50, 410), "Arıza:", font=font(FONT_SERIF_B, 34), fill=BROWN)
    # dotted lines = space for the question sticker
    for yy in (500, 580, 660):
        for x in range(50, w - 50, 22):
            d.line([(x, yy), (x + 10, yy)], fill=(150, 130, 100, 255), width=3)
    d.text((w - 330, h - 64), "*bazı şeyler hariç", font=font(FONT_HAND, 34), fill=(110, 80, 50, 255))
    # stamp
    st = Image.new("RGBA", (330, 104), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([5, 5, 325, 99], radius=12, outline=RED + (220,), width=6)
    centered(sd, 26, "KABUL EDİLİR", font(FONT_SERIF_B, 42), RED + (225,), 0, 330)
    rng = np.random.default_rng(5)
    a = np.array(st)
    a[..., 3] = (a[..., 3] * (rng.random(a.shape[:2]) > 0.18)).astype(np.uint8)
    st = Image.fromarray(a).rotate(7, expand=True, resample=Image.BICUBIC)
    p.alpha_composite(st, (40, h - st.size[1] - 6))
    return p.rotate(-2.2, expand=True, resample=Image.BICUBIC)


def main(out):
    cam = (650, 1670, 980)
    img = s3.shop(0.0, cam, usta="E_loupe", deniz="D_listen", rope="none", usta_blinks=False, deniz_blur=5, bg_blur=4).convert("RGBA")
    # warm vignette + darken bottom where the card sits
    y = np.linspace(0, 1, H)[:, None]
    shade = np.clip((y - 0.4) / 0.2, 0, 1) * 0.78
    ov = np.zeros((H, W, 4), np.uint8); ov[..., 0] = 18; ov[..., 1] = 11; ov[..., 2] = 6
    ov[..., 3] = (np.repeat(shade, W, 1) * 255).astype(np.uint8)
    img.alpha_composite(Image.fromarray(ov))
    c = card()
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    m = Image.new("L", c.size, 0); m.paste(c.split()[3])
    blk = Image.new("RGBA", c.size, (0, 0, 0, 170)); blk.putalpha(m.point(lambda v: int(v * 0.65)))
    cx, cy = (W - c.size[0]) // 2, 880
    sh.alpha_composite(blk, (cx + 14, cy + 26))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(c, (cx, cy))
    img.convert("RGB").save(out, quality=95)


if __name__ == "__main__":
    main(sys.argv[1])
