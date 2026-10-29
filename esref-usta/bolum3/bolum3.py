"""Bölüm 3 — "Söküm" (~39 sn)."""
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
    ("06_U", "U", "Hâlâ dönüyor bu."),
    ("07_Z", "E", "Biliyorum. O yüzden geldim. Her gece aynı yerde takılıyor."),
    ("09_U", "U", "Bu çark o değil kızım. Bu, onunla olan sen."),
    ("10_U", "U", "Sen onu değil… o zamanki kendini özlüyorsun."),
    ("11_Z", "E", "…O zamanlar çok gülüyordum."),
    ("12_U", "U", "Sökmeyelim. Yanına yenisini takalım."),
]
START = {0: 0.25, 1: 5.3, 2: 6.9, 3: 13.9, 4: 18.6, 5: 22.7, 6: 24.5}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
TOTAL = 38.6
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
s3.BLINKS["E"] = [8.2, 10.6, 23.9, 28.4]
s3.BLINKS["U"] = [4.6, 15.2, 20.9, 25.8]


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


def shotB(t):  # loupe goes on
    p = loupe_in(t, 3.85)
    cam = push(USTA_CU, t, 3.7, 5.2, 0.05)
    if p is None:
        return shop(t, cam, usta="E_front", rope="heart", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="heart", bg_blur=9, deniz_blur=8, usta_blinks=False)


def flip_f(t):
    return round(min(1, max(0, (t - 11.8) / 0.7)) * 14) / 14


SHOTS = [
    S(0.0, 3.7, plate(lambda t: ins4.heart(tick(t)), 0.0, 3.7, 1.0, 1.12)),
    S(3.7, 5.2, shotB),
    S(5.2, 6.8, plate(lambda t: ins4.loupe_gear(tick(t)), 5.2, 6.8, 1.0, 1.05)),
    S(6.8, 11.5, lambda t: door(t, push(EMRE_MCU, t, 6.8, 11.5, 0.1), emre="Z_front", rope="heart", usta_back=USTA_BACK_OTS)),
    S(11.5, 13.8, plate(lambda t: ins4.flip_gear(flip_f(t)), 11.5, 13.8, 1.0, 1.1)),
    S(13.8, 18.5, lambda t: shop(t, push(USTA_CU, t, 13.8, 18.5, 0.06), usta="E_soft", rope="heart", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(18.5, 22.6, lambda t: shop(t, push(USTA_CU, t, 18.5, 22.6, 0.1), usta="E_soft", rope="heart", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(22.6, 24.4, lambda t: door(t, push(EMRE_CU, t, 22.6, 24.4, 0.05), emre="Z_tear", rope="heart")),
    S(24.4, 27.8, plate(lambda t: ins4.new_gear(), 24.4, 27.8, 1.0, 1.07)),
    S(27.8, 29.8, lambda t: door(t, push(EMRE_CU, t, 27.8, 29.8, 0.06), emre="Z_tear", rope="none", emre_mouth=0.0)),
    S(29.8, 35.6, plate(lambda t: _ticket(round(min(1, max(0, (t - 30.0) / 3.8)) * 60) / 60, round(min(1, max(0, (t - 34.6) / 0.35)) * 8) / 8), 29.8, 35.6, 1.04, 1.0)),
    S(35.6, 38.6, plate(lambda t: _cta(), 35.6, 38.6, 1.0, 1.0)),
]


def frame_at(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            img = fn(t)
            break
    else:
        img = Image.new("RGB", (W, H))
    img = finish(img, t, dust=False, grain=False)
    if t < 29.8:
        img = subtitle(img, sub_at(t))
    if t > TOTAL - 0.6:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.6: int(v * max(k, 0)))
    if 35.3 <= t < 35.9:
        k = abs(t - 35.6) / 0.3
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
    add(f"{SFX}/tiktak.mp3", 0.0, 0.75, ",afade=t=out:st=4.0:d=0.6")
    add(f"{SFX}/loupe.mp3", 4.1, 0.8)
    add(f"{SFX}/tiktak.mp3", 5.2, 0.6, ",atrim=0:1.6,afade=t=out:st=1.2:d=0.4")
    add(f"{SFX}/tiktak.mp3", 11.5, 0.5, ",atrim=0:2.3,afade=t=out:st=1.8:d=0.5")
    add(f"{SFX}/cark_cevir.mp3", 11.8, 0.8)
    add(f"{SFX}/cingirak_cikis.mp3", 28.8, 0.45)
    add(f"{SFX}/kalem.mp3", 30.0, 0.7)
    add(f"{SFX}/damga.mp3", 34.6, 0.8)
    add(f"{SFX}/muzik.mp3", 11.5, 0.28, f",afade=t=in:st=0:d=2.5,afade=t=out:st={TOTAL - 11.5 - 3.0}:d=3.0")
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
