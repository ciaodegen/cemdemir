"""Bölüm 4 (Çalmayan Telefon) detay çekimleri: eski tuşlu telefon, arama geçmişi, gelen arama."""
import sys, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_BOLD
import inserts as ins

BW, BH = 1440, 2560
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def _phone_body(obj, cx, cy, screen_fn):
    d = ImageDraw.Draw(obj)
    w, h = 560, 1200
    x0, y0 = cx - w / 2, cy - h / 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=110, fill=(52, 56, 64, 255))
    d.rounded_rectangle([x0 + 18, y0 + 18, x0 + w - 18, y0 + h - 18], radius=96, outline=(84, 90, 100, 255), width=6)
    # screen bezel + screen
    sx0, sy0, sx1, sy1 = x0 + 70, y0 + 110, x0 + w - 70, y0 + 560
    d.rounded_rectangle([sx0 - 14, sy0 - 14, sx1 + 14, sy1 + 14], radius=30, fill=(28, 30, 34, 255))
    scr = Image.new("RGBA", (int(sx1 - sx0), int(sy1 - sy0)), (150, 178, 120, 255))
    screen_fn(ImageDraw.Draw(scr), scr.size)
    obj.alpha_composite(scr, (int(sx0), int(sy0)))
    # keypad
    kf = font(FONT_BOLD, 44)
    keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"]
    d.rounded_rectangle([x0 + 90, y0 + 600, x0 + 240, y0 + 660], radius=24, fill=(70, 150, 80, 255))
    d.rounded_rectangle([x0 + w - 240, y0 + 600, x0 + w - 90, y0 + 660], radius=24, fill=(170, 60, 56, 255))
    for i, k in enumerate(keys):
        r, c = divmod(i, 3)
        kx = x0 + 100 + c * 130; ky = y0 + 700 + r * 112
        d.rounded_rectangle([kx, ky, kx + 100, ky + 84], radius=26, fill=(196, 198, 204, 255))
        tw = d.textlength(k, font=kf); d.text((kx + 50 - tw / 2, ky + 16), k, font=kf, fill=(40, 40, 46, 255))


@functools.lru_cache(None)
def call_log():
    img = ins.wood_top(43).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    def scr(d, size):
        w, h = size
        f = font(MONO, 34); fb = font(MONO, 38)
        d.rectangle([0, 0, w, 64], fill=(110, 138, 86, 255))
        d.text((20, 12), "Gelen aramalar", font=fb, fill=(20, 30, 14, 255))
        rows = (("Oğlum", "Kurban Bay."), ("Kızım", "Ramazan Bay."), ("Oğlum", "Anneler Günü"), ("Kızım", "Yılbaşı"))
        y = 90
        for name, when in rows:
            d.text((20, y), name, font=fb, fill=(20, 30, 14, 255))
            tw = d.textlength(when, font=f); d.text((w - 20 - tw, y + 4), when, font=f, fill=(40, 56, 30, 255))
            d.line([(20, y + 66), (w - 20, y + 66)], fill=(120, 146, 96, 255), width=2)
            y += 84
    _phone_body(obj, 720, 1300, scr)
    ins.shadowed(img, obj, blur=34, off=(22, 36), alpha=180)
    return img


@functools.lru_cache(maxsize=16)
def ringing(shake=0):
    img = ins.wood_top(43).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    def scr(d, size):
        w, h = size
        d.rectangle([0, 0, w, h], fill=(176, 206, 140, 255))
        fb = font(MONO, 40); fbig = font(MONO, 56)
        for t, y, f_ in (("Gelen arama", 60, fb), ("Eşref Usta", 170, fbig)):
            tw = d.textlength(t, font=f_); d.text(((w - tw) / 2, y), t, font=f_, fill=(20, 30, 14, 255))
        cx = w / 2
        d.ellipse([cx - 40, 300, cx + 40, 380], outline=(20, 30, 14, 255), width=8)
        for k in (1, 2):
            d.arc([cx - 40 - 30 * k, 300 - 30 * k, cx + 40 + 30 * k, 380 + 30 * k], 300, 60, fill=(20, 30, 14, 255), width=6)
            d.arc([cx - 40 - 30 * k, 300 - 30 * k, cx + 40 + 30 * k, 380 + 30 * k], 120, 240, fill=(20, 30, 14, 255), width=6)
    dx = (-10, 10, -6, 6, 0)[shake % 5]
    _phone_body(obj, 720 + dx, 1300, scr)
    # vibration marks
    d = ImageDraw.Draw(obj)
    for sx in (-1, 1):
        for k in range(3):
            x = 720 + sx * (330 + k * 34)
            d.line([(x, 1120 + k * 20), (x, 1480 - k * 20)], fill=(255, 236, 200, 150 - k * 40), width=8)
    ins.shadowed(img, obj, blur=34, off=(22, 36), alpha=180)
    return img


@functools.lru_cache(None)
def deniz_calls_mom():
    return ins.phone(True, "", "Anne", "aranıyor…", True)


if __name__ == "__main__":
    ims = [call_log(), ringing(0), ringing(1), deniz_calls_mom()]
    sheet = Image.new("RGB", (360 * len(ims), 640))
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((360, 640)), (i * 360, 0))
    sheet.save(sys.argv[1])
