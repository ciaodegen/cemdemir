"""Eşref Usta'ya Mektup 1 — "Kısalmış Kalem" (KPSS) (~51 sn, sonda yorum çağrısı)."""
import sys, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup_kpss")
from PIL import Image, ImageDraw
from engine import W, H, UI, FPS, ROOT, finish, subtitle, envelope, duration, smooth, font, FONT_SERIF_B
import scenes3d as s3
from scenes3d import shop, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU
from scenes import split_sub, plate
import inserts as ins
import inserts_m1 as im
import inserts_kpss as ik

REP = f"{ROOT}/mektup_kpss/replikler_hizli"
SFX = f"{ROOT}/efektler"
GRAPHITE = (66, 66, 74, 255)

LINES = [  # file, speaker, subtitle (None = text on paper)
    ("01_D", "D", "Usta, KPSS'ymiş! Ben ehliyeti üçüncüde geçtim, ona bile ağladım!"),
    ("02_U", "U", "Deniz."),
    ("03_U", "U", "Dur, bir bakalım…"),
    ("04_U", "U", None),
    ("06_U", "U", "Dört yıldır aynı kapıya yürüyorsun evlat. Bak… kalem kısalmış. Ama kırılmamış."),
    ("07_U", "U", "Yorulmak bozulmak değil."),
    ("08_U", "U", "O kapı açıldığında, bu yolun hiçbir adımı boşa gitmemiş olacak."),
    ("09_U", "U", "Senin arızan ne? Yorumlara yaz. En çok beğenileni ben tamir edeceğim."),
]
START = {0: 3.75, 1: 8.4, 2: 9.7, 3: 12.0, 4: 22.3, 5: 29.0, 6: 34.05, 7: 45.8}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
SUB_END = {5: 30.7}     # 07_U: only the first sentence is a subtitle; the rest is written on paper
T_TICKET, T_CTA, T_END = 39.6, 43.4, 45.6
TOTAL = 51.4
FIELDS = (("Arıza:", "4 yıldır atanamamak. Yorgunluk."),
          ("Yapılan işlem:", "Kalem açıldı."),
          ("Not:", "Kısaldın ama kırılmadın."))

LETTER = (("Eşref Usta,", 0), ("2022'den beri KPSS'ye", 1), ("giriyorum.", 1),
          ("Artık atanmak istiyorum.", 2), ("Çok yoruldum.", 2), ("— Bir takipçin", 3))
REPLY = (("Kalem kısalmış,", 0), ("ama kırılmamış.", 0), ("Yorulmak bozulmak değil.", 0),
         ("Biraz dinlen,", 1), ("sonra yine yaz.", 2))
LETTER_SEG = [(0, 12.0, 12.97), (1, 13.8, 15.65), (2, 15.65, 16.4), (3, 17.22, 18.45), (4, 18.45, 19.16), (5, 19.1, 19.3)]
REPLY_SEG = [(0, 0, .01), (1, 0, .01), (2, 0, .01), (3, 31.25, 32.02), (4, 32.59, 33.62)]


def reveal(t, segs, lines):
    out = []
    for (i, a, b) in segs:
        n = len(lines[i][0])
        out.append(n if t >= b else (0 if t < a else int(n * (t - a) / (b - a))))
    return tuple(out)


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["U"] = [2.9, 11.9, 23.4, 36.2, 47.6, 50.2]
s3.BLINKS["D"] = [3.0, 6.6]


def sub_at(t):
    for i, (f, s, txt) in enumerate(LINES):
        end = SUB_END.get(i, START[i] + DUR[i] + 0.2)
        if txt and START[i] - 0.05 <= t < end:
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
    return ins.ticket(progress, stamp, "M-01", FIELDS, "DEVAM")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Yıllardır atanmayı", "bekleyen birine gönder."), "Eşref Usta'ya Mektup · 1")


def S(t0, t1, fn):
    return (t0, t1, fn)


def k01(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def q20(x):
    return int(round(x * 20))


@functools.lru_cache(None)
def _tag():
    w, h = int(940 * UI / 1.5), int(230 * UI / 1.5)
    tag = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(tag)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=int(24 * UI / 1.5), fill=(246, 234, 205, 240), outline=(176, 36, 36, 255), width=int(6 * UI / 1.5))
    f1 = font(FONT_SERIF_B, int(56 * UI / 1.5)); f2 = font(FONT_SERIF_B, int(36 * UI / 1.5))
    for txt, f, y, c in (("ARIZANI YORUMLARA YAZ", f1, 0.17, (40, 26, 16, 255)), ("En çok beğenilen tamir edilecek", f2, 0.6, (150, 30, 30, 255))):
        tw = d.textlength(txt, font=f); d.text(((w - tw) / 2, h * y), txt, font=f, fill=c)
    return tag.rotate(-2, expand=True, resample=Image.BICUBIC)


