"""Bölüm 13 — "Severek Ayrılınır mı?" (~50 sn). Zamanlama ses dosyalarından otomatik hesaplanır."""
import sys, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum13")
from PIL import Image, ImageDraw
from engine import W, H, UI, FPS, ROOT, finish, subtitle, envelope, duration, smooth, font, FONT_SERIF_B
import scenes3d as s3
from scenes3d import (shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU,
                      USTA_BACK_OTS, loupe_in, loupe_out)
from scenes import split_sub, plate
import inserts as ins
import inserts_foto as ifo

REP = f"{ROOT}/bolum13/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = customer), subtitle (None = text on screen)
    ("01_N", "E", "Usta, severek ayrılınır mı? Hâlâ seviyorum… ama ayrıldık."),
    ("02_D", "D", "Seviyorsanız niye ayrılıyorsunuz abla?"),
    ("03_U", "U", "Deniz."),
    ("04_U", "U", "Dur, bir bakalım…"),
    ("f05_U", "U", "Fotoğrafta bile uzaksınız…"),
    ("f07a_U", "U", "Fotoğraf bozuk değil kızım. Bak… ikiniz de giderken dönüp bakmışsınız."),
    ("f07b_U", "U", "Severek ayrılmak, giderken dönüp bakmaktır."),
    ("f08_N", "E", "Bu fotoğrafı saklayayım usta. Dönüp baktığımızı unutmamak için."),
    ("09_D", "D", "Ben yine de ayrılınmaz diyorum."),
    ("03_U", "U", "Deniz."),
]
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
SUBTIMES = {5: [(0.0, 1.6, "Fotoğraf bozuk değil kızım."), (1.6, 4.0, "Bak… ikiniz de giderken"), (4.0, 5.6, "dönüp bakmışsınız.")]}

T, START = {}, {}
START[0] = 0.4
T["wide"] = (0.0, max(4.3, START[0] + DUR[0] + 0.15)); t = T["wide"][1]
START[1] = t + 0.05; T["deniz"] = (t, START[1] + DUR[1] + 0.15); t = T["deniz"][1]
START[2] = t + 0.1; T["tepki"] = (t, START[2] + DUR[2] + 0.2); t = T["tepki"][1]
START[3] = t + 0.1; T["bakalim"] = (t, START[3] + DUR[3] + 0.6); T["loupe_in"] = T["bakalim"][1] - 0.55; t = T["bakalim"][1]
START[4] = t + 0.7; T["foto"] = (t, START[4] + DUR[4] + 1.6); t = T["foto"][1]
T["yuz"] = (t, t + 1.5); t = T["yuz"][1]
START[5] = t + 0.3; T["bozuk"] = (t, START[5] + 1.6); t = T["bozuk"][1]
T["donup"] = (t, START[5] + DUR[5] + 1.0); t = T["donup"][1]
S6 = START[5]; GAZE = (S6 + 4.5, S6 + 5.6)
START[6] = t + 0.2; T["cevap"] = (t, START[6] + DUR[6] + 0.4); t = T["cevap"][1]
START[7] = t + 0.15; T["final"] = (t, START[7] + DUR[7] + 0.8); t = T["final"][1]
T_TICKET = t; T_CTA = t + 4.0; T_END = T_CTA + 2.4
START[8] = T_END + 0.2; START[9] = START[8] + DUR[8] + 0.15
TOTAL = round(START[9] + DUR[9] + 0.4, 2)
FIELDS = (("Arıza:", "\"Severek ayrıldık.\""),
          ("Yapılan işlem:", "Fotoğrafa büyüteçle bakıldı."),
          ("Not:", "Severek ayrılmak, giderken dönüp bakmaktır."))

def k01(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["E"] = []
s3.BLINKS["U"] = [2.4, T["cevap"][0] + 1.6]
s3.BLINKS["D"] = [1.8, T["deniz"][0] + 1.2, START[8] + 0.7]


def sub_at(t):
    for i, (f, s, txt) in enumerate(LINES):
        if txt and START[i] - 0.05 <= t < START[i] + DUR[i] + 0.2:
            if i in SUBTIMES:
                for a, b, p in SUBTIMES[i]:
                    if t - START[i] < b:
                        return p
                return SUBTIMES[i][-1][2]
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
def _ticket(progress, stamp):
    return ins.ticket(progress, stamp, "013", FIELDS, "DÖNÜP BAKILDI")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Hâlâ aklından çıkmayan", "birine gönder."), "Eşref Usta · Bölüm 13")


def S(t0, t1, fn):
    return (t0, t1, fn)


def crop(img, cx, cy, z):
    cw, chh = 1440 / z, 2560 / z
    x0 = min(max(cx - cw / 2, 0), 1440 - cw); y0 = min(max(cy - chh / 2, 0), 2560 - chh)
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + chh))).resize((W, H), Image.LANCZOS)


