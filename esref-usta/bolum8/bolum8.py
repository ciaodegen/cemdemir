"""Bölüm 8 — "Hesabı Kim Öder?" (~56 sn)."""
import sys, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum8")
from PIL import Image, ImageDraw
from engine import W, H, UI, FPS, ROOT, finish, subtitle, envelope, duration, smooth, font, FONT_SERIF_B
import scenes3d as s3
from scenes3d import (shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU,
                      USTA_BACK_OTS, loupe_in, loupe_out)
from scenes import split_sub, plate
import inserts as ins
import inserts_hesap as ih

REP = f"{ROOT}/bolum8/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = Burak), subtitle (None = text on screen)
    ("01_B", "E", "Usta, hesabı kadın mı öder, erkek mi? Hep ben ödüyorum, yeter artık! Şunu ikiye böl."),
    ("02_D", "D", "Erkek öder usta! Ben hep ödedim… şimdi bekârım."),
    ("03_U", "U", "Deniz."),
    ("04_U", "U", "Dur, bir bakalım…"),
    ("05_U", "U", "Hm… kesilmiyor."),
    ("06_U", "U", "Bu hesabın bir de arkası var."),
    ("07_U", "U", None),
    ("08_B", "E", "Bunları… hiç saymamıştım."),
    ("09_U", "U", "Bu hesap ikiye bölünmez evlat. Çünkü sevgide kimse kasada durmaz."),
    ("10_B", "E", "Alo, aşkım… nasılsın? Akşam yemekleri benden. Tatlı da senden."),
    ("11_D", "D", "Ben hâlâ erkek öder diyorum."),
    ("03_U", "U", "Deniz."),
]
START = {0: 0.5, 1: 6.65, 2: 10.2, 3: 11.5, 4: 17.35, 5: 19.45, 6: 22.5, 7: 33.4, 8: 35.9, 9: 42.3, 10: 53.0, 11: 54.65}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
T_TICKET, T_CTA, T_END = 46.4, 50.4, 52.8
TOTAL = 56.1
FIELDS = (("Arıza:", "\"Hep ben ödüyorum.\""),
          ("Yapılan işlem:", "Fiş ikiye bölünemedi."),
          ("Not:", "Sevgide kimse kasada durmaz."))
S7 = START[6]
BACK_SEG = [((0, 1), S7, S7 + 3.16), ((3, 4), S7 + 3.51, S7 + 5.81), ((6, 7), S7 + 6.14, S7 + 9.4)]
T_TOTAL_TXT = S7 + 9.4


def back_reveal(t):
    out = [0] * len(ih.BACK)
    for (ids, a, b) in BACK_SEG:
        total = sum(len(ih.BACK[i]) for i in ids)
        n = total if t >= b else (0 if t < a else int(total * (t - a) / (b - a)))
        for i in ids:
            take = min(n, len(ih.BACK[i])); out[i] = take; n -= take
    return tuple(out)


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["E"] = [34.3, 44.9]
s3.BLINKS["U"] = [2.4, 12.4, 21.0, 38.4, 48.0]
s3.BLINKS["D"] = [1.8, 8.0, 54.0]


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
    return ins.ticket(progress, stamp, "008", FIELDS, "BÖLÜNEMEDİ")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Hesap tutmayan", "sevgiline gönder."), "Eşref Usta · Bölüm 8")


def S(t0, t1, fn):
    return (t0, t1, fn)


def k01(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def q(x):
    return int(round(max(0.0, min(1.0, x)) * 20))


def cut_state(t, ts):
    """One scissor cut starting at ts: scissors run up (0.45 s), halves part, then rejoin with a shimmer."""
    sc = k01(t, ts - 0.15, ts + 0.35)
    cut = k01(t, ts - 0.1, ts + 0.35)
    gap = smooth(k01(t, ts + 0.35, ts + 0.6)) * (1 - smooth(k01(t, ts + 0.75, ts + 1.3)))
    glow = max(0.0, 1 - abs(t - (ts + 1.2)) / 0.45) if t > ts + 0.75 else 0.0
    if t > ts + 1.3:
        cut = 0.0
    sc_vis = q(sc) if ts - 0.15 <= t < ts + 0.6 else 0
    opn = q(0.5 + 0.5 * __import__("math").sin(t * 40)) if sc_vis else 0
    return q(cut), q(gap), q(glow), sc_vis, opn


def shot_cut(t):
    ts = 14.3 if t < 15.85 else 15.9
    c, g, gl, sc, op = cut_state(t, ts)
    return ih.bill_plate(20, c, g, gl, sc, op)


def shot_bakalim(t):
    p = loupe_in(t, 13.35)
    cam = push(USTA_CU, t, 11.4, 14.0, 0.06)
    if p is None:
        return shop(t, cam, usta="E_front", rope="receipt", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="receipt", bg_blur=9, deniz_blur=8, usta_blinks=False)


def shot_arkasi(t):
    cam = push(USTA_CU, t, 17.1, 22.0, 0.06)
    if t < 19.2:
        return shop(t, cam, usta="E_loupe", rope="receipt", bg_blur=9, deniz_blur=8, usta_blinks=False)
    p = loupe_out(t, 19.2)
    if p is None:
        return shop(t, cam, usta="E_serious", rope="receipt", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, usta_mouth=0, rope="receipt", bg_blur=9, deniz_blur=8)


def shot_back(t):
    flip = q(k01(t, 22.0, 22.4))
    return ih.back_plate(flip, back_reveal(t), t >= T_TOTAL_TXT)


@functools.lru_cache(None)
def _tag():
    w, h = int(940 * UI / 1.5), int(230 * UI / 1.5)
    tag = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(tag)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=int(24 * UI / 1.5), fill=(246, 234, 205, 240), outline=(176, 36, 36, 255), width=int(6 * UI / 1.5))
    f1 = font(FONT_SERIF_B, int(52 * UI / 1.5)); f2 = font(FONT_SERIF_B, int(36 * UI / 1.5))
    for txt, f, y, c in (("SİZCE HESABI KİM ÖDEMELİ?", f1, 0.17, (40, 26, 16, 255)), ("Yorumlara yaz", f2, 0.6, (150, 30, 30, 255))):
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


