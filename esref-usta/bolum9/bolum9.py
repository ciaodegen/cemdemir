"""Bölüm 9 — "Uzak Mesafe İlişkisi Yürür mü?" (~45 sn)."""
import sys, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum9")
from PIL import Image, ImageDraw
from engine import W, H, UI, FPS, ROOT, finish, subtitle, envelope, duration, smooth, font, FONT_SERIF_B
import scenes3d as s3
from scenes3d import (shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU,
                      USTA_BACK_OTS, loupe_in, loupe_out)
from scenes import split_sub, plate
import inserts as ins
import inserts_bilet as ib

REP = f"{ROOT}/bolum9/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = Burak), subtitle (None = text on screen)
    ("01_B", "E", "Usta, uzak mesafe ilişkisi yürür mü? Ben İstanbul'dayım, o İzmir'de… Herkes 'bitecek' diyor!"),
    ("02_D", "D", "Yürümez usta! Benimki Kadıköy–Üsküdar'dı, o bile yürümedi!"),
    ("03_U", "U", "Deniz."),
    ("04_U", "U", "Dur, bir bakalım…"),
    ("05_U", "U", None),
    ("06_U", "U", "Bakalım ne kadar uzak."),
    ("07_U", "U", "Haritada dört yüz seksen kilometre evlat. Burada sıfır. Yol uzunsa, sevgi kısa değil demektir."),
    ("08_B", "E", "Cuma yine yoldayım."),
    ("09_D", "D", "Ben yine de yürümez diyorum."),
    ("03_U", "U", "Deniz."),
]
START = {0: 0.4, 1: 6.6, 2: 9.65, 3: 10.95, 4: 15.3, 5: 20.9, 6: 25.3, 7: 33.6, 8: 42.0, 9: 43.65}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
T_TICKET, T_CTA, T_END = 35.4, 39.4, 41.8
TOTAL = 45.2
FIELDS = (("Arıza:", "İstanbul–İzmir, 480 km."),
          ("Yapılan işlem:", "Ölçüldü. Kalpte 0 cm."),
          ("Not:", "Yol uzunsa, sevgi kısa değil."))
S5 = START[4]
NOTE_SEG = [(0, S5, S5 + 0.86), (1, S5 + 1.49, S5 + 2.53), (2, S5 + 3.14, S5 + 4.7)]
TICKET_T = (13.4, 13.8, 14.2, 14.6, 15.0)
S7 = START[6]


def notes_at(t):
    out = []
    for (i, a, b) in NOTE_SEG:
        n = len(ib.TICKETS[i][1])
        out.append(n if t >= b else (0 if t < a else int(n * (t - a) / (b - a))))
    return tuple(out)


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["E"] = [34.6]
s3.BLINKS["U"] = [2.4, 12.0, 22.6, 31.5, 36.0]
s3.BLINKS["D"] = [1.8, 7.9, 43.0]


def sub_at(t):
    for i, (f, s, txt) in enumerate(LINES):
        if txt and START[i] - 0.05 <= t < START[i] + DUR[i] + 0.2:
            parts = split_sub(txt)
            if len(parts) == 1:
                return txt
            k = (t - START[i]) / max(DUR[i], 0.1)
            L = [len(p) for p in parts]; acc = 0
            for p, l in zip(parts, L):
                acc += l / sum(L)
                if k < acc:
                    return p
            return parts[-1]
    return ""


@functools.lru_cache(None)
def _ticket(progress, stamp):
    return ins.ticket(progress, stamp, "009", FIELDS, "MESAFE YOK")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Kilometrelerce uzaktaki", "sevgiline gönder."), "Eşref Usta · Bölüm 9")


def S(t0, t1, fn):
    return (t0, t1, fn)