def shot_open(t):
    return shop(t, push(WIDE, t, 0, T["wide"][1], 0.04), deniz="D_phone", rope="photo" if t >= 1.1 else "none",
                emre_back=(120 - 220 * (1 - smooth(min(1.0, t / 1.0))), 560, 0.95, 5, "N_back", 0.85))


def shot_bakalim(t):
    t0, t1 = T["bakalim"]
    p = loupe_in(t, T["loupe_in"])
    cam = push(USTA_CU, t, t0, t1, 0.06)
    if p is None:
        return shop(t, cam, usta="E_serious", rope="photo", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="photo", bg_blur=9, deniz_blur=8, usta_blinks=False)


def keycam(t, keys):
    """keys: [(time, photo_x, photo_y, zoom)], smooth glide between consecutive keys."""
    if t <= keys[0][0]:
        k = keys[0]
    elif t >= keys[-1][0]:
        k = keys[-1]
    else:
        for k0, k1 in zip(keys, keys[1:]):
            if k0[0] <= t < k1[0]:
                u = smooth((t - k0[0]) / (k1[0] - k0[0]))
                k = tuple(k0[j] + (k1[j] - k0[j]) * u for j in range(4))
                break
    cx, cy = ifo.photo_point(k[1], k[2])
    return cx, cy, k[3]


WHOLE = (600, 390, 1.12)


def shot_foto(t):
    t0, t1 = T["foto"]
    img = ifo.photo_plate()
    return crop(img, *keycam(t, [(t0, *WHOLE), (t1, 600, 380, 1.3)]))


def shot_bozuk(t):
    t0, t1 = T["bozuk"]
    p = loupe_out(t, t0 + 0.05)
    cam = push(USTA_CU, t, t0, t1, 0.08)
    if p is None:
        return shop(t, cam, usta="E_soft", rope="photo", bg_blur=9, deniz_blur=8, usta_blinks=False)
    return shop(t, cam, usta=p, usta_mouth=0, rope="photo", bg_blur=9, deniz_blur=8)


def shot_donup(t):
    gq = int(round(smooth(k01(t, *GAZE)) * 20))
    img = ifo.photo_plate(gq)
    t0, t1 = T["donup"]
    keys = [(t0, *WHOLE), (S6 + 2.6, *WHOLE), (S6 + 3.4, 268, 330, 2.5), (S6 + 3.95, 268, 330, 2.5),
            (S6 + 4.5, 932, 330, 2.5), (S6 + 4.8, 932, 330, 2.5), (S6 + 5.8, 600, 380, 1.25), (t1, 600, 380, 1.3)]
    return crop(img, *keycam(t, keys))


def shot_cevap(t):
    return shop(t, push(USTA_CU, t, *T["cevap"], 0.08), usta="E_soft", rope="photo", bg_blur=9, deniz_blur=8)


@functools.lru_cache(None)
def _tag():
    w, h = int(940 * UI / 1.5), int(230 * UI / 1.5)
    tag = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(tag)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=int(24 * UI / 1.5), fill=(246, 234, 205, 240), outline=(176, 36, 36, 255), width=int(6 * UI / 1.5))
    f1 = font(FONT_SERIF_B, int(48 * UI / 1.5)); f2 = font(FONT_SERIF_B, int(36 * UI / 1.5))
    for txt, f, y, c in (("SİZCE SEVEREK AYRILINIR MI?", f1, 0.17, (40, 26, 16, 255)), ("Yorumlara yaz", f2, 0.6, (150, 30, 30, 255))):
        tw = d.textlength(txt, font=f); d.text(((w - tw) / 2, h * y), txt, font=f, fill=c)
    return tag.rotate(-2, expand=True, resample=Image.BICUBIC)


