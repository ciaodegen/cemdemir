"""Bölüm 3 — "Söküm" (~53 sn)."""
import sys, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum3")
from PIL import Image
from engine import W, H, FPS, ROOT, finish, subtitle, envelope, duration, smooth
import scenes3d as s3
from scenes3d import (shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU,
                      USTA_BACK_OTS, loupe_in)
from scenes import split_sub, plate
import inserts as ins
import inserts4 as ins4

REP = f"{ROOT}/bolum3/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = Zeynep), subtitle
    ("01_Z", "E", "Usta, eski sevgilimi kalbimden sökebilir misiniz?"),
    ("02_D", "D", "Abla iki dakikalık iş. Söker atarız."),
    ("03_U", "U", "Deniz."),
    ("04_U", "U", "Ne zaman ayrıldınız?"),
    ("05_Z", "E", "İki yıl oldu."),
    ("06_U", "U", "Hâlâ dönüyor bu."),
    ("07_Z", "E", "Biliyorum. O yüzden geldim. Her gece aynı yerde takılıyor."),
    ("08_U", "U", "Bakalım arkasında ne yazıyor."),
    ("09_U", "U", "Bu çark o değil kızım. Bu, onunla olan sen."),
    ("10_U", "U", "Sen onu değil… o zamanki kendini özlüyorsun."),
    ("11_Z", "E", "…O zamanlar çok gülüyordum."),
    ("12_U", "U", "Sökmeyelim. Yanına yenisini takalım. Üstüne ne yazacağına sen karar ver."),
]
START = {0: 0.25, 1: 3.9, 2: 5.9, 3: 7.6, 4: 10.1, 5: 11.5, 6: 13.1, 7: 17.9, 8: 23.5, 9: 28.3,
         10: 32.6, 11: 34.5}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
TOTAL = 53.0
FIELDS = (("Arıza:", "Eski parça hâlâ dönüyor."),
          ("Yapılan işlem:", "Söküm yapılmadı. Yeni parça eklendi."),
          ("Not:", "Bazen insan birini değil, onunla olan kendini özler."))


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["E"] = [9.0, 12.4, 16.2, 22.5, 26.1, 30.8, 33.3, 38.9, 42.6]


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
    return ins.ticket(progress, stamp, "003", FIELDS, "SÖKÜLMEDİ")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Eskisini özlediğini sanan", "arkadaşına gönder."), "Eşref Usta · Bölüm 3")


def S(t0, t1, fn):
    return (t0, t1, fn)


def shotD(t):  # loupe goes on
    p = loupe_in(t, 7.3)
    cam = push(USTA_CU, t, 7.2, 10.0, 0.06)
    if p is None:
        return shop(t, cam, usta="E_front", rope="heart", bg_blur=9, deniz_blur=8)
    if p == "E_loupe":
        return shop(t, cam, usta="E_loupe", rope="heart", bg_blur=9, deniz_blur=8, usta_blinks=False)
    return shop(t, cam, usta=p, rope="heart", bg_blur=9, deniz_blur=8, usta_blinks=False)


def flip_f(t):
    return round(min(1, max(0, (t - 21.3) / 0.7)) * 14) / 14


SHOTS = [
    S(0.0, 3.8, plate(lambda t: ins4.heart(tick(t)), 0.0, 3.8, 1.0, 1.12)),
    S(3.8, 5.8, lambda t: shop(t, push(DENIZ_MCU, t, 3.8, 5.8), deniz="D_phone", rope="heart", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(5.8, 7.2, lambda t: shop(t, push(USTA_MCU, t, 5.8, 7.2), usta="E_side", deniz="D_phone", rope="heart", bg_blur=8, deniz_blur=6)),
    S(7.2, 10.0, shotD),
    S(10.0, 11.4, lambda t: door(t, push(EMRE_CU, t, 10.0, 11.4, 0.03), emre="Z_sad", rope="heart")),
    S(11.4, 13.0, plate(lambda t: ins4.loupe_gear(tick(t)), 11.4, 13.0, 1.0, 1.05)),
    S(13.0, 17.8, lambda t: door(t, push(EMRE_MCU, t, 13.0, 17.8, 0.1), emre="Z_front", rope="heart", usta_back=USTA_BACK_OTS)),
    S(17.8, 20.9, lambda t: shop(t, push(USTA_MCU, t, 17.8, 20.9, 0.05), usta="E_loupe", rope="heart", bg_blur=8, deniz_blur=6, usta_blinks=False)),
    S(20.9, 23.4, plate(lambda t: ins4.flip_gear(flip_f(t)), 20.9, 23.4, 1.0, 1.1)),
    S(23.4, 28.2, lambda t: shop(t, push(USTA_CU, t, 23.4, 28.2, 0.06), usta="E_soft", rope="heart", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(28.2, 32.4, lambda t: shop(t, push(USTA_CU, t, 28.2, 32.4, 0.1), usta="E_soft", rope="heart", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(32.4, 34.4, lambda t: door(t, push(EMRE_CU, t, 32.4, 34.4, 0.05), emre="Z_tear", rope="heart")),
    S(34.4, 37.6, lambda t: shop(t, push(USTA_MCU, t, 34.4, 37.6, 0.05), usta="E_soft", rope="heart", bg_blur=8, deniz_blur=6, usta_blinks=False)),
    S(37.6, 41.2, plate(lambda t: ins4.new_gear(), 37.6, 41.2, 1.0, 1.07)),
    S(41.2, 43.6, lambda t: door(t, push(EMRE_CU, t, 41.2, 43.6, 0.06), emre="Z_tear", rope="none", emre_mouth=0.0)),
    S(43.6, 50.0, plate(lambda t: _ticket(round(min(1, max(0, (t - 43.9) / 4.5)) * 60) / 60, round(min(1, max(0, (t - 49.0) / 0.35)) * 8) / 8), 43.6, 50.0, 1.04, 1.0)),
    S(50.0, 53.0, plate(lambda t: _cta(), 50.0, 53.0, 1.0, 1.0)),
]


def frame_at(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            img = fn(t)
            break
    else:
        img = Image.new("RGB", (W, H))
    img = finish(img, t, dust=False, grain=False)
    if t < 43.6:
        img = subtitle(img, sub_at(t))
    if t > TOTAL - 0.6:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.6: int(v * max(k, 0)))
    if 49.7 <= t < 50.3:
        k = abs(t - 50.0) / 0.3
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
    add(f"{SFX}/tiktak.mp3", 0.0, 0.75, ",afade=t=out:st=4.2:d=0.6")
    add(f"{SFX}/tiktak.mp3", 11.4, 0.6, ",atrim=0:1.8,afade=t=out:st=1.4:d=0.4")
    add(f"{SFX}/tiktak.mp3", 20.9, 0.5, ",atrim=0:2.5,afade=t=out:st=2.0:d=0.5")
    add(f"{SFX}/cark_cevir.mp3", 21.3, 0.8)
    add(f"{SFX}/loupe.mp3", 7.6, 0.8)
    add(f"{SFX}/cingirak_cikis.mp3", 42.4, 0.45)
    add(f"{SFX}/kalem.mp3", 43.9, 0.7)
    add(f"{SFX}/damga.mp3", 49.0, 0.8)
    add(f"{SFX}/muzik.mp3", 21.0, 0.28, f",afade=t=in:st=0:d=3,afade=t=out:st={TOTAL - 21.0 - 3.5}:d=3.5")
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