def k01(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def shot_open(t):
    return shop(t, push(WIDE, t, 0, 6.5, 0.04), deniz="D_phone", rope="tickets" if t >= 1.1 else "none",
                emre_back=(120 - 220 * (1 - smooth(min(1.0, t / 1.0))), 560, 0.95, 5, "B_back", 0.85))


def shot_bakalim(t):
    p = loupe_in(t, 12.8)
    cam = push(USTA_CU, t, 10.85, 13.3, 0.06)
    if p is None:
        return shop(t, cam, usta="E_front", rope="tickets", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="tickets", bg_blur=9, deniz_blur=8, usta_blinks=False)


def shot_tickets(t):
    n = sum(1 for tt in TICKET_T if t >= tt)
    return ib.tickets_plate(n, notes_at(t))


def shot_olcelim(t):
    p = loupe_out(t, 20.55)
    cam = push(USTA_CU, t, 20.5, 22.4, 0.04)
    if p is None:
        return shop(t, cam, usta="E_serious", rope="tickets", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, usta_mouth=0, rope="tickets", bg_blur=9, deniz_blur=8)


def shot_tape(t):
    k = smooth(k01(t, 22.55, 23.8))
    return ib.tickets_plate(5, (99, 99, 99), round(k, 2), ib.km_counter(round(k * 20) / 20))


def shot_chest(t):
    k = smooth(k01(t, 28.7, 29.4))
    counter = "0 cm" if k >= 1 else ib.km_counter(1 - k)
    return ib.chest_plate(counter, int(round(k * 20)))


@functools.lru_cache(None)
def _tag():
    w, h = int(940 * UI / 1.5), int(230 * UI / 1.5)
    tag = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(tag)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=int(24 * UI / 1.5), fill=(246, 234, 205, 240), outline=(176, 36, 36, 255), width=int(6 * UI / 1.5))
    f1 = font(FONT_SERIF_B, int(48 * UI / 1.5)); f2 = font(FONT_SERIF_B, int(36 * UI / 1.5))
    for txt, f, y, c in (("SİZCE UZAK MESAFE YÜRÜR MÜ?", f1, 0.17, (40, 26, 16, 255)), ("Yorumlara yaz", f2, 0.6, (150, 30, 30, 255))):
        tw = d.textlength(txt, font=f); d.text(((w - tw) / 2, h * y), txt, font=f, fill=c)
    return tag.rotate(-2, expand=True, resample=Image.BICUBIC)


