"""Bölüm 7 — "Boyanmayan Kalp" (~48 sn)."""
import sys, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum7")
from PIL import Image
from engine import W, H, FPS, ROOT, finish, subtitle, envelope, duration, smooth
import scenes3d as s3
from scenes3d import (shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU,
                      USTA_BACK_OTS, loupe_in)
from scenes import split_sub, plate
import inserts as ins
import inserts9 as ins9

REP = f"{ROOT}/bolum7/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = Cengiz), subtitle
    ("01_C", "E", "Usta, Fenerbahçeli olmaktan yoruldum. Şu kalbi sarı-kırmızıya boyar mısın? Galatasaraylı olmak istiyorum."),
    ("02_D", "D", "Doğru seçim abi! Hemen boyayalım!"),
    ("03_U", "U", "Deniz."),
    ("04_U", "U", "Dur. Boyamadan önce bir dinleyelim."),
    ("05_U", "U", "Şampiyonluk."),
    ("06_U", "U", "Galatasaray."),
    ("07_D", "D", "Ayıp ediyor ama usta!"),
    ("08_U", "U", "Fenerbahçe."),
    ("09_C", "E", "Hâlâ… böyle mi atıyor?"),
    ("10_U", "U", "Bu kalp kazanınca atmıyor evlat. Fenerbahçe deyince atıyor. Kazanmak bir gecelik iş. Kalpteki yer ömürlük."),
    ("11_C", "E", "Boyamayın usta. Kalsın."),
    ("12_D", "D", "Galatasaray."),
    ("13_U", "U", "Gördün mü? Renk ayrı, atış aynı."),
]
START = {0: 0.4, 1: 5.7, 2: 7.8, 3: 9.1, 4: 11.6, 5: 14.1, 6: 15.9, 7: 17.4, 8: 21.7, 9: 23.8, 10: 32.7, 11: 34.8, 12: 37.5}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
TOTAL = 48.0
FIELDS = (("Arıza:", "Takım değiştirme talebi."),
          ("Yapılan işlem:", "Dinlendi. Boyanmadı."),
          ("Not:", "Kazanmak bir gecelik. Kalpteki yer ömürlük."))


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["E"] = [22.9, 33.9]
s3.BLINKS["U"] = [2.4, 10.6, 28.0]


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
    return ins.ticket(progress, stamp, "007", FIELDS, "BOYANMADI")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Kaybetse de takımından", "vazgeçmeyen arkadaşına gönder."), "Eşref Usta · Bölüm 7")


def S(t0, t1, fn):
    return (t0, t1, fn)


def beat(t, t0, period=0.46):
    """Heartbeat pulse 0..10 starting at t0 (double thump)."""
    if t < t0:
        return 0
    ph = ((t - t0) % period) / period
    v = max(0.0, 1 - abs(ph - 0.12) / 0.12) + 0.6 * max(0.0, 1 - abs(ph - 0.38) / 0.1)
    return int(round(min(1, v) * 10))


def weak(t, t0):
    return 3 if t0 <= t < t0 + 0.18 else 0


SHOTS = [
    S(0.0, 5.6, lambda t: shop(t, push(WIDE, t, 0, 5.6, 0.04), deniz="D_phone", rope="fbheart",
                               emre_back=(120 - 220 * (1 - smooth(t / 1.0)), 560, 0.95, 5, "G_back"))),
    S(5.6, 7.7, lambda t: shop(t, push(DENIZ_MCU, t, 5.6, 7.7), deniz="D_sincere", rope="fbheart", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(7.7, 9.0, lambda t: shop(t, push(USTA_MCU, t, 7.7, 9.0), usta="E_side", deniz="D_sincere", rope="fbheart", bg_blur=8, deniz_blur=6)),
    S(9.0, 11.4, lambda t: shop(t, push(USTA_MCU, t, 9.0, 11.4, 0.04), usta="E_front", rope="fbheart", bg_blur=8, deniz_blur=6)),
    S(11.4, 14.0, plate(lambda t: ins9.heart_plate(weak(t, 13.15), 0, True, True), 11.4, 14.0, 1.0, 1.05)),
    S(14.0, 15.8, plate(lambda t: ins9.heart_plate(0, 0, True, True), 14.0, 15.8, 1.05, 1.08)),
    S(15.8, 17.3, lambda t: shop(t, push(DENIZ_MCU, t, 15.8, 17.3, 0.03), deniz="D_listen", rope="fbheart", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(17.3, 21.6, plate(lambda t: ins9.heart_plate(beat(t, 19.2), 10 if t >= 19.2 else 0, True, True), 17.3, 21.6, 1.05, 1.15)),
    S(21.6, 23.7, lambda t: door(t, push(EMRE_CU, t, 21.6, 23.7, 0.04), emre="G_stun", rope="fbheart", usta_back=USTA_BACK_OTS)),
    S(23.7, 32.6, lambda t: shop(t, push(USTA_CU, t, 23.7, 32.6, 0.12), usta="E_soft", rope="fbheart", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(32.6, 34.7, lambda t: door(t, push(EMRE_CU, t, 32.6, 34.7, 0.04), emre="G_soft", rope="fbheart")),
    S(34.7, 37.4, plate(lambda t: ins9.deniz_chest(beat(t, 36.1)), 34.7, 37.4, 1.0, 1.06)),
    S(37.4, 41.0, lambda t: shop(t, push(USTA_MCU, t, 37.4, 41.0, 0.04), usta="E_proud", rope="none", bg_blur=8, deniz_blur=6, usta_blinks=False)),
    S(41.0, 45.4, plate(lambda t: _ticket(round(min(1, max(0, (t - 41.2) / 3.0)) * 60) / 60, round(min(1, max(0, (t - 44.6) / 0.35)) * 8) / 8), 41.0, 45.4, 1.04, 1.0)),
    S(45.4, 48.0, plate(lambda t: _cta(), 45.4, 48.0, 1.0, 1.0)),
]


def frame_at(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            img = fn(t)
            break
    else:
        img = Image.new("RGB", (W, H))
    img = finish(img, t, dust=False, grain=False)
    if t < 41.0:
        img = subtitle(img, sub_at(t))
    if t > TOTAL - 0.6:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.6: int(v * max(k, 0)))
    if 45.1 <= t < 45.7:
        k = abs(t - 45.4) / 0.3
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
    add(f"{SFX}/boya_kutusu.mp3", 0.8, 0.5)
    add(f"{SFX}/steteskop.mp3", 11.3, 0.7)
    add(f"{SFX}/kalp_zayif.mp3", 13.1, 1.0)
    add(f"{SFX}/kalp_guclu.mp3", 19.2, 1.0, ",afade=t=out:st=3.4:d=0.6")
    add(f"{SFX}/kalp_guclu.mp3", 21.6, 0.25, ",atrim=0:2.0,afade=t=out:st=1.4:d=0.6")
    add(f"{SFX}/cingirak_cikis.mp3", 34.9, 0.35)
    add(f"{SFX}/steteskop.mp3", 34.8, 0.6)
    add(f"{SFX}/kalp_guclu.mp3", 36.1, 0.9, ",atrim=0:1.6,afade=t=out:st=1.1:d=0.5")
    add(f"{SFX}/kalem.mp3", 41.2, 0.7, ",atrim=0:3.0,afade=t=out:st=2.6:d=0.4")
    add(f"{SFX}/damga.mp3", 44.6, 0.8)
    add(f"{SFX}/muzik.mp3", 23.7, 0.26, f",afade=t=in:st=0:d=2.5,afade=t=out:st={TOTAL - 23.7 - 3.0}:d=3.0")
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
