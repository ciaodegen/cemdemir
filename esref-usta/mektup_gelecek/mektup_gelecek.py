"""Eşref Usta'ya Mektup 1 — "Gelecek Kaygısı" (~46 sn, sonda yorum çağrısı)."""
import sys, subprocess, functools, math
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup_gelecek")
from PIL import Image, ImageDraw
from engine import W, H, UI, FPS, ROOT, finish, subtitle, envelope, duration, smooth, font, FONT_BOLD, FONT_SERIF_B
import scenes3d as s3
from scenes3d import shop, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, loupe_in, loupe_out
from scenes import split_sub, plate
import inserts as ins
import inserts_m1 as im
import saat

REP = f"{ROOT}/mektup_gelecek/replikler_hizli"
SFX = f"{ROOT}/efektler"
ARIZA = "Gelecek kaygısı."

LINES = [  # file, speaker, subtitle (None = text on paper)
    ("01_D", "D", "Usta, mektup gelmiş! Gelecek kaygısıymış… Burcuna baksın, geçer!"),
    ("02_U", "U", "Deniz."),
    ("03_U", "U", "Dur, bir bakalım…"),
    ("04_U", "U", None),
    ("05_U", "U", "Duyuyor musun? Bu saat hep ileri koşuyor."),
    ("06_U", "U", "Gelecek kaygısı arıza değil evlat. Ayar bozukluğu. Saatin hep ileride."),
    ("07_U", "U", "Yarını bugünden tamir edemezsin."),
    ("08_U", "U", None),
    ("09_U", "U", "Senin de bir arızan mı var? Yorumlara yaz. En çok beğenileni, bir sonraki mektupta tamir edeceğim."),
]
START = {0: 3.45, 1: 8.2, 2: 9.5, 3: 12.2, 4: 15.9, 5: 19.9, 6: 25.8, 7: 29.0, 8: 39.2}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
T_TICKET, T_CTA, T_END = 32.6, 36.6, 39.0
TOTAL = 46.4
FIELDS = (("Arıza:", "Gelecek kaygısı."),
          ("Yapılan işlem:", "Saat bugüne ayarlandı."),
          ("Not:", "Bugünü sağlam yap, yarın ona yaslanır."))

LETTER = (("Eşref Usta,", 0), ("Ne olacak bu", 1), ("gelecek kaygısı?", 1), ("— Bir takipçin", 2))
REPLY = (("Gelecek kaygısı arıza değil,", 0), ("ayar bozukluğu.", 0), ("Yarını bugünden", 0),
         ("tamir edemezsin.", 0), ("Bugünü sağlam yap,", 1), ("yarın ona yaslanır.", 2))
S4, S8 = START[3], START[7]
LETTER_SEG = [(0, S4, S4 + 1.0), (1, S4 + 1.72, S4 + 2.5), (2, S4 + 2.5, S4 + 3.32), (3, S4 + 3.35, S4 + 3.6)]
REPLY_SEG = [(0, 0, .01), (1, 0, .01), (2, 0, .01), (3, 0, .01), (4, S8, S8 + 1.52), (5, S8 + 1.81, S8 + 3.4)]


def reveal(t, segs, lines):
    out = []
    for (i, a, b) in segs:
        n = len(lines[i][0])
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
s3.BLINKS["U"] = [2.8, 21.2, 24.0, 41.6, 44.6]
s3.BLINKS["D"] = [2.6, 6.4]


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
    return ins.ticket(progress, stamp, "M-01", FIELDS, "AYARLANDI")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Geleceği düşünmekten", "bugünü kaçıran birine gönder."), "Eşref Usta'ya Mektup · 1")


def S(t0, t1, fn):
    return (t0, t1, fn)


