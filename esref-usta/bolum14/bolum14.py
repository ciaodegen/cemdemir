"""Bölüm 14 — "Borç Geri İstenir mi?" (~32 sn). Yeni formül: ilk karede yüz + soru, giriş sahnesi yok, son söz izleyicide."""
import sys, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum14")
from PIL import Image, ImageDraw
from engine import W, H, UI, FPS, ROOT, finish, subtitle, envelope, duration, smooth, font, FONT_SERIF_B
import scenes3d as s3
from scenes3d import shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_CU, loupe_in, loupe_out
from scenes import split_sub
import inserts_pecete as ipc

REP = f"{ROOT}/bolum14/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = customer), subtitle
    ("01_T", "E", "Usta, borç verdiğim parayı geri istemek ayıp mı?"),
    ("02_T", "E", "En yakın arkadaşım. Sekiz ay oldu… dün tatil fotoğrafı attı."),
    ("03_D", "D", "Fotoğrafı beğendin mi bari abi?"),
    ("04_U", "U", "Deniz."),
    ("05_U", "U", "Dur, bir bakalım…"),
    ("06_U", "U", "Bu kâğıtta sadece para yazmıyor evladım… söz yazıyor."),
    ("07_U", "U", "Geri istemek ayıp değil. Ayıp olan… istetmektir."),
    ("08_T", "E", "O zaman bu videoyu ona atıyorum usta."),
    ("09_D", "D", "Ben olsam istemezdim abi, arkadaşlık bozulur."),
    ("04_U", "U", "Deniz."),
]
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
SUBTIMES = {5: [(0.0, 2.6, "Bu kâğıtta sadece para yazmıyor evladım…"), (2.6, 4.2, "…söz yazıyor.")],
            6: [(0.0, 1.75, "Geri istemek ayıp değil."), (1.75, 4.3, "Ayıp olan… istetmektir.")]}

T, START = {}, {}
START[0] = 0.12; T["hook"] = (0.0, START[0] + DUR[0] + 0.25); t = T["hook"][1]
START[1] = t + 0.35; T["wide"] = (t, START[1] + DUR[1] + 0.2); PUT = t + 0.25; t = T["wide"][1]
START[2] = t + 0.05; T["deniz"] = (t, START[2] + DUR[2] + 0.15); t = T["deniz"][1]
START[3] = t + 0.1; T["tepki"] = (t, START[3] + DUR[3] + 0.2); t = T["tepki"][1]
START[4] = t + 0.1; T["bakalim"] = (t, START[4] + DUR[4] + 0.6); T["loupe_in"] = T["bakalim"][1] - 0.55; t = T["bakalim"][1]
START[5] = t + 0.5; T["pecete"] = (t, START[5] + DUR[5] + 0.8); t = T["pecete"][1]
S5 = START[5]; GLOW = (S5 + 2.85, S5 + 3.5)
T["yuz"] = (t, t + 1.0); t = T["yuz"][1]
START[6] = t + 0.3; T["cevap"] = (t, START[6] + DUR[6] + 0.45); t = T["cevap"][1]
START[7] = t + 0.15; T["final"] = (t, START[7] + DUR[7] + 0.7); t = T["final"][1]
T_END = t
START[8] = T_END + 0.25; START[9] = START[8] + DUR[8] + 0.15
TOTAL = round(START[9] + DUR[9] + 1.6, 2)


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
s3.BLINKS["E"] = [1.9, T["final"][0] + 1.2]
s3.BLINKS["U"] = [T["tepki"][0] + 0.9, T["cevap"][0] + 2.2]
s3.BLINKS["D"] = [T["deniz"][0] + 1.1, START[8] + 0.9]


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


def S(t0, t1, fn):
    return (t0, t1, fn)


def crop(img, cx, cy, z):
    cw, chh = 1440 / z, 2560 / z
    x0 = min(max(cx - cw / 2, 0), 1440 - cw); y0 = min(max(cy - chh / 2, 0), 2560 - chh)
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + chh))).resize((W, H), Image.LANCZOS)


def keycam(t, keys):
    """keys: [(time, napkin_x, napkin_y, zoom)], smooth glide between consecutive keys."""
    k = keys[0] if t <= keys[0][0] else keys[-1]
    for k0, k1 in zip(keys, keys[1:]):
        if k0[0] <= t < k1[0]:
            u = smooth((t - k0[0]) / (k1[0] - k0[0]))
            k = tuple(k0[j] + (k1[j] - k0[j]) * u for j in range(4))
            break
    cx, cy = ipc.napkin_point(k[1], k[2])
    return cx, cy, k[3]


@functools.lru_cache(None)
def _banner(l1, l2, sub=None):
    s = UI / 1.5
    f1 = font(FONT_SERIF_B, int(58 * s)); f2 = font(FONT_SERIF_B, int(36 * s))
    tmp = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    w = int(max(tmp.textlength(l1, font=f1), tmp.textlength(l2, font=f1)) + 90 * s)
    h = int((170 + (54 if sub else 0)) * s)
    tag = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(tag)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=int(24 * s), fill=(246, 234, 205, 245), outline=(176, 36, 36, 255), width=int(6 * s))
    for txt, f, y, c in ((l1, f1, 18, (40, 26, 16, 255)), (l2, f1, 88, (176, 36, 36, 255))) + (((sub, f2, 160, (150, 30, 30, 255)),) if sub else ()):
        tw = d.textlength(txt, font=f); d.text(((w - tw) / 2, y * s), txt, font=f, fill=c)
    return tag.rotate(-2, expand=True, resample=Image.BICUBIC)


