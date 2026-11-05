"""Bölüm 11 — "Bir Kupon Daha" (kumar bağımlılığı, ~48 sn). Zamanlama ses dosyalarından otomatik hesaplanır."""
import sys, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum11")
from PIL import Image, ImageDraw
from engine import W, H, UI, FPS, ROOT, finish, subtitle, envelope, duration, smooth, font, FONT_SERIF_B, FONT_BOLD
import scenes3d as s3
from scenes3d import (shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU,
                      USTA_BACK_OTS, loupe_in, loupe_out)
from scenes import split_sub, plate
import inserts as ins
import inserts_kupon as ik

REP = f"{ROOT}/bolum11/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = customer), subtitle (None = text on screen)
    ("01_P", "E", "Usta, kumar bağımlılık mı, şanssızlık mı? Bir kupon daha tutsa her şey düzelecek!"),
    ("02_D", "D", "Abi kaç maç tutturdun?"),
    ("03_U", "U", "Deniz."),
    ("04_U", "U", "Dur, bir bakalım…"),
    ("05_U", "U", None),
    ("06_U", "U", "Bu sonuncusu boş. Maç: Kendin."),
    ("07_U", "U", "Bu şanssızlık değil evlat, hastalık. Ama bu son maçı hâlâ kazanabilirsin. Tek başına değil."),
    ("08_P", "E", "Alo… yardım almak istiyorum."),
]
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
# inside 05_U: (text start, text end, 'kaybetti' start) per coupon
READ = [(0.0, 2.23, 2.69), (3.49, 5.01, 5.77), (6.77, 8.50, 9.08), (9.86, 10.79, 11.61)]
SEG06 = {"bos": (0.0, 1.43), "mac": (1.66, 2.05), "kendin": (2.66, 3.21)}

T, START = {}, {}
START[0] = 0.4
T["wide"] = (0.0, max(4.3, START[0] + DUR[0] + 0.15)); t = T["wide"][1]
START[1] = t + 0.05; T["deniz"] = (t, START[1] + DUR[1] + 0.15); t = T["deniz"][1]
START[2] = t + 0.1; T["tepki"] = (t, START[2] + DUR[2] + 0.3); t = T["tepki"][1]
START[3] = t + 0.1; T["bakalim"] = (t, START[3] + DUR[3] + 0.6); T["loupe_in"] = T["bakalim"][1] - 0.55; t = T["bakalim"][1]
DROP_T = tuple(round(t + 0.1 + 0.35 * i, 2) for i in range(4))
START[4] = t + 1.6; T["kuponlar"] = (t, START[4] + DUR[4] + 0.7); t = T["kuponlar"][1]
T["yuz"] = (t, t + 1.3); t = T["yuz"][1]
START[5] = t + 0.5; T["son"] = (t, START[5] + DUR[5] + 0.6); t = T["son"][1]
START[6] = t + 0.35; T["cevap"] = (t, START[6] + DUR[6] + 0.3); t = T["cevap"][1]
T["yazma"] = (t, t + 3.6); t = T["yazma"][1]
START[7] = t + 1.3; T["arama"] = (t, START[7] + DUR[7] + 0.8); t = T["arama"][1]
T_TICKET = t; T_CTA = t + 4.0
TOTAL = round(T_CTA + 3.6, 2)
S4, S5 = START[4], START[5]
FIELDS = (("Arıza:", "\"Bir kupon daha.\""),
          ("Yapılan işlem:", "Yardım istendi."),
          ("Not:", "Son maçı tek başına oynama."))


def chars_at(t):
    out, st = [], []
    for i, (a, b, kb) in enumerate(READ):
        l1, l2, _ = ik.COUPONS[i]
        n = len(l1) + len(l2)
        a += S4; b += S4; kb += S4
        out.append(n if t >= b else (0 if t < a else int(n * (t - a) / (b - a))))
        st.append(0 if t < kb else int(round(min(1.0, (t - kb) / 0.18) * 10)))
    return tuple(out), tuple(st)


def focus(t):
    for i in (3, 2, 1, 0):
        if t >= S4 + READ[i][0] - 0.35:
            return i
    return None


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["E"] = []
s3.BLINKS["U"] = [2.4, T["cevap"][0] + 2.4]
s3.BLINKS["D"] = [1.8]


