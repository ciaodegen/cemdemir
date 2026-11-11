"""Bölüm 14 (Borç) telefon çekimleri: arkadaşın yeni telefon story'si ve mesajlaşma (pizza daveti, Usta'nın yazdırdığı cevap, "Görüldü")."""
import sys, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from engine import font, FONT_BOLD
import inserts as ins

BW, BH = 1440, 2560
FONT_REG = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
FONT_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
BOX = (370, 560, 1070, 2040)
SCR = (BOX[0] + 26, BOX[1] + 26, BOX[2] - 26, BOX[3] - 26)
SW, SH = SCR[2] - SCR[0], SCR[3] - SCR[1]

OLD = [("out", "Kanka şu 5 bin?", "Eylül"), ("in", "Ay sonu veriyorum kanka", "Eylül"), ("out", "Kanka?", "Ekim")]
INVITE = "Kanka akşam maç var, bize gel. Pizzalar benden!"
REPLY = "Gelirim kanka. Pizzalar senden… beş bin de senden."


@functools.lru_cache(None)
def emoji(ch, size):
    f = ImageFont.truetype(FONT_EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((size, int(size * im.size[1] / im.size[0])), Image.LANCZOS)


def _wrap(d, text, f, maxw):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def _header(d, status):
    d.rectangle([0, 0, SW, 210], fill=(246, 240, 228, 255))
    d.line([(0, 210), (SW, 210)], fill=(222, 212, 196, 255), width=3)
    d.text((34, 96), "‹", font=font(FONT_BOLD, 70), fill=(120, 96, 70, 255))
    d.ellipse([90, 92, 186, 188], fill=(120, 150, 196, 255))
    d.text((122, 106), "K", font=font(FONT_BOLD, 56), fill=(255, 255, 255, 255))
    d.text((210, 98), "Kerem", font=font(FONT_BOLD, 46), fill=(40, 32, 26, 255))
    col = (40, 150, 90, 255) if status == "yazıyor…" else (130, 116, 100, 255)
    d.text((210, 152), status, font=font(FONT_REG, 32), fill=col)
    # status bar
    d.text((40, 24), "21:47", font=font(FONT_BOLD, 30), fill=(60, 50, 40, 255))
    d.rounded_rectangle([SW - 110, 28, SW - 50, 56], radius=6, outline=(60, 50, 40, 255), width=3)
    d.rectangle([SW - 106, 32, SW - 80, 52], fill=(60, 50, 40, 255))


def _bubble(img, d, side, text, y, extra=None, pop=1.0, emoji_tail=None):
    f = font(FONT_REG, 40)
    lines = _wrap(d, text, f, SW - 260)
    tw = max(d.textlength(l, font=f) for l in lines) + (60 if emoji_tail else 0)
    bw, bh = int(tw + 64), 30 + 52 * len(lines) + (40 if extra else 10)
    x0 = SW - 30 - bw if side == "out" else 30
    b = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    bd = ImageDraw.Draw(b)
    fill = (214, 236, 196, 255) if side == "out" else (255, 255, 255, 255)
    bd.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=30, fill=fill, outline=(214, 204, 188, 255), width=2)
    for i, l in enumerate(lines):
        bd.text((32, 20 + 52 * i), l, font=f, fill=(36, 30, 26, 255))
    if emoji_tail:
        e = emoji(emoji_tail, 50)
        lw = bd.textlength(lines[-1], font=f)
        b.alpha_composite(e, (int(32 + lw + 10), 20 + 52 * (len(lines) - 1)))
    if extra:
        ef = font(FONT_REG, 26)
        ew = bd.textlength(extra, font=ef)
        bd.text((bw - 28 - ew, bh - 40), extra, font=ef, fill=(120, 112, 100, 255))
    if pop < 1:
        s = 0.6 + 0.4 * pop
        b = b.resize((max(1, int(bw * s)), max(1, int(bh * s))), Image.LANCZOS)
        b.putalpha(b.split()[3].point(lambda v: int(v * pop)))
        x0 += (bw - b.size[0]) // (1 if side == "out" else 1000)
    img.alpha_composite(b, (int(x0), int(y)))
    return y + bh + 26


