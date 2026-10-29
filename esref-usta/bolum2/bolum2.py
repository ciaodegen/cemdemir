"""Bölüm 2 — "Orijinal Parça" (~64 sn)."""
import sys, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
from PIL import Image
from engine import W, H, FPS, ROOT, finish, subtitle, envelope, duration, smooth
import scenes3d as s3
from scenes3d import (shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU,
                      USTA_BACK_OTS, loupe_in)
from scenes import split_sub, plate
import inserts as ins
import inserts2 as ins2

REP = f"{ROOT}/bolum2/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = Elif), subtitle
    ("01_E", "E", "Usta… gülüş değiştiriyor musunuz?"),
    ("02_D", "D", "Abla yenisini al. Herkes alıyor zaten."),
    ("03_U", "U", "Deniz."),
    ("04_U", "U", "Neyi var bunun?"),
    ("05_E", "E", "Çarpık. Gülünce gözlerim kayboluyor. Fotoğraflarda hep elimle kapatıyorum."),
    ("06_U", "U", "Bu gamze kimden?"),
    ("07_E", "E", "Babaannemden."),
    ("08_U", "U", "Ya bu çentik?"),
    ("09_E", "E", "Yedi yaşında bisikletten düştüm. Babam bir hafta beni güldürmeye uğraştı."),
    ("10_E", "E", "Ama herkesinki düz, bembeyaz. Ben de öyle istiyorum."),
    ("11_U", "U", "Yenileri orada. Seç bakalım."),
    ("12_E", "E", "Hepsi… aynı."),
    ("13_U", "U", "Aynı. O yüzden kimse hatırlamaz."),
    ("14_D", "D", "Abla… bence seninki daha güzel."),
    ("15_U", "U", "Deniz."),
    ("16_U", "U", "Bu parça orijinal kızım. Piyasada yok."),
]
START = {0: 0.8, 1: 3.5, 2: 5.7, 3: 7.2, 4: 9.1, 5: 15.7, 6: 17.45, 7: 18.7, 8: 20.5, 9: 24.9,
         10: 30.5, 11: 35.3, 12: 37.9, 13: 41.8, 14: 44.75, 15: 46.3}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
TOTAL = 63.6
FIELDS = (("Arıza:", "Yok."),
          ("Yapılan işlem:", "Hiçbir şey. Orijinal parça."),
          ("Not:", "Kusursuz gülüşler birbirine benzer. Seninki sadece sana benzer."))


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["E"] = [2.2, 6.4, 11.0, 13.9, 19.3, 23.2, 27.5, 33.0, 36.4, 40.3, 47.8, 52.1]


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
def _i2(name, *a):
    return getattr(ins2, name)(*a)


@functools.lru_cache(None)
def _ticket(progress, stamp):
    return ins.ticket(progress, stamp, "002", FIELDS, "ORİJİNAL")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Gülüşünü saklayan", "arkadaşına gönder."), "Eşref Usta · Bölüm 2")


ELIF_BACK_WIDE = (120, 560, 0.95, 5, "F_back")


def shotF(t):  # loupe goes on
    p = loupe_in(t, 13.85)
    cam = push(USTA_CU, t, 13.7, 15.6, 0.06)
    if p is None:
        return shop(t, cam, usta="E_front", rope="box", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="box", bg_blur=9, deniz_blur=8, usta_blinks=False)


def S(t0, t1, fn):
    return (t0, t1, fn)