def shot_stinger(t):
    img = shop(t, push((s3.DENIZ_X - 30, 1450, 740), t, T_END, TOTAL, 0.05), deniz="D_whisper", rope="none", deniz_blur=0, bg_blur=8, usta_blur=6)
    k = smooth(k01(t, T_END + 0.3, T_END + 0.8))
    if k > 0:
        tg = _tag().copy()
        if k < 1:
            tg.putalpha(tg.split()[3].point(lambda v: int(v * k)))
        img.alpha_composite(tg, ((W - tg.size[0]) // 2, int(H * 0.115 - 40 * (1 - k) * UI)))
    return img


SHOTS = [
    S(0.0, 6.5, shot_open),
    S(6.5, 9.55, lambda t: shop(t, push(DENIZ_MCU, t, 6.5, 9.55), deniz="D_sincere", rope="tickets", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(9.55, 10.85, lambda t: shop(t, push(USTA_MCU, t, 9.55, 10.85), usta="E_side", deniz="D_sincere", rope="tickets", bg_blur=8, deniz_blur=6)),
    S(10.85, 13.3, shot_bakalim),
    S(13.3, 20.5, plate(shot_tickets, 13.3, 20.5, 1.05, 1.18, 0.5, 0.3)),
    S(20.5, 22.4, shot_olcelim),
    S(22.4, 25.2, plate(shot_tape, 22.4, 25.2, 1.0, 1.04, 0.5, 0.5)),
    S(25.2, 28.2, lambda t: shop(t, push(USTA_CU, t, 25.2, 28.2, 0.06), usta="E_soft", rope="tickets", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(28.2, 30.0, plate(shot_chest, 28.2, 30.0, 1.0, 1.08)),
    S(30.0, 33.4, lambda t: shop(t, push(USTA_CU, t, 30.0, 33.4, 0.08), usta="E_soft", rope="tickets", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(33.4, T_TICKET, lambda t: door(t, push(EMRE_CU, t, 33.4, T_TICKET, 0.05), emre="B_soft", rope="tickets")),
    S(T_TICKET, T_CTA, plate(lambda t: _ticket(round(k01(t, T_TICKET + 0.2, T_TICKET + 2.7) * 60) / 60, round(k01(t, T_CTA - 0.75, T_CTA - 0.4) * 8) / 8), T_TICKET, T_CTA, 1.04, 1.0)),
    S(T_CTA, T_END, plate(lambda t: _cta(), T_CTA, T_END, 1.0, 1.0)),
    S(T_END, TOTAL, shot_stinger),
]


def frame_at(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            img = fn(t)
            break
    else:
        img = Image.new("RGB", (W, H))
    img = finish(img, t, dust=False, grain=False)
    if t < T_TICKET or t >= T_END:
        img = subtitle(img, sub_at(t), 0.62 if t < 6.5 else 0.705)
    if t > TOTAL - 0.5:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.5: int(v * max(k, 0)))
    for tc in (T_CTA, T_END):
        if tc - 0.3 <= t < tc + 0.3:
            k = abs(t - tc) / 0.3
            img = Image.eval(img, lambda v, k=k: int(v * min(1, k)))
    return img


def audio_mix(out):
    inputs, filters, labels = [], [], []
    def add(path, at, vol=1.0, extra=""):
        idx = len(inputs) // 2; inputs.extend(["-i", path])
        ms = int(at * 1000)
        filters.append(f"[{idx}:a]aresample=44100,aformat=channel_layouts=stereo{extra},volume={vol},adelay={ms}|{ms}[a{idx}]")
        labels.append(f"[a{idx}]")
    for i, (f, sp, _) in enumerate(LINES):
        add(f"{REP}/{f}.mp3", START[i], 1.1 if sp == "E" else 1.0)
    add(f"{SFX}/ortam.mp3", 0.0, 0.32, f",aloop=loop=4:size=2e6,atrim=0:{TOTAL},afade=t=out:st={TOTAL - 3}:d=2.5")
    add(f"{SFX}/cingirak.mp3", 0.0, 0.6)
    add(f"{SFX}/fis_carpma.mp3", 1.05, 0.8)
    add(f"{SFX}/loupe.mp3", 12.8, 0.5)
    for tt in TICKET_T:
        add(f"{SFX}/kagit_birakma.mp3", tt - 0.05, 0.7)
    for (_, a, b) in NOTE_SEG:
        add(f"{SFX}/kalem.mp3", a, 0.3, f",atrim=0:{b - a:.2f},afade=t=out:st={max(0, b - a - 0.2):.2f}:d=0.2")
    add(f"{SFX}/serit_metre.mp3", 22.5, 0.85)
    add(f"{SFX}/serit_geri.mp3", 28.65, 0.85)
    add(f"{SFX}/kalem.mp3", T_TICKET + 0.2, 0.7, ",atrim=0:2.5,afade=t=out:st=2.1:d=0.4")
    add(f"{SFX}/damga.mp3", T_CTA - 0.75, 0.8)
    add(f"{SFX}/muzik.mp3", 13.3, 0.24, f",afade=t=in:st=0:d=2.5,afade=t=out:st={T_END - 13.3 - 1.5}:d=1.5")
    fc = ";".join(filters) + ";" + "".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{TOTAL},alimiter=limit=0.95[out]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-c:a", "pcm_s16le", out], check=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        for tt in sys.argv[3:]:
            frame_at(float(tt)).convert("RGB").save(f"{sys.argv[2]}/still_{float(tt):05.1f}.jpg", quality=88)
    elif mode == "video":
        out, a, b = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for n in range(int(round(a * FPS)), int(round(b * FPS))):
            p.stdin.write(frame_at(n / FPS).convert("RGB").tobytes())
        p.stdin.close(); p.wait()
    elif mode == "audio":
        audio_mix(sys.argv[2])
