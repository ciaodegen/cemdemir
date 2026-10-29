"""Bölüm 2 — "Ağır Çanta" (~53 sn)."""
import sys, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
from PIL import Image
from engine import W, H, FPS, ROOT, finish, subtitle, envelope, duration, smooth
import scenes3d as s3
from scenes3d import (shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU,
                      USTA_BACK_OTS, loupe_in)
from scenes import split_sub, plate
import inserts as ins
import inserts3 as ins3

REP = f"{ROOT}/bolum2b/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = Efe), subtitle
    ("01_K", "E", "Usta… babamın çantasını hafifletebilir misiniz?"),
    ("02_D", "D", "Ufaklık, yenisini alın. Hafifinden."),
    ("03_U", "U", "Deniz."),
    ("04_U", "U", "Neden hafiflesin?"),
    ("05_K", "E", "Babam akşam eve gelince çantayı bırakıyor… sonra hiç konuşmuyor. Çok ağır olmalı."),
    ("06_U", "U", "Bakalım içinde ne var."),
    ("07_U", "U", "Okul taksiti… Efe."),
    ("08_K", "E", "O benim."),
    ("09_U", "U", "Doğum günü hediyesi… Efe'ye."),
    ("10_U", "U", "Bu da kira."),
    ("11_K", "E", "Hepsi… benim için mi?"),
    ("12_U", "U", "Bunu hafifletemem evlat. İçindekilerin hepsi senin."),
    ("13_U", "U", "Akşam kapıda karşıla onu. Çanta hafiflemez… ama baban hafifler."),
]
START = {0: 0.9, 1: 4.7, 2: 7.7, 3: 9.1, 4: 11.5, 5: 17.8, 6: 20.1, 7: 22.3, 8: 24.1, 9: 27.0,
         10: 28.7, 11: 30.95, 12: 35.5}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
TOTAL = 53.0
FIELDS = (("Arıza:", "Çanta ağır."),
          ("Yapılan işlem:", "Açıldı, bakıldı, geri kondu."),
          ("Not:", "Bazı yükler ağırdır, çünkü sevgiyle taşınır."))


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["E"] = [2.4, 6.8, 10.2, 14.1, 19.0, 25.5, 31.8, 34.2, 38.6, 41.9]


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


@functools.lru_cache(None)
def _i3(name, *a):
    return getattr(ins3, name)(*a)


@functools.lru_cache(None)
def _ticket(progress, stamp):
    return ins.ticket(progress, stamp, "002", FIELDS, "TAMİR GEREKMEZ")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Babana gönder.",), "Eşref Usta · Bölüm 2")


def S(t0, t1, fn):
    return (t0, t1, fn)


SHOTS = [
    S(0.0, 4.6, lambda t: shop(t, push(WIDE, t, 0, 4.6, 0.04), deniz="D_phone", rope="case",
                               emre_back=(150 - 220 * (1 - smooth(t / 1.1)), 640, 0.95, 5, "K_back"))),
    S(4.6, 7.6, lambda t: shop(t, push(DENIZ_MCU, t, 4.6, 7.6), deniz="D_phone", rope="case", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(7.6, 9.0, lambda t: shop(t, push(USTA_MCU, t, 7.6, 9.0), usta="E_side", deniz="D_phone", rope="case", bg_blur=8, deniz_blur=6)),
    S(9.0, 11.4, lambda t: shop(t, push(USTA_CU, t, 9.0, 11.4, 0.04), usta="E_front", rope="case", bg_blur=9, deniz_blur=8)),
    S(11.4, 17.7, lambda t: door(t, push(EMRE_MCU, t, 11.4, 17.7, 0.12), emre="K_sad", rope="case")),
    S(17.7, 20.0, plate(lambda t: _i3("briefcase", t >= 18.5), 17.7, 20.0, 1.05, 1.12)),
    S(20.0, 22.2, plate(lambda t: _i3("receipt"), 20.0, 22.2, 1.0, 1.06)),
    S(22.2, 24.0, lambda t: door(t, push(EMRE_CU, t, 22.2, 24.0, 0.03), emre="K_look", rope="case")),
    S(24.0, 26.9, plate(lambda t: _i3("gift"), 24.0, 26.9, 1.0, 1.06)),
    S(26.9, 28.6, plate(lambda t: _i3("rent"), 26.9, 28.6, 1.0, 1.05)),
    S(28.6, 30.8, lambda t: door(t, push(EMRE_CU, t, 28.6, 30.8, 0.05), emre="K_look", rope="case")),
    S(30.8, 35.3, lambda t: shop(t, push(USTA_MCU, t, 30.8, 35.3, 0.08), usta="E_soft", rope="case", bg_blur=8, deniz_blur=6, usta_blinks=False)),
    S(35.3, 40.6, lambda t: shop(t, push(USTA_CU, t, 35.3, 40.6, 0.1), usta="E_soft", rope="case", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(40.6, 43.6, lambda t: door(t, push(EMRE_CU, t, 40.6, 43.6, 0.06), emre="K_smile", rope="none", emre_mouth=0.0)),
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
    if t < 0.4:
        img = Image.eval(img, lambda v, k=t / 0.4: int(v * k))
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
    add(f"{SFX}/cingirak.mp3", 0.0, 0.6)
    add(f"{SFX}/damga.mp3", 0.7, 0.35)
    add(f"{SFX}/telefon_cevir.mp3", 18.45, 0.6)
    add(f"{SFX}/gazete.mp3", 19.0, 0.4)
    add(f"{SFX}/cingirak_cikis.mp3", 42.4, 0.45)
    add(f"{SFX}/kalem.mp3", 43.9, 0.7)
    add(f"{SFX}/damga.mp3", 49.0, 0.8)
    add(f"{SFX}/muzik.mp3", 28.4, 0.30, f",afade=t=in:st=0:d=3,afade=t=out:st={TOTAL - 28.4 - 3.5}:d=3.5")
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