def shot_stinger(t):
    img = shop(t, push((s3.DENIZ_X - 30, 1450, 740), t, T_END, TOTAL, 0.05), deniz="D_whisper", rope="none", deniz_blur=0, bg_blur=8, usta_blur=6)
    k = smooth(k01(t, T_END + 0.3, T_END + 0.8))
    if k > 0:
        tg = _tag().copy()
        if k < 1:
            tg.putalpha(tg.split()[3].point(lambda v: int(v * k)))
        img.alpha_composite(tg, ((W - tg.size[0]) // 2, int(H * 0.115 - 40 * (1 - k) * UI)))
    return img


SHOTS = [
    S(*T["wide"], shot_open),
    S(*T["deniz"], lambda t: shop(t, push(DENIZ_MCU, t, *T["deniz"]), deniz="D_sincere", rope="photo", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(*T["tepki"], lambda t: shop(t, push(USTA_MCU, t, *T["tepki"]), usta="E_side", deniz="D_sincere", rope="photo", bg_blur=8, deniz_blur=6)),
    S(*T["bakalim"], shot_bakalim),
    S(*T["foto"], shot_foto),
    S(*T["yuz"], lambda t: door(t, push(EMRE_CU, t, *T["yuz"], 0.05), emre="N_sad", rope="photo", emre_mouth=0.0)),
    S(*T["bozuk"], shot_bozuk),
    S(*T["donup"], shot_donup),
    S(*T["cevap"], shot_cevap),
    S(*T["final"], lambda t: door(t, push(EMRE_CU, t, *T["final"], 0.05), emre="N_soft", rope="none")),
    S(T_TICKET, T_CTA, plate(lambda t: _ticket(round(k01(t, T_TICKET + 0.2, T_TICKET + 2.7) * 60) / 60, round(k01(t, T_CTA - 0.75, T_CTA - 0.4) * 8) / 8), T_TICKET, T_CTA, 1.04, 1.0)),
    S(T_CTA, T_END, plate(lambda t: _cta(), T_CTA, T_END, 1.0, 1.0)),
    S(T_END, TOTAL, shot_stinger),
]


def frame_at(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            img = fn(t)
            break
    else:
        img = Image.new("RGB", (W, H))
    img = finish(img, t, dust=False, grain=False)
    if t < T_TICKET or t >= T_END:
        img = subtitle(img, sub_at(t), 0.62 if t < T["wide"][1] else 0.705)
    if t > TOTAL - 0.5:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.5: int(v * max(k, 0)))
    for tc in (T_CTA, T_END):
        if tc - 0.3 <= t < tc + 0.3:
            k = abs(t - tc) / 0.3
            img = Image.eval(img, lambda v, k=k: int(v * min(1, k)))
    return img


def audio_mix(out):
    inputs, filters, labels = [], [], []
    def add(path, at, vol=1.0, extra=""):
        idx = len(inputs) // 2; inputs.extend(["-i", path])
        ms = int(at * 1000)
        filters.append(f"[{idx}:a]aresample=44100,aformat=channel_layouts=stereo{extra},volume={vol},adelay={ms}|{ms}[a{idx}]")
        labels.append(f"[a{idx}]")
    for i, (f, sp, _) in enumerate(LINES):
        add(f"{REP}/{f}.mp3", START[i], 1.05 if sp == "E" else 1.0)
    add(f"{SFX}/ortam.mp3", 0.0, 0.32, f",aloop=loop=4:size=2e6,atrim=0:{TOTAL},afade=t=out:st={TOTAL - 3}:d=2.5")
    add(f"{SFX}/cingirak.mp3", 0.0, 0.35, ",atrim=0:1.0,afade=t=out:st=0.3:d=0.7")   # short bell, fades before the hook
    add(f"{SFX}/kagit_birakma.mp3", 1.05, 0.6)
    add(f"{SFX}/loupe.mp3", T["loupe_in"], 0.5)
    add(f"{SFX}/tin.mp3", GAZE[0], 0.45)
    add(f"{SFX}/cingirak_cikis.mp3", START[7] + DUR[7] + 0.3, 0.35)
    add(f"{SFX}/kalem.mp3", T_TICKET + 0.2, 0.7, ",atrim=0:2.5,afade=t=out:st=2.1:d=0.4")
    add(f"{SFX}/damga.mp3", T_CTA - 0.75, 0.8)
    m0 = T["foto"][0] + 1.0
    add(f"{SFX}/muzik.mp3", m0, 0.26, f",afade=t=in:st=0:d=2.5,afade=t=out:st={T_END - m0 - 1.5}:d=1.5")
    fc = ";".join(filters) + ";" + "".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{TOTAL},alimiter=limit=0.95[out]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-c:a", "pcm_s16le", out], check=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        for tt in sys.argv[3:]:
            frame_at(float(tt)).convert("RGB").save(f"{sys.argv[2]}/still_{float(tt):05.1f}.jpg", quality=88)
    elif mode == "video":
        out, a, b = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for n in range(int(round(a * FPS)), int(round(b * FPS))):
            p.stdin.write(frame_at(n / FPS).convert("RGB").tobytes())
        p.stdin.close(); p.wait()
    elif mode == "audio":
        audio_mix(sys.argv[2])
