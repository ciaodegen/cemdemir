"""Eşref Usta'ya Mektup 1 — "Hâlâ Özlüyorum" (~45 sn)."""
import sys, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
from PIL import Image
from engine import W, H, FPS, ROOT, finish, subtitle, envelope, duration, smooth
import scenes3d as s3
from scenes3d import shop, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, loupe_in, loupe_out
from scenes import split_sub, plate
import inserts as ins
import inserts_m1 as im

REP = f"{ROOT}/mektup1/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker, subtitle (None = text already on paper)
    ("01_D", "D", "Usta, mektup gelmiş! Bu devirde mektup mu yazılır ya?"),
    ("02_U", "U", "Deniz."),
    ("03_U", "U", "Dur, bir bakalım…"),
    ("04_U", "U", None),
    ("05_U", "U", None),
    ("06_U", "U", "Özlemek arıza değil evlat. Dokuz yıl kolay sökülmez."),
    ("07_U", "U", None),
    ("08_U", "U", None),
    ("09_U", "U", "O özlemi geçmişe değil, ona harca."),
]
START = {0: 3.45, 1: 7.1, 2: 8.4, 3: 11.1, 4: 16.9, 5: 21.3, 6: 26.5, 7: 31.0, 8: 34.6}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
TOTAL = 45.2
T_TICKET, T_CTA = 38.8, 42.8
FIELDS = (("Arıza:", "Bitmiş bir evliliği hâlâ özlemek."),
          ("Yapılan işlem:", "Sökülmedi. Yeri değiştirildi."),
          ("Not:", "Evlilik biter. Anne babalık bitmez."))

# handwriting reveal: (line index, start, end) in absolute seconds, synced to the voice
S4, S5, S7, S8 = START[3], START[4], START[6], START[7]
LETTER_SEG = [(0, S4, S4 + 0.96), (1, S4 + 1.71, S4 + 2.85), (2, S4 + 2.85, S4 + 3.89), (3, S4 + 4.52, S4 + 5.43),
              (4, S5, S5 + 1.18), (5, S5 + 1.67, S5 + 2.61), (6, S5 + 2.6, S5 + 2.85)]
REPLY_SEG = [(0, 0, 0.01), (1, 0, 0.01), (2, S7, S7 + 2.6), (3, S7 + 3.08, S7 + 4.15),
             (4, S8, S8 + 1.18), (5, S8 + 1.94, S8 + 3.19)]


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
s3.BLINKS["U"] = [2.8, 21.0, 24.6, 37.2]
s3.BLINKS["D"] = [2.6, 5.9, 20.5]


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
    return ins.ticket(progress, stamp, "M-01", FIELDS, "CEVAP YAZILDI")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Ayrılsa da çocuğu için", "güçlü kalan birine gönder."), "Arızanı yaz, Eşref Usta okusun · Mektup 1")


def S(t0, t1, fn):
    return (t0, t1, fn)


def k01(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def shot_bakalim(t):
    p = loupe_in(t, 10.25)
    cam = push(USTA_CU, t, 8.3, 10.9, 0.06)
    if p is None:
        return shop(t, cam, usta="E_front", rope="envelope", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="envelope", bg_blur=9, deniz_blur=8, usta_blinks=False)


def shot_cevap(t):
    p = loupe_out(t, 20.95)
    cam = push(USTA_CU, t, 20.9, 26.4, 0.1)
    if p is None:
        return shop(t, cam, usta="E_soft", rope="envelope", bg_blur=9, deniz_blur=8, usta_blinks=False)
    return shop(t, cam, usta=p, usta_mouth=0, rope="envelope", bg_blur=9, deniz_blur=8)


IN_PLATE = []  # time ranges with paper text on screen (no subtitles)

SHOTS = [
    S(0.0, 2.2, plate(lambda t: im.envelope_plate(int(round(smooth(k01(t, 0.1, 0.8)) * 20))), 0.0, 2.2, 1.12, 1.2)),
    S(2.2, 3.4, lambda t: shop(t, push(WIDE, t, 2.2, 3.4, 0.03), deniz="D_phone", rope="envelope")),
    S(3.4, 7.0, lambda t: shop(t, push(DENIZ_MCU, t, 3.4, 7.0), deniz="D_phone", rope="envelope", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(7.0, 8.3, lambda t: shop(t, push(USTA_MCU, t, 7.0, 8.3), usta="E_side", deniz="D_phone", rope="envelope", bg_blur=8, deniz_blur=6)),
    S(8.3, 10.9, shot_bakalim),
    S(10.9, 19.9, plate(lambda t: im.letter_plate(reveal(t, LETTER_SEG, im.LETTER)), 10.9, 19.9, 1.22, 1.28, 0.45, 0.02)),
    S(19.9, 20.9, lambda t: shop(t, push(DENIZ_MCU, t, 19.9, 20.9, 0.03), deniz="D_sincere", rope="envelope", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(20.9, 26.4, shot_cevap),
    S(26.4, 34.5, plate(lambda t: im.reply_plate(reveal(t, REPLY_SEG, im.REPLY), t < S8 + 3.25), 26.4, 34.5, 1.22, 1.28, 0.45, 0.02)),
    S(34.5, T_TICKET, lambda t: shop(t, push(USTA_MCU, t, 34.5, T_TICKET, 0.08), usta="E_soft", rope="envelope", bg_blur=8, deniz_blur=6, usta_blinks=False)),
    S(T_TICKET, T_CTA, plate(lambda t: _ticket(round(k01(t, T_TICKET + 0.2, T_TICKET + 2.9) * 60) / 60, round(k01(t, T_CTA - 0.75, T_CTA - 0.4) * 8) / 8), T_TICKET, T_CTA, 1.04, 1.0)),
    S(T_CTA, TOTAL, plate(lambda t: _cta(), T_CTA, TOTAL, 1.0, 1.0)),
]


def frame_at(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            img = fn(t)
            break
    else:
        img = Image.new("RGB", (W, H))
    img = finish(img, t, dust=False, grain=False)
    if t < T_TICKET:
        img = subtitle(img, sub_at(t))
    if t > TOTAL - 0.6:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.6: int(v * max(k, 0)))
    if T_CTA - 0.3 <= t < T_CTA + 0.3:
        k = abs(t - T_CTA) / 0.3
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
    add(f"{SFX}/ortam.mp3", 0.0, 0.32, f",aloop=loop=4:size=2e6,atrim=0:{TOTAL},afade=t=out:st={TOTAL - 4}:d=3")
    add(f"{SFX}/zarf_kayma.mp3", 0.05, 0.8)
    add(f"{SFX}/loupe.mp3", 10.25, 0.5)
    add(f"{SFX}/kagit_acma.mp3", 10.85, 0.7)
    for (i, a, b) in REPLY_SEG[2:]:
        add(f"{SFX}/kalem.mp3", a, 0.45, f",atrim=0:{b - a:.2f},afade=t=out:st={max(0, b - a - 0.2):.2f}:d=0.2")
    add(f"{SFX}/kalem.mp3", T_TICKET + 0.2, 0.7, ",atrim=0:2.7,afade=t=out:st=2.3:d=0.4")
    add(f"{SFX}/damga.mp3", T_CTA - 0.75, 0.8)
    add(f"{SFX}/muzik.mp3", 10.9, 0.24, f",afade=t=in:st=0:d=3.0,afade=t=out:st={TOTAL - 10.9 - 3.0}:d=3.0")
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
