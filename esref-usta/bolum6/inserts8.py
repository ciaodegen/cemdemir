"""Bölüm 6 (Ekstre) detay çekimleri: kredi kartı hesap özeti, satırlar, üstü çizilip 'Pazar' yazılması."""
import sys, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_SERIF_B, FONT_HAND, FONT_BOLD
import inserts as ins

BW, BH = 1440, 2560
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
ROWS = (("Babanla balık tutmak", "ERTELENDİ"),
        ("Oğlunun okul gösterisi", "ERTELENDİ"),
        ("Eşinle tatil", "SENEYE"))


def statement(rows=0, total=False, strike=0.0, pazar=0.0):
    """rows: how many lines are visible; strike/pazar 0..1 animate the pen on the first line."""
    w, h = 1180, 1700
    p = Image.new("RGBA", (w, h), (246, 244, 238, 255))
    d = ImageDraw.Draw(p)
    d.rectangle([0, 0, w, 150], fill=(32, 52, 92, 255))
    d.text((50, 40), "KREDİ KARTI HESAP ÖZETİ", font=font(FONT_BOLD, 56), fill=(240, 240, 245, 255))
    f_small = font(MONO, 30)
    d.text((50, 190), "Kart sahibi: HAKAN K.", font=f_small, fill=(70, 70, 80, 255))
    d.text((50, 240), "Dönem: Son 11 yıl", font=f_small, fill=(70, 70, 80, 255))
    d.line([(50, 310), (w - 50, 310)], fill=(160, 160, 170, 255), width=3)
    d.text((50, 330), "İŞLEM", font=font(MONO, 32), fill=(90, 90, 100, 255))
    tw = d.textlength("DURUM", font=font(MONO, 32)); d.text((w - 50 - tw, 330), "DURUM", font=font(MONO, 32), fill=(90, 90, 100, 255))
    fr = font(MONO, 50)
    y = 420
    for i, (item, st) in enumerate(ROWS):
        if i >= rows:
            break
        d.text((50, y), item, font=fr, fill=(30, 30, 36, 255))
        tw = d.textlength(st, font=fr)
        d.text((w - 50 - tw, y), st, font=fr, fill=(176, 36, 36, 255))
        if i == 0 and strike > 0:
            x0 = w - 50 - tw - 10
            d.line([(x0, y + 26), (x0 + (tw + 20) * min(1, strike), y + 20)], fill=(30, 40, 110, 255), width=9)
        if i == 0 and pazar > 0:
            hf = font(FONT_HAND, 92)
            t = "Pazar."
            n = max(1, int(len(t) * min(1, pazar)))
            d.text((w - 50 - tw - 30, y + 46), t[:n], font=hf, fill=(30, 40, 110, 255))
        d.line([(50, y + 150), (w - 50, y + 150)], fill=(214, 210, 200, 255), width=2)
        y += 190
    if total:
        d.rectangle([40, 1300, w - 40, 1460], fill=(250, 236, 236, 255), outline=(176, 36, 36, 255), width=5)
        ft = font(FONT_BOLD, 70)
        t = "TOPLAM BORÇ: 11 YIL"
        tw = d.textlength(t, font=ft); d.text(((w - tw) / 2, 1340), t, font=ft, fill=(150, 24, 24, 255))
    p = p.rotate(-2, expand=True, resample=Image.BICUBIC)
    img = ins.wood_top(61).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    obj.alpha_composite(p, ((BW - p.size[0]) // 2, 300))
    ins.shadowed(img, obj, blur=28, off=(18, 30), alpha=160)
    return img


@functools.lru_cache(maxsize=32)
def stmt(rows, total, strike_q, pazar_q):
    return statement(rows, total, strike_q / 10, pazar_q / 10)


@functools.lru_cache(None)
def loupe_first():
    src = Image.new("RGBA", (BW, BH), (246, 244, 238, 255))
    d = ImageDraw.Draw(src)
    for yy in range(0, BH, 190):
        d.line([(0, yy + 120), (BW, yy + 120)], fill=(222, 218, 208, 255), width=3)
    fr = font(MONO, 96)
    for t, y, col in (("Babanla balık", 1010, (30, 30, 36, 255)), ("tutmak", 1130, (30, 30, 36, 255)), ("ERTELENDİ", 1330, (176, 36, 36, 255))):
        tw = d.textlength(t, font=fr); d.text(((BW - tw) / 2, y), t, font=fr, fill=col)
    m = Image.new("L", (BW, BH), 0)
    ImageDraw.Draw(m).ellipse([BW / 2 - 640, 1280 - 640, BW / 2 + 640, 1280 + 640], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(26))
    out = Image.new("RGBA", (BW, BH), (8, 5, 3, 255)); out.paste(src, (0, 0), m)
    ring = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([BW / 2 - 650, 1280 - 650, BW / 2 + 650, 1280 + 650], outline=(20, 16, 12, 255), width=60)
    out.alpha_composite(ring.filter(ImageFilter.GaussianBlur(14)))
    return out


if __name__ == "__main__":
    ims = [loupe_first(), stmt(2, False, 0, 0), stmt(3, True, 0, 0), stmt(3, True, 10, 10)]
    sheet = Image.new("RGB", (360 * len(ims), 640))
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((360, 640)), (i * 360, 0))
    sheet.save(sys.argv[1])