def k01(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


# --- clock -------------------------------------------------------------------
NOW_MIN = 10 * 60 + 11          # 10:11 "bugün"


def clock_state_run(t):
    """15.6..19.6: normal tick, then the hands race into the future."""
    t0, ta = 15.6, 16.8
    sec = int((t - t0)) * 6
    if t < ta:
        mins = NOW_MIN
        spin = 0.0
    else:
        u = t - ta
        mins = NOW_MIN + 40 * u ** 2.6 * 6
        spin = min(1.0, u / 1.2)
        sec = (t - t0) * 360 * (0.5 + u)
    year = 2026 + int((mins - NOW_MIN) / 60 / 2)
    return mins, sec, str(year), spin


def clock_state_back(t):
    """25.6..28.8: hands rewind and settle on today."""
    ta, tb = 25.6, 27.3
    if t < tb:
        k = smooth(k01(t, ta, tb))
        start = NOW_MIN + 2400
        mins = start + (NOW_MIN - start) * k
        spin = -1.0 * (1 - k) if k < 0.9 else 0.0
        sec = -(t - ta) * 900 * (1 - k)
        year = str(2026 + int((mins - NOW_MIN) / 60 / 2)) if k < 0.97 else "BUGÜN"
    else:
        mins = NOW_MIN; spin = 0.0; sec = int(t - tb) * 6; year = "BUGÜN"
    return mins, sec, year, spin


def clock_frame(state):
    mins, sec, year, spin = state
    md = (mins % 60) * 6
    hd = (mins / 60 % 12) * 30
    return saat.clock(round(md, 1), round(hd, 1), round(sec % 360, 1), year, abs(spin) if spin >= 0 else 0.0) if spin >= 0 else \
        saat.clock(round(md, 1), round(hd, 1), round(sec % 360, 1), year, 0.0)


# --- shots ---------------------------------------------------------------------
def shot_bakalim(t):
    p = loupe_in(t, 11.35)
    cam = push(USTA_CU, t, 9.4, 12.0, 0.06)
    if p is None:
        return shop(t, cam, usta="E_front", rope="envelope", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="envelope", bg_blur=9, deniz_blur=8, usta_blinks=False)


def shot_cevap(t):
    p = loupe_out(t, 19.65)
    cam = push(USTA_CU, t, 19.6, 25.6, 0.1)
    if p is None:
        return shop(t, cam, usta="E_soft", rope="envelope", bg_blur=9, deniz_blur=8, usta_blinks=False)
    return shop(t, cam, usta=p, usta_mouth=0, rope="envelope", bg_blur=9, deniz_blur=8)


@functools.lru_cache(None)
def _tag():
    """'Arızanı yorumlara yaz' paper tag for the final call to action."""
    w, h = int(940 * UI / 1.5), int(230 * UI / 1.5)
    tag = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(tag)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=int(24 * UI / 1.5), fill=(246, 234, 205, 240), outline=(176, 36, 36, 255), width=int(6 * UI / 1.5))
    f1 = font(FONT_SERIF_B, int(56 * UI / 1.5)); f2 = font(FONT_SERIF_B, int(36 * UI / 1.5))
    for txt, f, y, c in (("ARIZANI YORUMLARA YAZ", f1, 0.17, (40, 26, 16, 255)), ("En çok beğenilen tamir edilecek", f2, 0.6, (150, 30, 30, 255))):
        tw = d.textlength(txt, font=f); d.text(((w - tw) / 2, h * y), txt, font=f, fill=c)
    return tag.rotate(-2, expand=True, resample=Image.BICUBIC)