def shot_open(t):
    """Usual opening: bell, Burak walks in with his back to us and slaps the receipt on the counter."""
    return shop(t, push(WIDE, t, 0, 5.0, 0.04), deniz="D_phone", rope="receipt" if t >= 1.1 else "none",
                emre_back=(120 - 220 * (1 - smooth(min(1.0, t / 1.0))), 560, 0.95, 5, "B_back", 0.85))


SHOTS = [
    S(0.0, 5.0, shot_open),
    S(5.0, 6.6, plate(lambda t: ih.bill_plate(20), 5.0, 6.6, 1.22, 1.34, 0.5, 0.42)),
    S(6.6, 10.1, lambda t: shop(t, push(DENIZ_MCU, t, 6.6, 10.1), deniz="D_sincere", rope="receipt", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(10.1, 11.4, lambda t: shop(t, push(USTA_MCU, t, 10.1, 11.4), usta="E_side", deniz="D_sincere", rope="receipt", bg_blur=8, deniz_blur=6)),
    S(11.4, 14.0, shot_bakalim),
    S(14.0, 17.1, plate(shot_cut, 14.0, 17.1, 1.25, 1.32, 0.5, 0.42)),
    S(17.1, 22.0, shot_arkasi),
    S(22.0, 33.3, plate(shot_back, 22.0, 33.3, 1.32, 1.44, 0.5, 0.38)),
    S(33.3, 35.8, lambda t: door(t, push(EMRE_CU, t, 33.3, 35.8, 0.04), emre="B_stun", rope="receipt", usta_back=USTA_BACK_OTS)),
    S(35.8, 42.2, lambda t: shop(t, push(USTA_CU, t, 35.8, 42.2, 0.12), usta="E_soft", rope="receipt", bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(42.2, T_TICKET, lambda t: door(t, push(EMRE_MCU, t, 42.2, T_TICKET, 0.06), emre="B_call", rope="none")),
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
        img = subtitle(img, sub_at(t), 0.62 if t < 5.0 else 0.705)
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
        add(f"{REP}/{f}.mp3", START[i], 1.35 if sp == "E" else 1.0)
    add(f"{SFX}/ortam.mp3", 0.0, 0.32, f",aloop=loop=4:size=2e6,atrim=0:{TOTAL},afade=t=out:st={TOTAL - 3}:d=2.5")
    add(f"{SFX}/cingirak.mp3", 0.0, 0.6)
    add(f"{SFX}/fis_carpma.mp3", 1.05, 0.9)
    add(f"{SFX}/loupe.mp3", 13.35, 0.5)
    for ts in (14.3, 15.9):
        add(f"{SFX}/makas.mp3", ts - 0.05, 0.85)
        add(f"{SFX}/buyulu_geri.mp3", ts + 0.75, 0.7)
    add(f"{SFX}/kagit_acma.mp3", 22.0, 0.6)
    for (_, a, b) in BACK_SEG:
        add(f"{SFX}/kalem.mp3", a, 0.3, f",atrim=0:{b - a:.2f},afade=t=out:st={max(0, b - a - 0.2):.2f}:d=0.2")
    add(f"{SFX}/kalem.mp3", T_TICKET + 0.2, 0.7, ",atrim=0:2.5,afade=t=out:st=2.1:d=0.4")
    add(f"{SFX}/damga.mp3", T_CTA - 0.75, 0.8)
    add(f"{SFX}/muzik.mp3", 22.0, 0.26, f",afade=t=in:st=0:d=2.5,afade=t=out:st={T_END - 22.0 - 1.5}:d=1.5")
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