SHOTS = [
    S(0.0, 3.4, lambda t: shop(t, push(WIDE, t, 0, 3.4, 0.04), deniz="D_phone", rope="box",
                               emre_back=(120 - 220 * (1 - smooth(t / 1.1)), 560, 0.95, 5, "F_back"))),
    S(3.4, 5.6, lambda t: shop(t, push(DENIZ_MCU, t, 3.4, 5.6), deniz="D_phone", rope="box", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(5.6, 7.0, lambda t: shop(t, push(USTA_MCU, t, 5.6, 7.0), usta="E_side", deniz="D_phone", rope="box", bg_blur=8, deniz_blur=6)),
    S(7.0, 9.0, plate(lambda t: _i2("velvet_box", t >= 7.35), 7.0, 9.0, 1.25, 1.32)),
    S(9.0, 13.7, lambda t: door(t, push(EMRE_MCU, t, 9.0, 13.7, 0.1), emre="F_shy", rope="box")),
    S(13.7, 15.6, shotF),
    S(15.6, 18.6, plate(lambda t: _i2("loupe_dimple"), 15.6, 18.6, 1.0, 1.06)),
    S(18.6, 20.4, plate(lambda t: _i2("loupe_chip"), 18.6, 20.4, 1.0, 1.05)),
    S(20.4, 24.8, lambda t: door(t, push(EMRE_MCU, t, 20.4, 24.8, 0.06), emre="F_soft", rope="box", usta_back=USTA_BACK_OTS)),
    S(24.8, 30.1, lambda t: door(t, push(EMRE_CU, t, 24.8, 30.1, 0.08), emre="F_front", rope="box")),
    S(30.1, 33.6, lambda t: shop(t, push(USTA_MCU, t, 30.1, 33.6, 0.04), usta="E_front", rope="box", bg_blur=8, deniz_blur=6)),
    S(33.6, 35.2, plate(lambda t: _i2("jar"), 33.6, 35.2, 1.0, 1.08)),
    S(35.2, 37.8, lambda t: door(t, push(EMRE_CU, t, 35.2, 37.8, 0.04), emre="F_stun", rope="box")),
    S(37.8, 41.6, lambda t: shop(t, push(USTA_CU, t, 37.8, 41.6, 0.05), usta="E_front", rope="box", bg_blur=9, deniz_blur=8)),
    S(41.6, 44.6, lambda t: shop(t, push(DENIZ_MCU, t, 41.6, 44.6, 0.06), deniz="D_sincere", rope="box", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(44.6, 46.2, lambda t: shop(t, push(USTA_MCU, t, 44.6, 46.2, 0.03), usta="E_proud", rope="box", bg_blur=8, deniz_blur=6, usta_blinks=False)),
    S(46.2, 51.0, lambda t: shop(t, push(USTA_MCU, t, 46.2, 51.0, 0.1), usta="E_soft", rope="box", bg_blur=8, deniz_blur=6, usta_blinks=False)),
    S(51.0, 54.0, lambda t: door(t, push(EMRE_CU, t, 51.0, 54.0, 0.08), emre="F_smile", rope="none", emre_mouth=0.0)),
    S(54.0, 60.4, plate(lambda t: _ticket(round(min(1, max(0, (t - 54.3) / 4.5)) * 60) / 60, round(min(1, max(0, (t - 59.4) / 0.35)) * 8) / 8), 54.0, 60.4, 1.04, 1.0)),
    S(60.4, 63.6, plate(lambda t: _cta(), 60.4, 63.6, 1.0, 1.0)),
]


def frame_at(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            img = fn(t)
            break
    else:
        img = Image.new("RGB", (W, H))
    img = finish(img, t, dust=False, grain=False)
    if t < 54.0:
        img = subtitle(img, sub_at(t))
    if t < 0.4:
        img = Image.eval(img, lambda v, k=t / 0.4: int(v * k))
    if t > TOTAL - 0.6:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.6: int(v * max(k, 0)))
    if 60.1 <= t < 60.7:
        k = abs(t - 60.4) / 0.3
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
    add(f"{SFX}/telefon_cevir.mp3", 0.5, 0.4)
    add(f"{SFX}/telefon_cevir.mp3", 7.3, 0.5)
    add(f"{SFX}/loupe.mp3", 14.1, 0.8)
    add(f"{SFX}/cingirak_cikis.mp3", 52.6, 0.45)
    add(f"{SFX}/kalem.mp3", 54.3, 0.7)
    add(f"{SFX}/damga.mp3", 59.4, 0.8)
    add(f"{SFX}/muzik.mp3", 41.3, 0.30, f",afade=t=in:st=0:d=3,afade=t=out:st={TOTAL - 41.3 - 3.5}:d=3.5")
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
