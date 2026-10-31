"""Bölüm 5 — "Sigaranın Üstündeki Yazılar" (~43 sn)."""
import sys, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum5")
from PIL import Image
from engine import W, H, FPS, ROOT, finish, subtitle, envelope, duration, smooth
import scenes3d as s3
from scenes3d import (shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU,
                      USTA_BACK_OTS, loupe_in)
from scenes import split_sub, plate
import inserts as ins
import inserts7 as ins7

REP = f"{ROOT}/bolum5/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = Kemal), subtitle
    ("01_K", "E", "Usta, sigaramın üstünde yazılar çıkıyor. Okuyabilir misiniz?"),
    ("02_D", "D", "Abi, onlar marka yazısı."),
    ("03_U", "U", "Deniz."),
    ("04_U", "U", "Dur, bir bakalım…"),
    ("05_U", "U", "Kızının düğünü."),
    ("06_K", "E", "Ne?"),
    ("07_U", "U", "Torununu kucağına alman."),
    ("08_U", "U", "Emekli olunca o deniz kenarı."),
    ("09_K", "E", "Sabah iki tane içtim… Onlarda ne yazıyordu?"),
    ("10_U", "U", "Artık okunmuyor."),
    ("11_U", "U", "Bunlar sigara değil evlat. Bunlar senin günlerin. Her biri bir tanesini yakıyor."),
    ("12_K", "E", "Kalanları siz saklayın usta."),
]
START = {0: 1.0, 1: 4.7, 2: 6.35, 3: 7.75, 4: 9.6, 5: 11.5, 6: 14.0, 7: 16.9, 8: 19.7, 9: 22.6, 10: 24.3, 11: 31.0}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
TOTAL = 43.2
FIELDS = (("Arıza:", "Paket dolu."),
          ("Yapılan işlem:", "Okundu. Emanete alındı."),
          ("Not:", "Her sigara bir gün yakmaz. Bir anı yakar."))


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["E"] = [12.9, 20.8, 22.1, 32.4]
s3.BLINKS["U"] = [2.4, 5.1, 26.0]


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
    return ins.ticket(progress, stamp, "005", FIELDS, "SÖNDÜRÜLDÜ")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Sigarasının üstünde ne yazdığını", "bilmeyen birine gönder."), "Eşref Usta · Bölüm 5")


def S(t0, t1, fn):
    return (t0, t1, fn)


def shotD(t):  # loupe goes on
    p = loupe_in(t, 7.7)
    cam = push(USTA_CU, t, 7.6, 9.4, 0.05)
    if p is None:
        return shop(t, cam, usta="E_read", rope="pack", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="pack", bg_blur=9, deniz_blur=8, usta_blinks=False)


def cig_stage(t):
    return 1 if t < 14.0 else (2 if t < 16.8 else 3)


SHOTS = [
    S(0.0, 4.6, lambda t: shop(t, push(WIDE, t, 0, 4.6, 0.04), deniz="D_phone", rope="pack",
                               emre_back=(120 - 220 * (1 - smooth(t / 1.0)), 560, 0.95, 5, "H_back"))),
    S(4.6, 6.3, lambda t: shop(t, push(DENIZ_MCU, t, 4.6, 6.3), deniz="D_phone", rope="pack", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(6.3, 7.6, lambda t: shop(t, push(USTA_MCU, t, 6.3, 7.6), usta="E_side", deniz="D_phone", rope="pack", bg_blur=8, deniz_blur=6)),
    S(7.6, 9.4, shotD),
    S(9.4, 11.4, plate(lambda t: ins7.loupe_note(), 9.4, 11.4, 1.0, 1.06)),
    S(11.4, 13.7, lambda t: door(t, push(EMRE_CU, t, 11.4, 13.7, 0.04), emre="H_stun", rope="pack", usta_back=USTA_BACK_OTS)),
    S(13.7, 19.6, plate(lambda t: ins7.counter_cigs(cig_stage(t)), 13.7, 19.6, 1.0, 1.08, cy=0.6)),
    S(19.6, 22.4, lambda t: door(t, push(EMRE_MCU, t, 19.6, 22.4, 0.06), emre="H_sad", rope="pack")),
    S(22.4, 24.2, plate(lambda t: ins7.ashtray(), 22.4, 24.2, 1.0, 1.08)),
    S(24.2, 30.9, lambda t: shop(t, push(USTA_CU, t, 24.2, 30.9, 0.1), usta="E_soft", rope="pack", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(30.9, 33.2, lambda t: door(t, push(EMRE_CU, t, 30.9, 33.2, 0.04), emre="H_decided", rope="pack")),
    S(33.2, 35.4, plate(lambda t: ins7.drawer(t >= 34.0), 33.2, 35.4, 1.0, 1.05)),
    S(35.4, 40.4, plate(lambda t: _ticket(round(min(1, max(0, (t - 35.6) / 3.2)) * 60) / 60, round(min(1, max(0, (t - 39.6) / 0.35)) * 8) / 8), 35.4, 40.4, 1.04, 1.0)),
    S(40.4, 43.2, plate(lambda t: _cta(), 40.4, 43.2, 1.0, 1.0)),
]


def frame_at(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            img = fn(t)
            break
    else:
        img = Image.new("RGB", (W, H))
    img = finish(img, t, dust=False, grain=False)
    if t < 35.4:
        img = subtitle(img, sub_at(t))
    if t > TOTAL - 0.6:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.6: int(v * max(k, 0)))
    if 40.1 <= t < 40.7:
        k = abs(t - 40.4) / 0.3
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
    add(f"{SFX}/oksuruk.mp3", 0.25, 0.6)
    add(f"{SFX}/loupe.mp3", 8.0, 0.6)
    add(f"{SFX}/ip.mp3", 14.0, 0.35)
    add(f"{SFX}/ip.mp3", 16.8, 0.35)
    add(f"{SFX}/oksuruk.mp3", 22.9, 0.35)
    add(f"{SFX}/cekmece.mp3", 33.4, 0.7)
    add(f"{SFX}/cingirak_cikis.mp3", 34.8, 0.4)
    add(f"{SFX}/kalem.mp3", 35.6, 0.7, ",atrim=0:3.2,afade=t=out:st=2.8:d=0.4")
    add(f"{SFX}/damga.mp3", 39.6, 0.8)
    add(f"{SFX}/muzik.mp3", 24.2, 0.28, f",afade=t=in:st=0:d=2.5,afade=t=out:st={TOTAL - 24.2 - 3.0}:d=3.0")
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