def sub_at(t):
    for i, (f, s, txt) in enumerate(LINES):
        if txt and START[i] - 0.05 <= t < START[i] + DUR[i] + 0.2:
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
    return ins.ticket(progress, stamp, "011", FIELDS, "İLK ADIM ATILDI")


@functools.lru_cache(None)
def _cta():
    img = ins.cta(("“Bir kupon daha” diyen", "birine gönder."), "Eşref Usta · Bölüm 11")
    d = ImageDraw.Draw(img)
    box = (220, 1720, 1220, 1960)
    d.rounded_rectangle(box, radius=40, outline=(120, 180, 120, 255), width=6, fill=(22, 30, 22, 255))
    f1 = font(FONT_BOLD, 76); f2 = font(FONT_BOLD, 42)
    t1 = "Yeşilay 115"; t2 = "Ücretsiz ve gizli destek"
    d.text(((1440 - d.textlength(t1, font=f1)) / 2, 1752), t1, font=f1, fill=(200, 236, 200, 255))
    d.text(((1440 - d.textlength(t2, font=f2)) / 2, 1862), t2, font=f2, fill=(170, 210, 170, 255))
    return img


def S(t0, t1, fn):
    return (t0, t1, fn)


def k01(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def shot_open(t):
    return shop(t, push(WIDE, t, 0, T["wide"][1], 0.04), deniz="D_phone", rope="coupons" if t >= 1.1 else "none",
                emre_back=(120 - 220 * (1 - smooth(min(1.0, t / 1.0))), 560, 0.95, 5, "P_back", 0.85))


def shot_bakalim(t):
    t0, t1 = T["bakalim"]
    p = loupe_in(t, T["loupe_in"])
    cam = push(USTA_CU, t, t0, t1, 0.06)
    if p is None:
        return shop(t, cam, usta="E_serious", rope="coupons", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="coupons", bg_blur=9, deniz_blur=8, usta_blinks=False)


def shot_coupons(t):
    n = sum(1 for tt in DROP_T if t >= tt)
    ch, st = chars_at(t)
    img = ik.coupons_plate(n, ch, st)
    over = (720, 1280, 1.06)
    f = focus(t)
    if f is None:
        prev = tgt = over; tf = T["kuponlar"][0]
    else:
        x, y, _ = ik.SPOTS[f]; tgt = (x, y + 30, 1.3)
        tf = S4 + READ[f][0] - 0.35
        prev = over if f == 0 else (ik.SPOTS[f - 1][0], ik.SPOTS[f - 1][1] + 30, 1.3)
    k = smooth(min(1.0, max(0.0, (t - tf) / 0.45)))
    cx = prev[0] + (tgt[0] - prev[0]) * k; cy = prev[1] + (tgt[1] - prev[1]) * k; z = prev[2] + (tgt[2] - prev[2]) * k
    cw, chh = 1440 / z, 2560 / z
    x0 = min(max(cx - cw / 2, 0), 1440 - cw); y0 = min(max(cy - chh / 2, 0), 2560 - chh)
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + chh))).resize((W, H), Image.LANCZOS)


def shot_son(t):
    rev = 0
    if t >= S5 + SEG06["kendin"][0]:
        rev = 1
    if t >= S5 + SEG06["kendin"][1] + 0.15:
        rev = 2
    return ik.last_plate("front", rev)


def shot_cevap(t):
    t0, t1 = T["cevap"]
    p = loupe_out(t, t0 + 0.05)
    cam = push(USTA_CU, t, t0, t1, 0.1)
    if p is None:
        return shop(t, cam, usta="E_soft", rope="coupons", bg_blur=9, deniz_blur=8, usta_blinks=False)
    return shop(t, cam, usta=p, usta_mouth=0, rope="coupons", bg_blur=9, deniz_blur=8)


SUB115 = "Yeşilay · ücretsiz ve gizli"


