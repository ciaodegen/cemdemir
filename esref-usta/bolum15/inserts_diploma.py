"""Bölüm 15 (Üniversite) çekimleri: tezgâhtaki diploma (büyüteç altında parlayan bölüm adı) ve ret mailleriyle dolu gelen kutusu."""
import sys, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum14")
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_BOLD, FONT_SERIF_B, FONT_HAND
import inserts as ins
import inserts_telefon as itl

BW, BH = 1440, 2560
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
DW, DH = 1120, 820
DCX, DCY = 720, 1300
ROT = 2
DEPT_Y = 470


def _centered(d, y, text, f, fill):
    tw = d.textlength(text, font=f)
    d.text(((DW - tw) / 2, y), text, font=f, fill=fill)
    return (DW - tw) / 2, tw


def diploma(glow=0.0):
    im = Image.new("RGBA", (DW, DH), (248, 242, 224, 255))
    d = ImageDraw.Draw(im)
    # paper tone + ornamental border
    for i in range(0, DH, 4):
        d.line([(0, i), (DW, i)], fill=(248 - (i % 12) // 6, 242 - (i % 12) // 6, 224, 255))
    for k, (pad, col, w) in enumerate(((22, (150, 112, 50, 255), 6), (38, (180, 140, 70, 255), 2), (48, (150, 112, 50, 255), 2))):
        d.rectangle([pad, pad, DW - pad, DH - pad], outline=col, width=w)
    for cx, cy in ((48, 48), (DW - 48, 48), (48, DH - 48), (DW - 48, DH - 48)):
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline=(150, 112, 50, 255), width=3)
    ink = (52, 40, 30, 255)
    _centered(d, 86, "T.C.", font(SERIF, 34), ink)
    _centered(d, 128, "ÇINARALTI ÜNİVERSİTESİ", font(FONT_SERIF_B, 52), (120, 30, 30, 255))
    _centered(d, 200, "DİPLOMA", font(FONT_SERIF_B, 86), ink)
    _centered(d, 312, "Zeynep Yılmaz", font(SERIF_I, 56), (30, 40, 90, 255))
    _centered(d, 396, "Güzel Sanatlar Fakültesi", font(SERIF, 36), ink)
    f = font(FONT_SERIF_B, 50)
    t = "Grafik Tasarım Bölümü'nü"
    x0, tw = _centered(d, DEPT_Y, t, f, ink)
    if glow > 0:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([x0 - 80, DEPT_Y - 40, x0 + tw + 80, DEPT_Y + 100], fill=(255, 214, 90, int(210 * glow)))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(40)))
        d = ImageDraw.Draw(im)
        d.text((x0, DEPT_Y), t, font=f, fill=(int(52 + 150 * glow), int(40 + 100 * glow), int(30 * (1 - glow)), 255))
    _centered(d, 548, "başarıyla tamamlayarak LİSANS diploması almaya hak kazanmıştır.", font(SERIF, 30), ink)
    _centered(d, 600, "Haziran 2024", font(SERIF_I, 30), ink)
    # signatures + seal
    for sx in (190, DW - 330):
        d.line([(sx, 712), (sx + 160, 712)], fill=ink, width=2)
        d.line([(sx + 20, 700), (sx + 60, 680), (sx + 80, 704), (sx + 130, 676)], fill=(30, 40, 90, 255), width=3)
    d.ellipse([DW / 2 - 70, 640, DW / 2 + 70, 780], fill=(176, 40, 40, 255))
    d.ellipse([DW / 2 - 52, 658, DW / 2 + 52, 762], outline=(230, 150, 140, 255), width=4)
    _centered(d, 692, "ÇÜ", font(FONT_SERIF_B, 40), (250, 220, 210, 255))
    # gentle curl shading on the left/right edges (it was rolled up)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for k in range(40):
        a = int(70 * (1 - k / 40))
        sd.line([(k, 0), (k, DH)], fill=(60, 40, 20, a)); sd.line([(DW - 1 - k, 0), (DW - 1 - k, DH)], fill=(60, 40, 20, a))
    im.alpha_composite(sh)
    return im