def shot_end(t):
    img = shop(t, push((650, 1400, 820), t, T_END, TOTAL, 0.05), usta="E_front", rope="none", bg_blur=8, deniz_blur=6)
    k = smooth(k01(t, T_END + 0.3, T_END + 0.8))
    if k > 0:
        tg = _tag().copy()
        if k < 1:
            tg.putalpha(tg.split()[3].point(lambda v: int(v * k)))
        img.alpha_composite(tg, ((W - tg.size[0]) // 2, int(H * 0.115 - 40 * (1 - k) * UI)))
    return img


def slips_n(t):
    return sum(1 for tt in (19.5, 20.1, 20.7, 21.3) if t >= tt)


def sharpen(t):
    if t < 30.65:
        ins_q = q20(smooth(k01(t, 28.85, 29.2)))
        return ik.pencil_plate(0, q20(k01(t, 29.2, 30.6)), True, ins_q)
    out = 1 - smooth(k01(t, 30.65, 30.95))
    if out > 0:
        return ik.pencil_plate(20, 20, True, q20(out))
    return ik.pencil_plate(20, 20, False, 0)


LP, RP = LETTER, REPLY
SHOTS = [
    S(0.0, 2.6, plate(lambda t: ik.envelope_plate(q20(smooth(k01(t, 0.1, 0.8))), q20(smooth(k01(t, 0.9, 1.7)))), 0.0, 2.6, 1.1, 1.18)),
    S(2.6, 3.7, lambda t: shop(t, push(WIDE, t, 2.6, 3.7, 0.03), deniz="D_phone", rope="envelope")),
    S(3.7, 8.3, lambda t: shop(t, push(DENIZ_MCU, t, 3.7, 8.3), deniz="D_phone", rope="envelope", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(8.3, 9.6, lambda t: shop(t, push(USTA_MCU, t, 8.3, 9.6), usta="E_side", deniz="D_phone", rope="envelope", bg_blur=8, deniz_blur=6)),
    S(9.6, 11.8, lambda t: shop(t, push(USTA_CU, t, 9.6, 11.8, 0.05), usta="E_front", rope="envelope", bg_blur=9, deniz_blur=8)),
    S(11.8, 19.4, plate(lambda t: im.letter_plate(reveal(t, LETTER_SEG, LP), LP), 11.8, 19.4, 1.22, 1.3, 0.45, 0.02)),
    S(19.4, 22.2, plate(lambda t: ik.slips_plate(slips_n(t)), 19.4, 22.2, 1.0, 1.06)),
    S(22.2, 24.9, lambda t: shop(t, push(USTA_CU, t, 22.2, 24.9, 0.05), usta="E_soft", rope="envelope", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(24.9, 28.8, plate(lambda t: ik.pencil_plate(0, 0, False, 0, True), 24.9, 28.8, 1.0, 1.16, 0.55, 0.5)),
    S(28.8, 31.2, plate(sharpen, 28.8, 31.2, 1.12, 1.2, 0.45, 0.55)),
    S(31.2, 33.9, plate(lambda t: im.reply_plate(reveal(t, REPLY_SEG, RP), t < 33.7, RP, GRAPHITE, True), 31.2, 33.9, 1.22, 1.28, 0.45, 0.02)),
    S(33.9, T_TICKET, lambda t: shop(t, push(USTA_CU, t, 33.9, T_TICKET, 0.1), usta="E_soft", rope="envelope", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(T_TICKET, T_CTA, plate(lambda t: _ticket(round(k01(t, T_TICKET + 0.2, T_TICKET + 2.7) * 60) / 60, round(k01(t, T_CTA - 0.75, T_CTA - 0.4) * 8) / 8), T_TICKET, T_CTA, 1.04, 1.0)),
    S(T_CTA, T_END, plate(lambda t: _cta(), T_CTA, T_END, 1.0, 1.0)),
    S(T_END, TOTAL, shot_end),
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
        img = subtitle(img, sub_at(t))
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
    for i, (f, _, _) in enumerate(LINES):
        add(f"{REP}/{f}.mp3", START[i], 1.0)
    add(f"{SFX}/ortam.mp3", 0.0, 0.32, f",aloop=loop=4:size=2e6,atrim=0:{TOTAL},afade=t=out:st={TOTAL - 3}:d=2.5")
    add(f"{SFX}/zarf_kayma.mp3", 0.05, 0.8)
    add(f"{SFX}/kalem_yuvarlanma.mp3", 0.9, 0.8)
    add(f"{SFX}/kagit_acma.mp3", 11.75, 0.7)
    for tt in (19.5, 20.1, 20.7, 21.3):
        add(f"{SFX}/kagit_birakma.mp3", tt - 0.05, 0.8)
        add(f"{SFX}/damga.mp3", tt + 0.12, 0.25)
    add(f"{SFX}/kalemtiras.mp3", 29.15, 0.85, ",afade=t=out:st=1.3:d=0.3")
    for (i, a, b) in REPLY_SEG[3:]:
        add(f"{SFX}/kalem.mp3", a, 0.45, f",atrim=0:{b - a:.2f},afade=t=out:st={max(0, b - a - 0.2):.2f}:d=0.2")
    add(f"{SFX}/kalem.mp3", T_TICKET + 0.2, 0.7, ",atrim=0:2.5,afade=t=out:st=2.1:d=0.4")
    add(f"{SFX}/damga.mp3", T_CTA - 0.75, 0.8)
    add(f"{SFX}/muzik.mp3", 11.8, 0.24, f",afade=t=in:st=0:d=3.0,afade=t=out:st={TOTAL - 11.8 - 2.5}:d=2.5")
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
