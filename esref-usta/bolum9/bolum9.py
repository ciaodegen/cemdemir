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

LINES = [  # file, speaker (E = customer), subtitle (None = text on screen)
    ("01_B", "E", "Usta, uzak mesafe ilişkisi yürür mü? Herkes 'bitecek' diyor!"),
    ("02_D", "D", "Yürümez usta! Benimki Kadıköy–Üsküdar'dı, o bile yürümedi!"),
    ("03_U", "U", "Deniz."),
    ("04_U", "U", "Dur, bir bakalım…"),
    ("05_U", "U", None),
    ("06_U", "U", "Bakalım ne kadar uzak."),
    ("07_U", "U", "Haritada dört yüz seksen kilometre evlat. Burada sıfır. Yol uzunsa, sevgi kısa değil demektir."),
    ("08_B", "E", "Usta… ben en iyisi cuma yine gideyim."),
    ("09_D", "D", "Ben yine de yürümez diyorum."),
    ("03_U", "U", "Deniz."),
]
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
# segment offsets inside the audio files (seconds, after speed-up)
NOTE_PARTS = [((0.0, 1.05), (1.05, 2.15)), ((2.48, 4.37), (4.59, 5.70)), ((5.96, 6.91), (7.31, 8.12))]
SEG07 = {"harita": (0.0, 2.79), "sifir": (3.41, 4.21), "yol": (4.67, 7.86)}

# ---- automatic layout ------------------------------------------------------------
T = {}
START = {}
t = 0.0
START[0] = 0.4
T["wide"] = (0.0, max(4.3, START[0] + DUR[0] + 0.15))
t = T["wide"][1]
START[1] = t + 0.05; T["deniz"] = (t, START[1] + DUR[1] + 0.1); t = T["deniz"][1]
START[2] = t + 0.1; T["deniz_tepki"] = (t, START[2] + DUR[2] + 0.15); t = T["deniz_tepki"][1]
START[3] = t + 0.1; T["bakalim"] = (t, START[3] + DUR[3] + 0.6); t = T["bakalim"][1]
T["loupe_in"] = T["bakalim"][1] - 0.6
TICKET_T = tuple(round(t + 0.1 + 0.45 * i, 2) for i in range(3))
START[4] = t + 1.7; T["biletler"] = (t, START[4] + DUR[4] + 0.6); t = T["biletler"][1]
START[5] = t + 0.4; T["olcelim"] = (t, START[5] + DUR[5] + 0.3); t = T["olcelim"][1]
T["metre"] = (t, t + 2.8); t = T["metre"][1]
START[6] = t + 0.1
T["harita"] = (t, START[6] + SEG07["sifir"][0] - 0.1); t = T["harita"][1]
T["kalp"] = (t, START[6] + SEG07["yol"][0] - 0.05); t = T["kalp"][1]
T["yol"] = (t, START[6] + DUR[6] + 0.25); t = T["yol"][1]
START[7] = t + 0.15; T["yolda"] = (t, START[7] + DUR[7] + 0.5); t = T["yolda"][1]
T_TICKET = t; T_CTA = t + 4.0; T_END = T_CTA + 2.4
START[8] = T_END + 0.2; START[9] = START[8] + DUR[8] + 0.15
TOTAL = round(START[9] + DUR[9] + 0.4, 2)
FIELDS = (("Arıza:", "İstanbul–İzmir, 480 km."),
          ("Yapılan işlem:", "Ölçüldü. Kalpte 0 cm."),
          ("Not:", "Yol uzunsa, sevgi kısa değil."))
S5 = START[4]
S7 = START[6]


def notes_at(t):
    out = []
    for i, parts in enumerate(NOTE_PARTS):
        lines = ib.TICKETS[i][1]
        n = 0
        for (a, b), line in zip(parts, lines):
            a += S5; b += S5
            n += len(line) if t >= b else (0 if t < a else int(len(line) * (t - a) / (b - a)))
        out.append(n)
    return tuple(out)


def note_focus(t):
    """Which ticket the camera looks at while its note is read (None before reading)."""
    if t < S5 - 0.3:
        return None
    for i in (2, 1, 0):
        if t >= S5 + NOTE_PARTS[i][0][0] - 0.35:
            return i
    return 0


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["E"] = []
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
    return shop(t, push(WIDE, t, 0, T["wide"][1], 0.04), deniz="D_phone", rope="tickets" if t >= 1.1 else "none",
                emre_back=(120 - 220 * (1 - smooth(min(1.0, t / 1.0))), 560, 0.95, 5, "A_back", 0.85))


def shot_bakalim(t):
    t0, t1 = T["bakalim"]
    p = loupe_in(t, T["loupe_in"])
    cam = push(USTA_CU, t, t0, t1, 0.06)
    if p is None:
        return shop(t, cam, usta="E_front", rope="tickets", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="tickets", bg_blur=9, deniz_blur=8, usta_blinks=False)


