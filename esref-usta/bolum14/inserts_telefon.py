"""Bölüm 14 (Borç) telefon çekimleri: arkadaşın Bodrum story'si ve mesajlaşma (tatilden borç isteği, Usta'nın yazdırdığı cevap, "Görüldü")."""
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
INVITE = "Kanka bin lira atabilir misin? Ay sonu toplu veririm"
REPLY = "Atarım kanka. Önce beş bini gönder… bini hemen geri atarım."


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


@functools.lru_cache(None)
def _beach(w, h, label=True):
    """Small holiday photo: sky, sea, sun, a boat, sand, and a pin label."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for i in range(h):
        k = i / h
        if k < 0.5:
            c = (int(120 + 100 * k), int(190 + 40 * k), 245)
        elif k < 0.78:
            c = (30, int(130 + 40 * (k - 0.5)), 190)
        else:
            c = (236, 214, 160)
        d.line([(0, i), (w, i)], fill=c + (255,))
    r = min(w, h) * 0.08
    d.ellipse([w * 0.76 - r, h * 0.2 - r, w * 0.76 + r, h * 0.2 + r], fill=(255, 236, 140, 255))
    d.polygon([(w * 0.25, h * 0.6), (w * 0.42, h * 0.6), (w * 0.39, h * 0.66), (w * 0.28, h * 0.66)], fill=(250, 250, 250, 255))
    d.line([(w * 0.33, h * 0.6), (w * 0.33, h * 0.42)], fill=(250, 250, 250, 255), width=3)
    d.polygon([(w * 0.335, h * 0.43), (w * 0.335, h * 0.58), (w * 0.43, h * 0.58)], fill=(250, 250, 250, 255))
    for x0 in (0.12, 0.62):   # umbrellas
        d.pieslice([w * x0, h * 0.7, w * (x0 + 0.2), h * 0.86], 180, 360, fill=(230, 70, 60, 255))
        d.line([(w * (x0 + 0.1), h * 0.78), (w * (x0 + 0.1), h * 0.95)], fill=(90, 70, 50, 255), width=3)
    if not label:
        return im
    f = font(FONT_BOLD, max(14, h // 9))
    t = "Bodrum"
    tw = d.textlength(t, font=f)
    d.rounded_rectangle([w / 2 - tw / 2 - 40, h * 0.06, w / 2 + tw / 2 + 16, h * 0.06 + h // 7], radius=10, fill=(255, 255, 255, 230))
    d.ellipse([w / 2 - tw / 2 - 30, h * 0.06 + h // 28, w / 2 - tw / 2 - 12, h * 0.06 + h // 28 + 18], fill=(220, 50, 60, 255))
    d.text((w / 2 - tw / 2 - 4, h * 0.06 + 2), t, font=f, fill=(30, 26, 24, 255))
    return im


def _photo_bubble(img, y, pop=1.0):
    pw, ph = 380, 290
    b = Image.new("RGBA", (pw + 24, ph + 24), (0, 0, 0, 0))
    ImageDraw.Draw(b).rounded_rectangle([0, 0, pw + 23, ph + 23], radius=28, fill=(255, 255, 255, 255), outline=(214, 204, 188, 255), width=2)
    m = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=20, fill=255)
    b.paste(_beach(pw, ph), (12, 12), m)
    if pop < 1:
        s = 0.6 + 0.4 * pop
        b = b.resize((max(1, int(b.size[0] * s)), max(1, int(b.size[1] * s))), Image.LANCZOS)
        b.putalpha(b.split()[3].point(lambda v: int(v * pop)))
    if pop > 0:
        img.alpha_composite(b, (30, int(y)))
    return y + ph + 24 + 20


def chat_screen(invite=0.0, typed=0, sent=False, typing=False, seen=False):
    scr = Image.new("RGBA", (SW, SH), (238, 230, 214, 255))
    d = ImageDraw.Draw(scr)
    # faint pattern
    for yy in range(240, SH, 90):
        for xx in range((yy // 90 % 2) * 45, SW, 90):
            d.ellipse([xx - 3, yy - 3, xx + 3, yy + 3], fill=(228, 218, 200, 255))
    # messages are laid out on a tall layer, then scrolled so the newest one sits above the input bar
    lay = Image.new("RGBA", (SW, 3000), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    y = 250
    for side, text, date in OLD:
        y = _bubble(lay, ld, side, text, y, extra=date)
    if invite > 0:
        y = _photo_bubble(lay, y + 10, pop=min(1.0, invite * 1.6))
        if invite > 0.35:
            y = _bubble(lay, ld, "in", INVITE, y, extra="21:46", pop=min(1.0, (invite - 0.35) / 0.65), emoji_tail="🙏")
    if sent:
        y = _bubble(lay, ld, "out", REPLY, y, extra="21:47 ✓✓")
        if typing:
            y = _bubble(lay, ld, "in", "yazıyor…", y)
        if seen:
            f = font(FONT_BOLD, 42)
            t = "Görüldü"
            ld.text((SW - 40 - ld.textlength(t, font=f), y - 12), t, font=f, fill=(52, 120, 220, 255))
            y += 50
    off = max(0, y - (SH - 170))
    scr.alpha_composite(lay.crop((0, off, SW, off + SH)))
    d = ImageDraw.Draw(scr)
    _header(d, "yazıyor…" if typing else "çevrimiçi")
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
    scr = _beach(SW, SH, label=False).copy()
    d = ImageDraw.Draw(scr)
    scr.alpha_composite(Image.new("RGBA", (SW, 190), (0, 0, 0, 60)))
    d = ImageDraw.Draw(scr)
    d.rounded_rectangle([24, 30, SW - 24, 38], radius=4, fill=(255, 255, 255, 110))
    d.rounded_rectangle([24, 30, 24 + (SW - 48) * progress, 38], radius=4, fill=(255, 255, 255, 255))
    d.ellipse([30, 66, 114, 150], fill=(120, 150, 196, 255))
    d.text((58, 80), "K", font=font(FONT_BOLD, 48), fill=(255, 255, 255, 255))
    d.text((132, 82), "kerem", font=font(FONT_BOLD, 38), fill=(255, 255, 255, 255))
    d.text((132, 122), "2 sa", font=font(FONT_REG, 28), fill=(255, 240, 230, 255))
    # drink on the sand + caption sticker
    cx, cy = SW // 2 + 120, int(SH * 0.86)
    d.polygon([(cx - 60, cy - 150), (cx + 60, cy - 150), (cx + 30, cy), (cx - 30, cy)], fill=(255, 150, 90, 230))
    d.line([(cx + 10, cy - 150), (cx + 50, cy - 230)], fill=(240, 240, 240, 255), width=8)
    d.ellipse([cx - 70, cy - 175, cx - 20, cy - 125], fill=(250, 220, 60, 255))
    f = font(FONT_BOLD, 60)
    t = "Kafa dinliyoruz"
    tw = d.textlength(t, font=f)
    d.rounded_rectangle([SW / 2 - tw / 2 - 30, SH * 0.42, SW / 2 + tw / 2 + 30, SH * 0.42 + 96], radius=20, fill=(255, 255, 255, 235))
    d.text((SW / 2 - tw / 2, SH * 0.42 + 12), t, font=f, fill=(30, 26, 24, 255))
    scr.alpha_composite(emoji("😎", 80), (int(SW / 2 - 40), int(SH * 0.42 + 110)))
    f = font(FONT_BOLD, 50); t = "Bodrum"; tw = d.textlength(t, font=f)
    d.rounded_rectangle([SW / 2 - tw / 2 - 56, SH * 0.3, SW / 2 + tw / 2 + 26, SH * 0.3 + 80], radius=16, fill=(255, 255, 255, 235))
    d.ellipse([SW / 2 - tw / 2 - 42, SH * 0.3 + 26, SW / 2 - tw / 2 - 14, SH * 0.3 + 54], fill=(220, 50, 60, 255))
    d.text((SW / 2 - tw / 2, SH * 0.3 + 10), t, font=f, fill=(30, 26, 24, 255))
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
