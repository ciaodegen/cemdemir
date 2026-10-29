"""Bölüm 4 — "Çalmayan Telefon" (~43 sn)."""
import sys, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum4")
from PIL import Image
from engine import W, H, FPS, ROOT, finish, subtitle, envelope, duration, smooth
import scenes3d as s3
from scenes3d import (shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU,
                      USTA_BACK_OTS, loupe_in)
from scenes import split_sub, plate
import inserts as ins
import inserts5 as ins5

REP = f"{ROOT}/bolum4/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = Saniye Teyze), subtitle
    ("01_S", "E", "Usta, telefonum hiç çalmıyor. Bozuk mu acaba?"),
    ("02_D", "D", "Teyzeciğim yenisini alalım, akıllısından."),
    ("03_U", "U", "Deniz."),
    ("06_U", "U", "Bozuk değil teyzem. Çalıyor."),
    ("07_S", "E", "Biliyorum oğlum… Bayramlarda çalıyor."),
    ("08_S", "E", "Çocuklar evlendi, gittiler. Beyim de gideli beş yıl oldu."),
    ("09_S", "E", "Ben bayramı beklemekten yoruldum."),
    ("10_U", "U", "Bunu ben tamir edemem."),
    ("11_D", "D", "Anne? Yok bir şey… Sesini duymak istedim."),
]
START = {0: 0.5, 1: 4.3, 2: 6.5, 3: 14.5, 4: 17.0, 5: 19.9, 6: 23.7, 7: 26.2, 8: 29.9}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
TOTAL = 43.0
FIELDS = (("Arıza:", "Telefon sağlam. Arayan yok."),
          ("Yapılan işlem:", "Dükkândan arandı."),
          ("Not:", "Bazı telefonlar bozulmaz, sadece unutulur."))


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["E"] = [3.9, 18.6, 22.2, 25.9, 33.4]
s3.BLINKS["U"] = [2.2, 10.0, 16.2, 27.9]


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
    return ins.ticket(progress, stamp, "004", FIELDS, "SAĞLAM")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Annesini en son bayramda", "arayan birine gönder."), "Eşref Usta · Bölüm 4")


def S(t0, t1, fn):
    return (t0, t1, fn)


def shotD(t):  # loupe goes on
    p = loupe_in(t, 8.15)
    cam = push(USTA_CU, t, 8.0, 9.4, 0.05)
    if p is None:
        return shop(t, cam, usta="E_front", rope="oldphone", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="oldphone", bg_blur=9, deniz_blur=8, usta_blinks=False)


SHOTS = [
    S(0.0, 4.2, lambda t: shop(t, push(WIDE, t, 0, 4.2, 0.04), deniz="D_phone", rope="oldphone",
                               emre_back=(120 - 220 * (1 - smooth(t / 1.0)), 560, 0.95, 5, "S_back"))),
    S(4.2, 6.4, lambda t: shop(t, push(DENIZ_MCU, t, 4.2, 6.4), deniz="D_phone", rope="oldphone", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(6.4, 8.0, lambda t: shop(t, push(USTA_MCU, t, 6.4, 8.0), usta="E_side", deniz="D_phone", rope="oldphone", bg_blur=8, deniz_blur=6)),
    S(8.0, 9.4, shotD),
    S(9.4, 11.8, plate(lambda t: ins5.call_log(), 9.4, 11.8, 1.5, 1.7, cy=0.25)),
    S(11.8, 14.4, plate(lambda t: ins5.ringing(int(t * 16)), 11.8, 14.4, 1.3, 1.36, cy=0.35)),
    S(14.4, 16.9, lambda t: shop(t, push(USTA_MCU, t, 14.4, 16.9, 0.04), usta="E_front", rope="oldphone", bg_blur=8, deniz_blur=6)),
    S(16.9, 19.8, lambda t: door(t, push(EMRE_MCU, t, 16.9, 19.8, 0.05), emre="S_smile", rope="oldphone", usta_back=USTA_BACK_OTS)),
    S(19.8, 23.6, lambda t: door(t, push(EMRE_MCU, t, 19.8, 23.6, 0.1), emre="S_sad", rope="oldphone")),
    S(23.6, 26.1, lambda t: door(t, push(EMRE_CU, t, 23.6, 26.1, 0.05), emre="S_smile", rope="oldphone")),
    S(26.1, 28.1, lambda t: shop(t, push(USTA_CU, t, 26.1, 28.1, 0.05), usta="E_serious", rope="oldphone", bg_blur=9, deniz_blur=8)),
    S(28.1, 29.8, plate(lambda t: ins5.deniz_calls_mom(), 28.1, 29.8, 1.0, 1.05)),
    S(29.8, 33.6, lambda t: shop(t, push(DENIZ_MCU, t, 29.8, 33.6, 0.06), deniz="D_sincere", rope="oldphone", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(33.6, 35.4, lambda t: door(t, push(EMRE_CU, t, 33.6, 35.4, 0.05), emre="S_smile", rope="none", emre_mouth=0.0)),
    S(35.4, 40.0, plate(lambda t: _ticket(round(min(1, max(0, (t - 35.6) / 3.2)) * 60) / 60, round(min(1, max(0, (t - 39.2) / 0.35)) * 8) / 8), 35.4, 40.0, 1.04, 1.0)),
    S(40.0, 43.0, plate(lambda t: _cta(), 40.0, 43.0, 1.0, 1.0)),
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
    if 39.7 <= t < 40.3:
        k = abs(t - 40.0) / 0.3
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
    add(f"{SFX}/telefon_cevir.mp3", 0.7, 0.4)
    add(f"{SFX}/loupe.mp3", 8.4, 0.8)
    add(f"{SFX}/eski_telefon_caliyor.mp3", 11.8, 0.7, ",afade=t=out:st=2.2:d=0.4")
    add(f"{SFX}/telefon.mp3", 28.1, 0.35)
    add(f"{SFX}/cingirak_cikis.mp3", 34.4, 0.45)
    add(f"{SFX}/kalem.mp3", 35.6, 0.7)
    add(f"{SFX}/damga.mp3", 39.2, 0.8)
    add(f"{SFX}/muzik.mp3", 19.8, 0.28, f",afade=t=in:st=0:d=2.5,afade=t=out:st={TOTAL - 19.8 - 3.0}:d=3.0")
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