def shot_end(t):
    img = shop(t, push((650, 1400, 820), t, T_END, TOTAL, 0.05), usta="E_front", rope="none", bg_blur=8, deniz_blur=6)
    k = smooth(k01(t, T_END + 0.3, T_END + 0.8))
    if k > 0:
        tg = _tag().copy()
        if k < 1:
            tg.putalpha(tg.split()[3].point(lambda v: int(v * k)))
        img.alpha_composite(tg, ((W - tg.size[0]) // 2, int(H * 0.115 - 40 * (1 - k) * UI)))
    return img


LP = tuple(LETTER); RP = tuple(REPLY)
SHOTS = [
    S(0.0, 2.2, plate(lambda t: im.envelope_plate(int(round(smooth(k01(t, 0.1, 0.8)) * 20)), ARIZA), 0.0, 2.2, 1.12, 1.2)),
    S(2.2, 3.4, lambda t: shop(t, push(WIDE, t, 2.2, 3.4, 0.03), deniz="D_phone", rope="envelope")),
    S(3.4, 8.1, lambda t: shop(t, push(DENIZ_MCU, t, 3.4, 8.1), deniz="D_phone", rope="envelope", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(8.1, 9.4, lambda t: shop(t, push(USTA_MCU, t, 8.1, 9.4), usta="E_side", deniz="D_phone", rope="envelope", bg_blur=8, deniz_blur=6)),
    S(9.4, 12.0, shot_bakalim),
    S(12.0, 15.6, plate(lambda t: im.letter_plate(reveal(t, LETTER_SEG, LP), LP), 12.0, 15.6, 1.3, 1.38, 0.4, 0.02)),
    S(15.6, 19.6, plate(lambda t: clock_frame(clock_state_run(t)), 15.6, 19.6, 1.12, 1.24)),
    S(19.6, 25.6, shot_cevap),
    S(25.6, 28.8, plate(lambda t: clock_frame(clock_state_back(t)), 25.6, 28.8, 1.24, 1.14)),
    S(28.8, T_TICKET, plate(lambda t: im.reply_plate(reveal(t, REPLY_SEG, RP), t < S8 + 3.45, RP), 28.8, T_TICKET, 1.22, 1.28, 0.45, 0.02)),
    S(T_TICKET, T_CTA, plate(lambda t: _ticket(round(k01(t, T_TICKET + 0.2, T_TICKET + 2.9) * 60) / 60, round(k01(t, T_CTA - 0.75, T_CTA - 0.4) * 8) / 8), T_TICKET, T_CTA, 1.04, 1.0)),
    S(T_CTA, T_END, plate(lambda t: _cta(), T_CTA, T_END, 1.0, 1.0)),
    S(T_END, TOTAL, shot_end),
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
        img = subtitle(img, sub_at(t))
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
    for i, (f, _, _) in enumerate(LINES):
        add(f"{REP}/{f}.mp3", START[i], 1.0)
    add(f"{SFX}/ortam.mp3", 0.0, 0.32, f",aloop=loop=4:size=2e6,atrim=0:{TOTAL},afade=t=out:st={TOTAL - 3}:d=2.5")
    add(f"{SFX}/zarf_kayma.mp3", 0.05, 0.8)
    add(f"{SFX}/loupe.mp3", 11.35, 0.5)
    add(f"{SFX}/kagit_acma.mp3", 11.95, 0.7)
    add(f"{SFX}/saat_normal.mp3", 15.6, 0.8, ",atrim=0:1.4,afade=t=out:st=1.1:d=0.3")
    add(f"{SFX}/saat_hizli.mp3", 16.8, 0.8, ",afade=t=out:st=2.4:d=0.4")
    add(f"{SFX}/saat_hizli.mp3", 25.6, 0.55, ",areverse,atrim=0:1.7,afade=t=out:st=1.3:d=0.4")
    add(f"{SFX}/saat_normal.mp3", 27.3, 0.8, ",atrim=0:1.5,afade=t=out:st=1.1:d=0.4")
    for (i, a, b) in REPLY_SEG[4:]:
        add(f"{SFX}/kalem.mp3", a, 0.45, f",atrim=0:{b - a:.2f},afade=t=out:st={max(0, b - a - 0.2):.2f}:d=0.2")
    add(f"{SFX}/kalem.mp3", T_TICKET + 0.2, 0.7, ",atrim=0:2.7,afade=t=out:st=2.3:d=0.4")
    add(f"{SFX}/damga.mp3", T_CTA - 0.75, 0.8)
    add(f"{SFX}/muzik.mp3", 12.0, 0.24, f",afade=t=in:st=0:d=3.0,afade=t=out:st={TOTAL - 12.0 - 2.5}:d=2.5")
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