@functools.lru_cache(maxsize=64)
def diploma_plate(glow_q=0):
    img = ins.wood_top(191).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    dp = diploma(glow_q / 20).rotate(ROT, expand=True, resample=Image.BICUBIC)
    obj.alpha_composite(dp, (DCX - dp.size[0] // 2, DCY - dp.size[1] // 2))
    # the red ribbon it was rolled with, lying beside it
    d = ImageDraw.Draw(obj)
    d.line([(260, DCY + 470), (420, DCY + 520), (560, DCY + 500), (700, DCY + 560)], fill=(180, 30, 40, 255), width=22, joint="curve")
    ins.shadowed(img, obj, blur=22, off=(14, 22), alpha=130)
    return img


def diploma_point(x, y):
    return DCX - DW / 2 + x, DCY - DH / 2 + y


MAILS = [("Kuzey Ajans", "Başvurunuz hakkında", "Maalesef bu aşamada başka bir adayla…"),
         ("Pixel Medya", "Başvurunuz Hk.", "Deneyim kriterini karşılamadığınız için…"),
         ("Mavi Reklam", "Başvurunuz hakkında", "İlginiz için teşekkür ederiz, ancak…"),
         ("Atlas Yayın", "Pozisyon güncellemesi", "Aradığımız profil en az 3 yıl…"),
         ("Nokta Tasarım", "Başvurunuz hakkında", "Maalesef olumlu dönüş yapamıyoruz…"),
         ("Lale Basım", "Başvurunuz Hk.", "Pozisyon dolmuştur, ilginiz için…"),
         ("Yön Kreatif", "Başvurunuz hakkında", "Şu an için deneyimli bir adayla…"),
         ("Orkide Reklam", "Başvuru sonucu", "Maalesef değerlendirme sonucunda…")]
NEW = ("Ekin Dijital", "Başvurunuz hakkında", "Maalesef bu pozisyon için deneyimli…")


def _mail_row(d, y, sender, subj, prev, unread=False, time="Dün"):
    d.ellipse([30, y + 18, 110, y + 98], fill=(150, 160, 190, 255) if not unread else (220, 90, 80, 255))
    d.text((56, y + 34), sender[0], font=font(FONT_BOLD, 40), fill=(255, 255, 255, 255))
    fb = font(FONT_BOLD if unread else itl.FONT_REG, 36)
    d.text((134, y + 10), sender, font=fb, fill=(30, 26, 24, 255))
    tf = font(itl.FONT_REG, 28)
    d.text((itl.SW - 40 - d.textlength(time, font=tf), y + 16), time, font=tf, fill=(110, 100, 90, 255))
    d.text((134, y + 54), subj, font=font(FONT_BOLD if unread else itl.FONT_REG, 32), fill=(40, 34, 30, 255))
    d.text((134, y + 92), prev, font=font(itl.FONT_REG, 28), fill=(120, 110, 100, 255))
    d.line([(134, y + 140), (itl.SW, y + 140)], fill=(226, 220, 210, 255), width=2)
    return y + 144


def mail_screen(new=0.0):
    scr = Image.new("RGBA", (itl.SW, itl.SH), (252, 250, 246, 255))
    d = ImageDraw.Draw(scr)
    d.text((40, 24), "14:02", font=font(FONT_BOLD, 30), fill=(60, 50, 40, 255))
    d.text((40, 96), "Gelen Kutusu", font=font(FONT_BOLD, 56), fill=(30, 26, 24, 255))
    n = "113" if new > 0.5 else "112"
    f = font(FONT_BOLD, 30)
    d.rounded_rectangle([itl.SW - 150, 110, itl.SW - 40, 158], radius=24, fill=(220, 90, 80, 255))
    d.text((itl.SW - 95 - d.textlength(n, font=f) / 2, 116), n, font=f, fill=(255, 255, 255, 255))
    y = 200 + int(144 * min(1.0, new))
    if new > 0:
        row = Image.new("RGBA", (itl.SW, 144), (255, 244, 236, 255))
        rd = ImageDraw.Draw(row)
        _mail_row(rd, 0, *NEW, unread=True, time="Şimdi")
        row.putalpha(row.split()[3].point(lambda v: int(v * min(1.0, new))))
        scr.alpha_composite(row, (0, 200 - int(144 * (1 - min(1.0, new)))))
    for m in MAILS:
        y = _mail_row(d, y, *m)
    return scr


@functools.lru_cache(maxsize=32)
def mail_plate(new_q=0):
    return itl.phone_plate(mail_screen(new_q / 10))


if __name__ == "__main__":
    ims = [diploma_plate(0), diploma_plate(20), mail_plate(0), mail_plate(10)]
    sheet = Image.new("RGB", (360 * len(ims), 640))
    for i, x in enumerate(ims):
        sheet.paste(x.convert("RGB").resize((360, 640)), (i * 360, 0))
    sheet.save(sys.argv[1])