def chat_screen(invite=0.0, typed=0, sent=False, typing=False, seen=False):
    scr = Image.new("RGBA", (SW, SH), (238, 230, 214, 255))
    d = ImageDraw.Draw(scr)
    # faint pattern
    for yy in range(240, SH, 90):
        for xx in range((yy // 90 % 2) * 45, SW, 90):
            d.ellipse([xx - 3, yy - 3, xx + 3, yy + 3], fill=(228, 218, 200, 255))
    _header(d, "yazıyor…" if typing else "çevrimiçi")
    y = 250
    for side, text, date in OLD:
        y = _bubble(scr, d, side, text, y, extra=date)
    if invite > 0:
        y = _bubble(scr, d, "in", INVITE, y + 10, extra="21:46", pop=min(1.0, invite), emoji_tail="🍕")
    if sent:
        y = _bubble(scr, d, "out", REPLY, y, extra="21:47 ✓✓" if not seen else "21:47 ✓✓")
        if typing:
            y = _bubble(scr, d, "in", "yazıyor…", y)
        if seen:
            f = font(FONT_BOLD, 42)
            t = "Görüldü"
            d.text((SW - 40 - d.textlength(t, font=f), y - 12), t, font=f, fill=(52, 120, 220, 255))
    # input bar
    d.rectangle([0, SH - 150, SW, SH], fill=(246, 240, 228, 255))
    d.rounded_rectangle([24, SH - 128, SW - 130, SH - 30], radius=48, fill=(255, 255, 255, 255), outline=(214, 204, 188, 255), width=2)
    if typed > 0 and not sent:
        f = font(FONT_REG, 36)
        s = REPLY[:typed]
        while d.textlength(s, font=f) > SW - 210:
            s = s[1:]
        d.text((56, SH - 100), s, font=f, fill=(36, 30, 26, 255))
        cx = 56 + d.textlength(s, font=f) + 4
        d.line([(cx, SH - 104), (cx, SH - 56)], fill=(40, 150, 90, 255), width=3)
    else:
        d.text((56, SH - 100), "Mesaj", font=font(FONT_REG, 36), fill=(160, 150, 136, 255))
    d.ellipse([SW - 112, SH - 128, SW - 14, SH - 30], fill=(40, 150, 90, 255))
    d.polygon([(SW - 82, SH - 100), (SW - 40, SH - 79), (SW - 82, SH - 58)], fill=(255, 255, 255, 255))
    return scr


def story_screen(progress=1.0):
    scr = Image.new("RGBA", (SW, SH), (0, 0, 0, 255))
    d = ImageDraw.Draw(scr)
    for i in range(SH):   # warm gradient
        k = i / SH
        d.line([(0, i), (SW, i)], fill=(int(250 - 60 * k), int(170 - 90 * k), int(110 + 40 * k), 255))
    d.rounded_rectangle([24, 30, SW - 24, 38], radius=4, fill=(255, 255, 255, 110))
    d.rounded_rectangle([24, 30, 24 + (SW - 48) * progress, 38], radius=4, fill=(255, 255, 255, 255))
    d.ellipse([30, 66, 114, 150], fill=(120, 150, 196, 255))
    d.text((58, 80), "K", font=font(FONT_BOLD, 48), fill=(255, 255, 255, 255))
    d.text((132, 82), "kerem", font=font(FONT_BOLD, 38), fill=(255, 255, 255, 255))
    d.text((132, 122), "dün", font=font(FONT_REG, 28), fill=(255, 240, 230, 255))
    # unboxing: box + brand-new phone
    cx, cy = SW // 2, SH // 2 + 40
    d.rounded_rectangle([cx - 230, cy - 60, cx + 230, cy + 340], radius=26, fill=(250, 248, 244, 255))
    d.rounded_rectangle([cx - 200, cy - 30, cx + 200, cy + 310], radius=20, fill=(236, 232, 226, 255))
    d.rounded_rectangle([cx - 150, cy - 420, cx + 150, cy + 200], radius=46, fill=(30, 30, 36, 255))
    d.rounded_rectangle([cx - 132, cy - 402, cx + 132, cy + 182], radius=36, fill=(110, 80, 190, 255))
    g = Image.new("RGBA", scr.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([cx - 120, cy - 380, cx + 140, cy - 80], fill=(255, 150, 200, 200))
    scr.alpha_composite(g.filter(ImageFilter.GaussianBlur(50)))
    d = ImageDraw.Draw(scr)
    for k, ox in enumerate((-80, -10)):
        d.rounded_rectangle([cx + ox - 30, cy - 390, cx + ox + 30, cy - 330], radius=30, fill=(20, 20, 24, 255))
    f = font(FONT_BOLD, 64)
    t = "Yeni bebeğim"
    tw = d.textlength(t, font=f)
    d.rounded_rectangle([cx - tw / 2 - 64, 196, cx + tw / 2 + 66, 296], radius=20, fill=(255, 255, 255, 235))
    d.text((cx - tw / 2 - 34, 208), t, font=f, fill=(30, 26, 24, 255))
    scr.alpha_composite(emoji("😍", 64), (int(cx + tw / 2 - 22), 214))
    return scr


def phone_plate(screen):
    img = ins.wood_top(181).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(obj)
    d.rounded_rectangle(BOX, radius=96, fill=(20, 20, 24, 255))
    m = Image.new("L", (SW, SH), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, SW - 1, SH - 1], radius=72, fill=255)
    obj.paste(screen, (SCR[0], SCR[1]), m)
    d.rounded_rectangle([BW // 2 - 70, SCR[1] + 14, BW // 2 + 70, SCR[1] + 50], radius=18, fill=(14, 14, 16, 255))
    ins.shadowed(img, obj, blur=28, off=(20, 32), alpha=160)
    return img


@functools.lru_cache(maxsize=128)
def chat_plate(invite_q=0, typed=0, sent=False, typing=False, seen=False):
    return phone_plate(chat_screen(invite_q / 10, typed, sent, typing, seen))


@functools.lru_cache(maxsize=32)
def story_plate(prog_q=20):
    return phone_plate(story_screen(prog_q / 20))


def screen_point(x, y):
    return SCR[0] + x, SCR[1] + y


if __name__ == "__main__":
    ims = [story_plate(10), chat_plate(10), chat_plate(10, 30), chat_plate(10, len(REPLY), True, True), chat_plate(10, len(REPLY), True, False, True)]
    sheet = Image.new("RGB", (360 * len(ims), 640))
    for i, x in enumerate(ims):
        sheet.paste(x.convert("RGB").resize((360, 640)), (i * 360, 0))
    sheet.save(sys.argv[1])