def with_banner(img, tag, y=0.075, k=1.0):
    if k <= 0:
        return img
    tg = tag
    if k < 1:
        tg = tag.copy(); tg.putalpha(tg.split()[3].point(lambda v: int(v * k)))
    img.alpha_composite(tg, ((W - tg.size[0]) // 2, int(H * y - 30 * (1 - k) * UI)))
    return img


HOOK = ("BORÇ VERDİĞİN PARAYI", "GERİ İSTEMEK AYIP MI?")


def shot_hook(t):
    img = door(t, push(EMRE_CU, t, *T["hook"], 0.06), emre="T_ask", rope="napkin")
    return with_banner(img, _banner(*HOOK))


def shot_wide(t):
    img = shop(t, push(WIDE, t, *T["wide"], 0.04), deniz="D_phone", rope="napkin" if t >= PUT else "none",
               emre_back=(120, 560, 0.95, 5, "T_back", 0.85))
    return with_banner(img, _banner(*HOOK), k=1 - k01(t, T["wide"][1] - 0.6, T["wide"][1] - 0.2))


def shot_bakalim(t):
    t0, t1 = T["bakalim"]
    p = loupe_in(t, T["loupe_in"])
    cam = push(USTA_CU, t, t0, t1, 0.06)
    if p is None:
        return shop(t, cam, usta="E_serious", rope="napkin", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="napkin", bg_blur=9, deniz_blur=8, usta_blinks=False)


def shot_pecete(t):
    gq = int(round(smooth(k01(t, *GLOW)) * 20))
    img = ipc.napkin_plate(gq)
    t0, t1 = T["pecete"]
    keys = [(t0, 470, 470, 1.35), (S5, 470, 400, 1.6), (S5 + 2.3, 470, 380, 1.75), (S5 + 3.1, 490, 640, 2.05), (t1, 490, 640, 2.15)]
    return crop(img, *keycam(t, keys))


def shot_cevap(t):
    t0, t1 = T["cevap"]
    p = loupe_out(t, t0 + 0.05)
    cam = push(USTA_CU, t, t0, t1, 0.1)
    if p is None:
        return shop(t, cam, usta="E_soft", rope="napkin", bg_blur=9, deniz_blur=8, usta_blinks=False)
    return shop(t, cam, usta=p, usta_mouth=0, rope="napkin", bg_blur=9, deniz_blur=8)


def shot_stinger(t):
    img = shop(t, push((s3.DENIZ_X - 30, 1450, 740), t, T_END, TOTAL, 0.05), deniz="D_whisper", rope="none", deniz_blur=0, bg_blur=8, usta_blur=6)
    return with_banner(img, _banner("SEN OLSAN", "GERİ İSTER MİSİN?", "Yorumlara yaz"), 0.1, smooth(k01(t, START[8] + 0.4, START[8] + 0.9)))


SHOTS = [
    S(*T["hook"], shot_hook),
    S(*T["wide"], shot_wide),
    S(*T["deniz"], lambda t: shop(t, push(DENIZ_MCU, t, *T["deniz"]), deniz="D_phone", rope="napkin", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(*T["tepki"], lambda t: shop(t, push(USTA_MCU, t, *T["tepki"]), usta="E_side", deniz="D_sincere", rope="napkin", bg_blur=8, deniz_blur=6)),
    S(*T["bakalim"], shot_bakalim),
    S(*T["pecete"], shot_pecete),
    S(*T["yuz"], lambda t: door(t, push(EMRE_CU, t, *T["yuz"], 0.05), emre="T_ask", rope="napkin", emre_mouth=0.0)),
    S(*T["cevap"], shot_cevap),
    S(*T["final"], lambda t: door(t, push(EMRE_CU, t, *T["final"], 0.05), emre="T_smile", rope="none")),
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
    yf = 0.62 if T["wide"][0] <= t < T["wide"][1] else 0.89 if T["pecete"][0] <= t < T["pecete"][1] else 0.705
    img = subtitle(img, sub_at(t), yf)
    if t > TOTAL - 0.4:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.4: int(v * max(k, 0)))
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
    add(f"{SFX}/ortam.mp3", 0.0, 0.3, f",aloop=loop=4:size=2e6,atrim=0:{TOTAL},afade=t=out:st={TOTAL - 2.5}:d=2.2")
    add(f"{SFX}/kagit_birakma.mp3", PUT, 0.6)
    add(f"{SFX}/loupe.mp3", T["loupe_in"], 0.5)
    add(f"{SFX}/tin.mp3", GLOW[0], 0.45)
    add(f"{SFX}/cingirak_cikis.mp3", START[7] + DUR[7] + 0.25, 0.35)
    m0 = T["pecete"][0]
    add(f"{SFX}/muzik.mp3", m0, 0.24, f",afade=t=in:st=0:d=2.0,afade=t=out:st={T_END - m0 - 1.2}:d=1.2")
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
