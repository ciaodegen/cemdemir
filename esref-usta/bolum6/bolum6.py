"""Bölüm 6 — "Ekstre" (~43 sn)."""
import sys, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum6")
from PIL import Image
from engine import W, H, FPS, ROOT, finish, subtitle, envelope, duration, smooth
import scenes3d as s3
from scenes3d import (shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU,
                      USTA_BACK_OTS, loupe_in)
from scenes import split_sub, plate
import inserts as ins
import inserts8 as ins8

REP = f"{ROOT}/bolum6/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = Hakan), subtitle
    ("01_H", "E", "Usta, kredi kartı ekstremde harcamadığım şeyler var."),
    ("02_D", "D", "Abi, onlara gizli masraf diyorlar. Bankayı ara."),
    ("03_U", "U", "Deniz."),
    ("04_U", "U", "Dur, bir bakalım…"),
    ("05_U", "U", "Babanla balık tutmak. Ertelendi."),
    ("06_U", "U", "Oğlunun okul gösterisi. Ertelendi."),
    ("07_U", "U", "Eşinle tatil. Seneye."),
    ("08_U", "U", "Toplam borç… on bir yıl."),
    ("09_H", "E", "Hep… sonra yaparım dedim."),
    ("10_U", "U", "Bu borç faizle büyür evlat. Ama parayla ödenmez."),
]
START = {0: 0.5, 1: 3.9, 2: 6.35, 3: 7.9, 4: 9.6, 5: 12.9, 6: 16.5, 7: 18.7, 8: 22.8, 9: 25.4}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
TOTAL = 43.2
FIELDS = (("Arıza:", "Ekstrede ertelenmiş bir hayat."),
          ("Yapılan işlem:", "İlk taksit ödendi. Pazar, balık."),
          ("Not:", "Bazı borçlar parayla değil, zamanla ödenir."))


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["E"] = [24.6, 34.3]
s3.BLINKS["U"] = [2.4, 5.4, 27.6]


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
    return ins.ticket(progress, stamp, "006", FIELDS, "İLK TAKSİT ÖDENDİ")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Hep \u201csonra\u201d diyen", "birine gönder."), "Eşref Usta · Bölüm 6")


def S(t0, t1, fn):
    return (t0, t1, fn)


def shotD(t):  # loupe goes on
    p = loupe_in(t, 7.95)
    cam = push(USTA_CU, t, 7.8, 9.5, 0.05)
    if p is None:
        return shop(t, cam, usta="E_read", rope="paper", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="paper", bg_blur=9, deniz_blur=8, usta_blinks=False)


def q(x):
    return int(round(min(1, max(0, x)) * 10))


SHOTS = [
    S(0.0, 3.8, lambda t: shop(t, push(WIDE, t, 0, 3.8, 0.04), deniz="D_phone", rope="paper",
                               emre_back=(120 - 220 * (1 - smooth(t / 1.0)), 560, 0.95, 5, "R_back"))),
    S(3.8, 6.3, lambda t: shop(t, push(DENIZ_MCU, t, 3.8, 6.3), deniz="D_phone", rope="paper", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(6.3, 7.8, lambda t: shop(t, push(USTA_MCU, t, 6.3, 7.8), usta="E_side", deniz="D_phone", rope="paper", bg_blur=8, deniz_blur=6)),
    S(7.8, 9.5, shotD),
    S(9.5, 12.8, plate(lambda t: ins8.loupe_first(), 9.5, 12.8, 1.0, 1.06)),
    S(12.8, 16.4, plate(lambda t: ins8.stmt(2, False, 0, 0), 12.8, 16.4, 1.15, 1.2, cy=0.2)),
    S(16.4, 18.6, plate(lambda t: ins8.stmt(3, False, 0, 0), 16.4, 18.6, 1.15, 1.2, cy=0.25)),
    S(18.6, 22.7, plate(lambda t: ins8.stmt(3, True, 0, 0), 18.6, 22.7, 1.05, 1.25, cy=0.55)),
    S(22.7, 25.3, lambda t: door(t, push(EMRE_MCU, t, 22.7, 25.3, 0.06), emre="R_sad", rope="paper", usta_back=USTA_BACK_OTS)),
    S(25.3, 30.5, lambda t: shop(t, push(USTA_CU, t, 25.3, 30.5, 0.1), usta="E_soft", rope="paper", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(30.5, 33.9, plate(lambda t: ins8.stmt(3, True, q((t - 30.8) / 0.6), q((t - 31.5) / 1.4)), 30.5, 33.9, 1.25, 1.35, cy=0.2)),
    S(33.9, 35.6, lambda t: door(t, push(EMRE_CU, t, 33.9, 35.6, 0.05), emre="R_soft", rope="none", emre_mouth=0.0)),
    S(35.6, 40.4, plate(lambda t: _ticket(round(min(1, max(0, (t - 35.8) / 3.2)) * 60) / 60, round(min(1, max(0, (t - 39.6) / 0.35)) * 8) / 8), 35.6, 40.4, 1.04, 1.0)),
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
    if t < 35.6:
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
    add(f"{SFX}/gazete.mp3", 0.5, 0.35, ",atrim=0:1.2")
    add(f"{SFX}/loupe.mp3", 8.2, 0.6)
    add(f"{SFX}/gazete.mp3", 12.8, 0.25, ",atrim=0:0.8")
    add(f"{SFX}/kalem.mp3", 30.8, 0.75, ",atrim=0:2.2,afade=t=out:st=1.9:d=0.3")
    add(f"{SFX}/cingirak_cikis.mp3", 35.0, 0.4)
    add(f"{SFX}/kalem.mp3", 35.8, 0.7, ",atrim=0:3.2,afade=t=out:st=2.8:d=0.4")
    add(f"{SFX}/damga.mp3", 39.6, 0.8)
    add(f"{SFX}/muzik.mp3", 22.7, 0.28, f",afade=t=in:st=0:d=2.5,afade=t=out:st={TOTAL - 22.7 - 3.0}:d=3.0")
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
