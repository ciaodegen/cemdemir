"""Bölüm 3 — "Susan Kedi" (~46 sn)."""
import sys, math, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum3k")
from PIL import Image
from engine import W, H, FPS, ROOT, finish, subtitle, envelope, duration, smooth
import scenes3d as s3
from scenes3d import (shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU,
                      USTA_BACK_OTS, loupe_in)
from scenes import split_sub, plate
import inserts as ins
import inserts6 as ins6

REP = f"{ROOT}/bolum3k/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = Ela, O = operator), subtitle
    ("01_E", "E", "Usta, bu kedi hiç miyavlamıyor. Bozuk mu?"),
    ("02_D", "D", "Abla bir yaş mama verin, düzelir bence."),
    ("03_U", "U", "Deniz."),
    ("04_E", "E", "Sokakta buldum. Bir haftadır yanımda, bir kere bile ses çıkarmadı."),
    ("10_U", "U", "Dur, bir bakalım…"),
    ("05_U", "U", "Bu kedi sokak kedisi değil kızım. Ev kedisi."),
    ("06_O", "O", "Aradığınız numara kullanılmamaktadır."),
    ("07_U", "U", "Kediler birbirine miyavlamaz. Sadece insana miyavlar."),
    ("08_U", "U", "Bu kedi miyavlamayı unutmamış… Cevap veren olmayınca susmuş."),
    ("09_E", "E", "Pamuk?"),
]
START = {0: 0.5, 1: 4.1, 2: 6.15, 3: 7.9, 4: 12.65, 5: 15.9, 6: 21.0, 7: 23.3, 8: 27.9, 9: 33.1}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
TOTAL = 46.2
FIELDS = (("Arıza:", "Miyavlamıyor."),
          ("Sebep:", "Cevap veren yok."),
          ("Yapılan işlem:", "Adı söylendi."),
          ("Not:", "Hayvanlar susmaz. Susturulur."))


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["E"] = [9.6, 11.8, 34.2, 37.9]
s3.BLINKS["C"] = [2.6, 6.8, 10.5, 17.6, 25.2, 29.4, 36.4, 40.0]
s3.BLINKS["U"] = [2.2, 9.6, 17.4, 21.6]


def sub_at(t):
    for i, (f, s, txt) in enumerate(LINES):
        if START[i] - 0.05 <= t < START[i] + DUR[i] + 0.2:
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


def tick(t):
    return int(t * 2)


@functools.lru_cache(None)
def _ticket(progress, stamp):
    return ins.ticket(progress, stamp, "003", FIELDS, "SAHİPLENİLDİ")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Bir sokak dostunu", "sahiplenen birine gönder."), "Eşref Usta · Bölüm 3")


def S(t0, t1, fn):
    return (t0, t1, fn)


CAT_CU = (s3.CAT_X, 1810, 520)


def shotE(t):  # loupe goes on, looking at the cat
    p = loupe_in(t, 12.7)
    cam = push(USTA_CU, t, 12.6, 14.0, 0.05)
    if p is None:
        return shop(t, cam, usta="E_read", rope="none", cat="C_idle", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="none", cat="C_idle", bg_blur=9, deniz_blur=8, usta_blinks=False)


def meow_level(t):
    import math
    k = (t - 35.0) / 0.6
    return max(0.0, math.sin(math.pi * k)) if 0 <= k <= 1 else 0.0