def shot_tickets(t):
    n = sum(1 for tt in TICKET_T if t >= tt)
    img = ib.tickets_plate(n, notes_at(t))
    # camera: overview while tickets fall, then glide to the ticket being read
    t0 = T["biletler"][0]
    over = (720, 1280, 1.06)
    tgt = over
    f = note_focus(t)
    if f is not None:
        x, y, _ = ib.SPOTS[f]
        tgt = (x, y + 60, 1.45)
    # smooth glide: blend from the previous target over 0.45 s
    prev = over
    tf = t0
    if f is not None:
        tf = S5 + NOTE_PARTS[f][0][0] - 0.35
        if f > 0:
            px, py, _ = ib.SPOTS[f - 1]; prev = (px, py + 60, 1.45)
    k = smooth(min(1.0, max(0.0, (t - tf) / 0.45)))
    cx = prev[0] + (tgt[0] - prev[0]) * k; cy = prev[1] + (tgt[1] - prev[1]) * k; z = prev[2] + (tgt[2] - prev[2]) * k
    cw, chh = 1440 / z, 2560 / z
    x0 = min(max(cx - cw / 2, 0), 1440 - cw); y0 = min(max(cy - chh / 2, 0), 2560 - chh)
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + chh))).resize((W, H), Image.LANCZOS)


def shot_olcelim(t):
    t0, t1 = T["olcelim"]
    p = loupe_out(t, t0 + 0.05)
    cam = push(USTA_CU, t, t0, t1, 0.04)
    if p is None:
        return shop(t, cam, usta="E_serious", rope="tickets", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, usta_mouth=0, rope="tickets", bg_blur=9, deniz_blur=8)


def shot_tape(t):
    t0 = T["metre"][0]
    k = smooth(k01(t, t0 + 0.15, t0 + 1.4))
    return ib.tickets_plate(3, (99, 99, 99), round(k, 2), ib.km_counter(round(k * 20) / 20))


HEART = (0.575, 0.615)     # customer's heart in the door MCU frame (fraction of W, H)


def shot_kalp(t):
    """Usta's tape measure reaches the customer's heart; the counter rolls from 480 km to 0 cm."""
    t0, t1 = T["kalp"]
    img = door(t, push(EMRE_MCU, t, t0, t1, 0.05), emre="A_soft", rope="tickets", emre_mouth=0.0).convert("RGBA")
    reach = smooth(k01(t, t0, t0 + 0.4))
    k = smooth(k01(t, t0 + 0.35, t0 + 0.8))
    counter = "0 cm" if k >= 1 else ib.km_counter(1 - k)
    return ib.tape_to_point(img, (W * 0.83, H * 0.86), (W * HEART[0], H * HEART[1]), reach, counter, k)


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
    S(*T["wide"], shot_open),
    S(*T["deniz"], lambda t: shop(t, push(DENIZ_MCU, t, *T["deniz"]), deniz="D_sincere", rope="tickets", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(*T["deniz_tepki"], lambda t: shop(t, push(USTA_MCU, t, *T["deniz_tepki"]), usta="E_side", deniz="D_sincere", rope="tickets", bg_blur=8, deniz_blur=6)),
    S(*T["bakalim"], shot_bakalim),
    S(*T["biletler"], shot_tickets),
    S(*T["olcelim"], shot_olcelim),
    S(*T["metre"], plate(shot_tape, *T["metre"], 1.0, 1.04, 0.5, 0.5)),
    S(*T["harita"], lambda t: shop(t, push(USTA_CU, t, *T["harita"], 0.06), usta="E_soft", rope="tickets", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(*T["kalp"], shot_kalp),
    S(*T["yol"], lambda t: shop(t, push(USTA_CU, t, *T["yol"], 0.08), usta="E_soft", rope="tickets", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(*T["yolda"], lambda t: door(t, push(EMRE_CU, t, *T["yolda"], 0.05), emre="A_soft", rope="tickets")),
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
        img = subtitle(img, sub_at(t), 0.62 if t < T["wide"][1] else 0.705)
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
    add(f"{SFX}/loupe.mp3", T["loupe_in"], 0.5)
    for tt in TICKET_T:
        add(f"{SFX}/kagit_birakma.mp3", tt - 0.05, 0.7)
    for parts in NOTE_PARTS:
        for (a, b) in parts:
            add(f"{SFX}/kalem.mp3", S5 + a, 0.3, f",atrim=0:{b - a:.2f},afade=t=out:st={max(0, b - a - 0.2):.2f}:d=0.2")
    add(f"{SFX}/serit_metre.mp3", T["metre"][0] + 0.1, 0.85)
    add(f"{SFX}/serit_geri.mp3", T["kalp"][0] + 0.3, 0.85)
    add(f"{SFX}/kalem.mp3", T_TICKET + 0.2, 0.7, ",atrim=0:2.5,afade=t=out:st=2.1:d=0.4")
    add(f"{SFX}/damga.mp3", T_CTA - 0.75, 0.8)
    add(f"{SFX}/muzik.mp3", T["biletler"][0], 0.24, f",afade=t=in:st=0:d=2.5,afade=t=out:st={T_END - T['biletler'][0] - 1.5}:d=1.5")
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