def shot_yazma(t):
    t0, t1 = T["yazma"]
    if t < t0 + 0.4:
        return ik.last_plate("flip", 2, int(round(k01(t, t0, t0 + 0.4) * 20)))
    n = int(round((3 + len(SUB115)) * k01(t, t0 + 0.55, t0 + 2.9)))
    return ik.last_plate("back", 2, 20, n, t < t0 + 3.0)


SHOTS = [
    S(*T["wide"], shot_open),
    S(*T["deniz"], lambda t: shop(t, push(DENIZ_MCU, t, *T["deniz"]), deniz="D_sincere", rope="coupons", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(*T["tepki"], lambda t: shop(t, push(USTA_MCU, t, *T["tepki"]), usta="E_serious", deniz="D_listen", rope="coupons", bg_blur=8, deniz_blur=6)),
    S(*T["bakalim"], shot_bakalim),
    S(*T["kuponlar"], shot_coupons),
    S(*T["yuz"], lambda t: door(t, push(EMRE_CU, t, *T["yuz"], 0.05), emre="P_sad", rope="coupons", emre_mouth=0.0)),
    S(*T["son"], plate(shot_son, *T["son"], 1.05, 1.14, 0.5, 0.44)),
    S(*T["cevap"], shot_cevap),
    S(*T["yazma"], plate(shot_yazma, *T["yazma"], 1.08, 1.16, 0.5, 0.44)),
    S(*T["arama"], lambda t: door(t, push(EMRE_MCU, t, *T["arama"], 0.06), emre="P_call", rope="none")),
    S(T_TICKET, T_CTA, plate(lambda t: _ticket(round(k01(t, T_TICKET + 0.2, T_TICKET + 2.7) * 60) / 60, round(k01(t, T_CTA - 0.75, T_CTA - 0.4) * 8) / 8), T_TICKET, T_CTA, 1.04, 1.0)),
    S(T_CTA, TOTAL, plate(lambda t: _cta(), T_CTA, TOTAL, 1.0, 1.0)),
]


def frame_at(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            img = fn(t)
            break
    else:
        img = Image.new("RGB", (W, H))
    img = finish(img, t, dust=False, grain=False)
    if t < T_TICKET:
        img = subtitle(img, sub_at(t), 0.62 if t < T["wide"][1] else 0.705)
    if t > TOTAL - 0.7:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.7: int(v * max(k, 0)))
    if T_CTA - 0.3 <= t < T_CTA + 0.3:
        k = abs(t - T_CTA) / 0.3
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
        add(f"{REP}/{f}.mp3", START[i], 1.1 if sp == "E" else 1.0)
    add(f"{SFX}/ortam.mp3", 0.0, 0.32, f",aloop=loop=4:size=2e6,atrim=0:{TOTAL},afade=t=out:st={TOTAL - 3}:d=2.5")
    add(f"{SFX}/cingirak.mp3", 0.0, 0.6)
    add(f"{SFX}/kupon_deste.mp3", 1.0, 0.8)
    add(f"{SFX}/loupe.mp3", T["loupe_in"], 0.5)
    for tt in DROP_T:
        add(f"{SFX}/kagit_birakma.mp3", tt - 0.05, 0.6)
    for (a, b, kb) in READ:
        add(f"{SFX}/damga.mp3", S4 + kb, 0.55)
    add(f"{SFX}/kagit_acma.mp3", T["yazma"][0], 0.6)
    add(f"{SFX}/kalem.mp3", T["yazma"][0] + 0.55, 0.5, ",atrim=0:2.35,afade=t=out:st=2.0:d=0.35")
    add(f"{SFX}/telefon_tus.mp3", T["arama"][0] + 0.05, 0.6, ",atrim=0:1.25,afade=t=out:st=1.0:d=0.25")
    add(f"{SFX}/kalem.mp3", T_TICKET + 0.2, 0.7, ",atrim=0:2.5,afade=t=out:st=2.1:d=0.4")
    add(f"{SFX}/damga.mp3", T_CTA - 0.75, 0.8)
    m0 = T["kuponlar"][0]
    add(f"{SFX}/muzik.mp3", m0, 0.22, f",afade=t=in:st=0:d=3.0,afade=t=out:st={TOTAL - m0 - 2.5}:d=2.5")
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