SHOTS = [
    S(0.0, 4.0, lambda t: shop(t, push(WIDE, t, 0, 4.0, 0.04), deniz="D_phone", rope="none", cat="C_idle",
                               cat_dx=-300 * (1 - smooth((t - 0.6) / 0.9)), cat_dy=430 * (1 - smooth((t - 0.6) / 0.9)) - 60 * math.sin(math.pi * min(1, max(0, (t - 0.6) / 0.9))),
                               emre_back=(120 - 220 * (1 - smooth(t / 1.0)), 560, 0.95, 5, "L_back"))),
    S(4.0, 6.1, lambda t: shop(t, push(DENIZ_MCU, t, 4.0, 6.1), deniz="D_phone", rope="none", cat="C_idle", deniz_blur=0, bg_blur=8, usta_blur=6, cat_blur=4)),
    S(6.1, 7.8, lambda t: shop(t, push(USTA_MCU, t, 6.1, 7.8), usta="E_side", deniz="D_phone", rope="none", cat="C_idle", bg_blur=8, deniz_blur=6)),
    S(7.8, 12.6, lambda t: door(t, push(EMRE_MCU, t, 7.8, 12.6, 0.1), emre="L_worried", rope="none", usta_back=USTA_BACK_OTS)),
    S(12.6, 14.0, shotE),
    S(14.0, 15.8, plate(lambda t: ins6.loupe_tag(), 14.0, 15.8, 1.0, 1.06)),
    S(15.8, 19.7, lambda t: shop(t, push(USTA_MCU, t, 15.8, 19.7, 0.05), usta="E_serious", rope="none", cat="C_sad", bg_blur=8, deniz_blur=6)),
    S(19.7, 20.9, plate(lambda t: ins6.deniz_dials(), 19.7, 20.9, 1.0, 1.04)),
    S(20.9, 23.2, lambda t: shop(t, push(DENIZ_MCU, t, 20.9, 23.2, 0.04), deniz="D_listen", rope="none", cat="C_sad", deniz_blur=0, bg_blur=8, usta_blur=6, cat_blur=4)),
    S(23.2, 27.8, lambda t: shop(t, push(USTA_CU, t, 23.2, 27.8, 0.06), usta="E_soft", rope="none", cat="C_sad", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(27.8, 30.6, lambda t: shop(t, push(USTA_CU, t, 27.8, 30.6, 0.06), usta="E_soft", rope="none", cat="C_sad", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(30.6, 33.0, lambda t: shop(t, push(CAT_CU, t, 30.6, 33.0, 0.08), usta="E_soft", rope="none", cat="C_sad", bg_blur=10, deniz_blur=10, usta_blur=7, usta_blinks=False)),
    S(33.0, 34.6, lambda t: door(t, push(EMRE_CU, t, 33.0, 34.6, 0.04), emre="L_tender", rope="none")),
    S(34.6, 37.0, lambda t: shop(t, push(CAT_CU, t, 34.6, 37.0, 0.1), usta="E_soft", rope="none", cat="C_meow", cat_mouth=meow_level(t), bg_blur=10, deniz_blur=10, usta_blur=7, usta_blinks=False)),
    S(37.0, 38.6, lambda t: door(t, push(EMRE_CU, t, 37.0, 38.6, 0.05), emre="L_smile", rope="none", emre_mouth=0.0)),
    S(38.6, 43.4, plate(lambda t: _ticket(round(min(1, max(0, (t - 38.8) / 3.0)) * 60) / 60, round(min(1, max(0, (t - 42.6) / 0.35)) * 8) / 8), 38.6, 43.4, 1.04, 1.0)),
    S(43.4, 46.2, plate(lambda t: _cta(), 43.4, 46.2, 1.0, 1.0)),
]


def frame_at(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            img = fn(t)
            break
    else:
        img = Image.new("RGB", (W, H))
    img = finish(img, t, dust=False, grain=False)
    if t < 38.6:
        img = subtitle(img, sub_at(t))
    if t > TOTAL - 0.6:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.6: int(v * max(k, 0)))
    if 43.1 <= t < 43.7:
        k = abs(t - 43.4) / 0.3
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
    add(f"{SFX}/cingirak.mp3", 0.0, 0.6)
    add(f"{SFX}/loupe.mp3", 12.95, 0.6)
    add(f"{SFX}/ip.mp3", 1.35, 0.5)
    add(f"{SFX}/telefon.mp3", 19.8, 0.4, ",atrim=0:1.2")
    add(f"{SFX}/miyav_ilk.mp3", 35.0, 1.0)
    add(f"{SFX}/kedi_mirlama.mp3", 35.9, 0.5, ",afade=t=out:st=2.2:d=0.8")
    add(f"{SFX}/cingirak_cikis.mp3", 38.0, 0.45)
    add(f"{SFX}/kalem.mp3", 38.8, 0.7, ",atrim=0:3.0,afade=t=out:st=2.6:d=0.4")
    add(f"{SFX}/damga.mp3", 42.6, 0.8)
    add(f"{SFX}/muzik.mp3", 23.2, 0.28, f",afade=t=in:st=0:d=2.5,afade=t=out:st={TOTAL - 23.2 - 3.0}:d=3.0")
    fc = ";".join(filters) + ";" + "".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{TOTAL},alimiter=limit=0.95[out]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-c:a", "pcm_s16le", out], check=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        for tt in sys.argv[3:]:
            frame_at(float(tt)).save(f"{sys.argv[2]}/still_{float(tt):05.1f}.jpg", quality=88)
    elif mode == "video":
        out, a, b = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for n in range(int(round(a * FPS)), int(round(b * FPS))):
            p.stdin.write(frame_at(n / FPS).convert("RGB").tobytes())
        p.stdin.close(); p.wait()
    elif mode == "audio":
        audio_mix(sys.argv[2])
