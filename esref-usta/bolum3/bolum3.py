"""Bölüm 3 — "Söküm" (~43 sn), standart açılış: dükkân, çıngırak, Deniz esprisi."""
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
    ("06_U", "U", "Hâlâ dönüyor bu."),
    ("07_Z", "E", "Biliyorum. O yüzden geldim. Her gece aynı yerde takılıyor."),
    ("09_U", "U", "Bu çark o değil kızım. Bu, onunla olan sen."),
    ("10_U", "U", "Sen onu değil… o zamanki kendini özlüyorsun."),
    ("11_Z", "E", "…O zamanlar çok gülüyordum."),
    ("12_U", "U", "Sökmeyelim. Yanına yenisini takalım."),
]
START = {0: 0.4, 1: 4.5, 2: 6.5, 3: 9.4, 4: 11.0, 5: 18.0, 6: 22.7, 7: 26.8, 8: 28.6}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
TOTAL = 42.7
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
s3.BLINKS["E"] = [12.4, 14.8, 27.9, 32.4]
s3.BLINKS["U"] = [2.2, 8.9, 19.6, 25.0]


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
    p = loupe_in(t, 7.95)
    cam = push(USTA_CU, t, 7.8, 9.3, 0.05)
    if p is None:
        return shop(t, cam, usta="E_front", rope="heart", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="heart", bg_blur=9, deniz_blur=8, usta_blinks=False)


def flip_f(t):
    return round(min(1, max(0, (t - 15.9) / 0.7)) * 14) / 14


SHOTS = [
    S(0.0, 4.4, lambda t: shop(t, push(WIDE, t, 0, 4.4, 0.04), deniz="D_phone", rope="heart",
                               emre_back=(120 - 220 * (1 - smooth(t / 1.0)), 560, 0.95, 5, "Z_back"))),
    S(4.4, 6.4, lambda t: shop(t, push(DENIZ_MCU, t, 4.4, 6.4), deniz="D_phone", rope="heart", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(6.4, 7.8, lambda t: shop(t, push(USTA_MCU, t, 6.4, 7.8), usta="E_side", deniz="D_phone", rope="heart", bg_blur=8, deniz_blur=6)),
    S(7.8, 9.3, shotD),
    S(9.3, 10.9, plate(lambda t: ins4.loupe_gear(tick(t)), 9.3, 10.9, 1.0, 1.05)),
    S(10.9, 15.6, lambda t: door(t, push(EMRE_MCU, t, 10.9, 15.6, 0.1), emre="Z_front", rope="heart", usta_back=USTA_BACK_OTS)),
    S(15.6, 17.9, plate(lambda t: ins4.flip_gear(flip_f(t)), 15.6, 17.9, 1.0, 1.1)),
    S(17.9, 22.6, lambda t: shop(t, push(USTA_CU, t, 17.9, 22.6, 0.06), usta="E_soft", rope="heart", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(22.6, 26.7, lambda t: shop(t, push(USTA_CU, t, 22.6, 26.7, 0.1), usta="E_soft", rope="heart", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(26.7, 28.5, lambda t: door(t, push(EMRE_CU, t, 26.7, 28.5, 0.05), emre="Z_tear", rope="heart")),
    S(28.5, 31.9, plate(lambda t: ins4.new_gear(), 28.5, 31.9, 1.0, 1.07)),
    S(31.9, 33.9, lambda t: door(t, push(EMRE_CU, t, 31.9, 33.9, 0.06), emre="Z_tear", rope="none", emre_mouth=0.0)),
    S(33.9, 39.7, plate(lambda t: _ticket(round(min(1, max(0, (t - 34.1) / 3.8)) * 60) / 60, round(min(1, max(0, (t - 38.7) / 0.35)) * 8) / 8), 33.9, 39.7, 1.04, 1.0)),
    S(39.7, 42.7, plate(lambda t: _cta(), 39.7, 42.7, 1.0, 1.0)),
]


def frame_at(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            img = fn(t)
            break
    else:
        img = Image.new("RGB", (W, H))
    img = finish(img, t, dust=False, grain=False)
    if t < 33.9:
        img = subtitle(img, sub_at(t))
    if t > TOTAL - 0.6:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.6: int(v * max(k, 0)))
    if 39.4 <= t < 40.0:
        k = abs(t - 39.7) / 0.3
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
    add(f"{SFX}/tiktak.mp3", 0.3, 0.35, ",atrim=0:4.0,afade=t=out:st=3.4:d=0.6")
    add(f"{SFX}/loupe.mp3", 8.2, 0.8)
    add(f"{SFX}/tiktak.mp3", 9.3, 0.6, ",atrim=0:1.6,afade=t=out:st=1.2:d=0.4")
    add(f"{SFX}/tiktak.mp3", 15.6, 0.5, ",atrim=0:2.3,afade=t=out:st=1.8:d=0.5")
    add(f"{SFX}/cark_cevir.mp3", 15.9, 0.8)
    add(f"{SFX}/cingirak_cikis.mp3", 32.9, 0.45)
    add(f"{SFX}/kalem.mp3", 34.1, 0.7)
    add(f"{SFX}/damga.mp3", 38.7, 0.8)
    add(f"{SFX}/muzik.mp3", 15.6, 0.28, f",afade=t=in:st=0:d=2.5,afade=t=out:st={TOTAL - 15.6 - 3.0}:d=3.0")
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
