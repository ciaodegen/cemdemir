"""Bölüm 15 — "Üniversite Okumaya Değer mi?" (~55 sn). Diplomam var işim yok; ret mailleri; Usta'dan ilk iş: dükkân tabelası."""
import sys, re, subprocess, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum14")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum15")
from PIL import Image, ImageDraw
from engine import W, H, UI, FPS, ROOT, finish, subtitle, envelope, duration, smooth, font, FONT_SERIF_B
import scenes3d as s3
from scenes3d import shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU, loupe_in, loupe_out
from scenes import plate
import inserts as ins
import inserts_diploma as idp

REP = f"{ROOT}/bolum15/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = customer), subtitle
    ("01v_Z", "E", "Usta, üniversite okumaya değer mi? Diplomam var, işim yok!"),
    ("02v_Z", "E", "Yüz on iki başvuru… hepsi \"deneyim\" istiyor!"),
    ("03v_Z", "E", "Yüz on üç…"),
    ("04_D", "D", "Abla, diplomayı çerçeveletelim, en azından duvarda bir işe yarasın."),
    ("04_U", "U", "Deniz."),
    ("05_U", "U", "Dur, bir bakalım…"),
    ("08_U", "U", "Diploma kapıyı gösterir evladım… kapıyı açan, elindeki iştir."),
    ("09_U", "U", "Şu tabela otuz yıldır aynı. Yenisini sen çizer misin?"),
    ("10v_Z", "E", "Ciddi misiniz usta?"),
    ("11_U", "U", "İlk deneyimin benden. Gerisi senin elinde."),
    ("12v_Z", "E", "O zaman CV'me ilk satırı yazıyorum: \"Eşref Usta Tamir Atölyesi!\""),
    ("13_D", "D", "Ben hiç okumadım abi, ustanın yanında öğrendim. Bence değmez."),
    ("04_U", "U", "Deniz."),
]
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
# subtitle chunks per line; their timing is snapped to the pauses measured in each audio file
CHUNKS = {3: ["Abla, diplomayı çerçeveletelim,", "en azından duvarda bir işe yarasın."],
          6: ["Diploma kapıyı gösterir evladım…", "…kapıyı açan, elindeki iştir."],
          7: ["Şu tabela otuz yıldır aynı.", "Yenisini sen çizer misin?"],
          9: ["İlk deneyimin benden.", "Gerisi senin elinde."],
          10: ["O zaman CV'me ilk satırı yazıyorum:", "\"Eşref Usta Tamir Atölyesi!\""],
          11: ["Ben hiç okumadım abi, ustanın yanında öğrendim.", "Bence değmez."]}
CUTS = {}


@functools.lru_cache(None)
def pauses(path):
    """Midpoints of the short silences inside a line (candidate subtitle cut points)."""
    o = subprocess.run(["ffmpeg", "-i", path, "-af", "silencedetect=n=-35dB:d=0.07", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", o)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", o)]
    return [(a + b) / 2 for a, b in zip(st, en) if a > 0.05]


@functools.lru_cache(None)
def chunk_times(i):
    """Start offset of each subtitle chunk of line i: proportional to text length, snapped to the nearest real pause."""
    if i in CUTS:
        return CUTS[i]
    parts = CHUNKS[i]
    L = [len(p) for p in parts]
    cand = pauses(f"{REP}/{LINES[i][0]}.mp3")
    out, used, acc = [0.0], -1, 0
    for l in L[:-1]:
        acc += l
        p = acc / sum(L) * DUR[i]
        best = None
        for j, c in enumerate(cand):
            if j > used and abs(c - p) < 0.8 and (best is None or abs(c - p) < abs(cand[best] - p)):
                best = j
        if best is not None:
            used = best; out.append(cand[best])
        else:
            out.append(p)
    return out


T, START = {}, {}
START[0] = 0.35; T["wide"] = (0.0, max(4.0, START[0] + DUR[0] + 0.2)); PUT = 1.1; t = T["wide"][1]
START[1] = t + 0.15; T["dert"] = (t, START[1] + DUR[1] + 0.2); t = T["dert"][1]
T["mail"] = (t, t + 2.6); BUZZ = t - 0.2; NEWMAIL = t + 0.5; t = T["mail"][1]
START[2] = t + 0.3; T["uzgun"] = (t, START[2] + DUR[2] + 0.6); t = T["uzgun"][1]
START[3] = t + 0.1; T["deniz"] = (t, START[3] + DUR[3] + 0.15); t = T["deniz"][1]
START[4] = t + 0.1; T["tepki"] = (t, START[4] + DUR[4] + 0.2); t = T["tepki"][1]
START[5] = t + 0.1; T["bakalim"] = (t, START[5] + DUR[5] + 0.6); T["loupe_in"] = T["bakalim"][1] - 0.55; t = T["bakalim"][1]
T["dip"] = (t, t + 2.7); GLOW = (t + 1.1, t + 1.8); t = T["dip"][1]
START[6] = t + 0.25; T["cevap"] = (t, START[6] + DUR[6] + 0.35); t = T["cevap"][1]
START[7] = t + 0.15; T["tabela"] = (t, START[7] + 2.41); T["soru"] = (T["tabela"][1], START[7] + DUR[7] + 0.3); t = T["soru"][1]
START[8] = t + 0.1; T["ciddi"] = (t, START[8] + DUR[8] + 0.3); t = T["ciddi"][1]
START[9] = t + 0.15; T["ilk"] = (t, START[9] + DUR[9] + 0.3); t = T["ilk"][1]
START[10] = t + 0.15; T["final"] = (t, START[10] + DUR[10] + 0.8); t = T["final"][1]
T_TICKET = t; T_CTA = t + 4.0; T_END = T_CTA + 2.4
START[11] = T_END + 0.25; START[12] = START[11] + DUR[11] + 0.15
TOTAL = round(START[12] + DUR[12] + 1.6, 2)
FIELDS = (("Arıza:", "\"Diplomam var, işim yok.\""),
          ("Yapılan işlem:", "İlk iş verildi: dükkân tabelası."),
          ("Not:", "Diploma kapıyı gösterir; kapıyı açan elindeki iştir."))


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
s3.BLINKS["E"] = [T["dert"][0] + 1.6, T["uzgun"][0] + 0.9, T["final"][0] + 1.5]
s3.BLINKS["U"] = [T["tepki"][0] + 0.9, T["cevap"][0] + 2.6, T["ilk"][0] + 1.4]
s3.BLINKS["D"] = [T["deniz"][0] + 1.4, START[11] + 0.9]


def sub_at(t):
    for i, (f, s, txt) in enumerate(LINES):
        if txt and START[i] - 0.05 <= t < START[i] + DUR[i] + 0.2:
            if i in CHUNKS:
                ts = chunk_times(i); u = t - START[i]
                k = max(j for j, c in enumerate(ts) if u >= c - 0.05) if u >= -0.05 else 0
                return CHUNKS[i][k]
            return txt
    return ""


def S(t0, t1, fn):
    return (t0, t1, fn)


def crop(img, cx, cy, z):
    cw, chh = 1440 / z, 2560 / z
    x0 = min(max(cx - cw / 2, 0), 1440 - cw); y0 = min(max(cy - chh / 2, 0), 2560 - chh)
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + chh))).resize((W, H), Image.LANCZOS)


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


def shot_wide(t):
    return shop(t, push(WIDE, t, *T["wide"], 0.04), deniz="D_phone", rope="diploma" if t >= PUT else "none",
                emre_back=(120 - 220 * (1 - smooth(min(1.0, t / 1.0))), 560, 0.95, 5, "Z_back", 0.85))


def pcrop(img, keys, t):
    """keys in plate coordinates: [(time, x, y, zoom)]."""
    k = keys[0] if t <= keys[0][0] else keys[-1]
    for k0, k1 in zip(keys, keys[1:]):
        if k0[0] <= t < k1[0]:
            u = smooth((t - k0[0]) / (k1[0] - k0[0]))
            k = tuple(k0[j] + (k1[j] - k0[j]) * u for j in range(4))
            break
    return crop(img, k[1], k[2], k[3])


def shot_bakalim(t):
    t0, t1 = T["bakalim"]
    p = loupe_in(t, T["loupe_in"])
    cam = push(USTA_CU, t, t0, t1, 0.06)
    if p is None:
        return shop(t, cam, usta="E_serious", rope="diploma", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, rope="diploma", bg_blur=9, deniz_blur=8, usta_blinks=False)


def shot_mail(t):
    t0, t1 = T["mail"]
    img = idp.mail_plate(int(round(k01(t, NEWMAIL, NEWMAIL + 0.35) * 10)))
    return pcrop(img, [(t0, 720, 1200, 1.55), (NEWMAIL + 0.3, 720, 1200, 1.6), (t1, 720, 1050, 2.0)], t)


def shot_dip(t):
    t0, t1 = T["dip"]
    gq = int(round(smooth(k01(t, *GLOW)) * 20))
    img = idp.diploma_plate(gq)
    x, y = idp.diploma_point(560, 400)
    xd, yd = idp.diploma_point(560, 500)
    return pcrop(img, [(t0, x, y, 1.25), (GLOW[0], x, yd, 1.6), (t1, x, yd, 2.1)], t)


def shot_cevap(t):
    t0, t1 = T["cevap"]
    p = loupe_out(t, t0 + 0.05)
    cam = push(USTA_CU, t, t0, t1, 0.1)
    if p is None:
        return shop(t, cam, usta="E_soft", rope="diploma", bg_blur=9, deniz_blur=8, usta_blinks=False)
    return shop(t, cam, usta=p, usta_mouth=0, rope="diploma", bg_blur=9, deniz_blur=8)


SIGN = (707, 1110, 1000)


def shot_tabela(t):
    return shop(t, push(SIGN, t, *T["tabela"], 0.06), usta="E_proud", rope="diploma", bg_blur=0, deniz_blur=2)


@functools.lru_cache(None)
def _ticket(progress, stamp):
    return ins.ticket(progress, stamp, "015", FIELDS, "İLK DENEYİM")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("İş arayan bir", "mezuna gönder."), "Eşref Usta · Bölüm 15")


def shot_stinger(t):
    img = shop(t, push((s3.DENIZ_X - 30, 1450, 740), t, T_END, TOTAL, 0.05), deniz="D_whisper", rope="none", deniz_blur=0, bg_blur=8, usta_blur=6)
    return with_banner(img, _banner("SİZCE ÜNİVERSİTE", "OKUMAYA DEĞER Mİ?", "Yorumlara yaz"), 0.1, smooth(k01(t, START[11] + 0.4, START[11] + 0.9)))


def cu(name, key, push_amt=0.06, mouth=None, cam=EMRE_CU, rope="diploma"):
    return S(*T[key], lambda t: door(t, push(cam, t, *T[key], push_amt), emre=name, rope=rope, emre_mouth=mouth))


SHOTS = [
    S(*T["wide"], shot_wide),
    cu("Z_front", "dert", 0.1),
    S(*T["mail"], shot_mail),
    cu("Z_sad", "uzgun", 0.08),
    S(*T["deniz"], lambda t: shop(t, push(DENIZ_MCU, t, *T["deniz"]), deniz="D_sincere", rope="diploma", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(*T["tepki"], lambda t: shop(t, push(USTA_MCU, t, *T["tepki"]), usta="E_side", deniz="D_sincere", rope="diploma", bg_blur=8, deniz_blur=6)),
    S(*T["bakalim"], shot_bakalim),
    S(*T["dip"], shot_dip),
    S(*T["cevap"], shot_cevap),
    S(*T["tabela"], shot_tabela),
    S(*T["soru"], lambda t: shop(t, push(USTA_CU, t, *T["soru"], 0.06), usta="E_proud", rope="diploma", bg_blur=9, deniz_blur=8)),
    cu("Z_stun", "ciddi", 0.06),
    S(*T["ilk"], lambda t: shop(t, push(USTA_CU, t, *T["ilk"], 0.08), usta="E_soft", rope="diploma", bg_blur=9, deniz_blur=8)),
    cu("Z_tear", "final", 0.06, rope="none"),
    S(T_TICKET, T_CTA, plate(lambda t: _ticket(round(k01(t, T_TICKET + 0.2, T_TICKET + 2.7) * 60) / 60, round(k01(t, T_CTA - 0.75, T_CTA - 0.4) * 8) / 8), T_TICKET, T_CTA, 1.04, 1.0)),
    S(T_CTA, T_END, plate(lambda t: _cta(), T_CTA, T_END, 1.0, 1.0)),
    S(T_END, TOTAL, shot_stinger),
]

PHONE = ("mail",)


def frame_at(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            img = fn(t)
            break
    else:
        img = Image.new("RGB", (W, H))
    img = finish(img, t, dust=False, grain=False)
    inn = lambda keys: any(T[k][0] <= t < T[k][1] for k in keys)
    yf = 0.705
    txt = sub_at(t)
    if txt and inn(PHONE):
        band = Image.new("RGBA", (W, int(H * 0.09)), (20, 16, 14, 170))
        img = img.convert("RGBA"); img.alpha_composite(band, (0, int(H * (yf - 0.035))))
    if t < T_TICKET or t >= T_END:
        img = subtitle(img, txt, yf)
    for tc in (T_CTA, T_END):
        if tc - 0.3 <= t < tc + 0.3:
            k = abs(t - tc) / 0.3
            img = Image.eval(img, lambda v, k=k: int(v * min(1, k)))
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
    add(f"{SFX}/cingirak.mp3", 0.0, 0.35, ",atrim=0:1.0,afade=t=out:st=0.3:d=0.7")   # short bell, fades before the hook
    add(f"{SFX}/kagit_birakma.mp3", PUT, 0.5)
    add(f"{SFX}/telefon.mp3", BUZZ, 0.5, ",atrim=0:1.2,afade=t=out:st=0.9:d=0.3")
    add(f"{SFX}/tin.mp3", NEWMAIL, 0.35)
    add(f"{SFX}/loupe.mp3", T["loupe_in"], 0.5)
    add(f"{SFX}/tin.mp3", GLOW[0], 0.45)
    add(f"{SFX}/cingirak_cikis.mp3", T["final"][1] - 0.3, 0.3)
    add(f"{SFX}/kalem.mp3", T_TICKET + 0.2, 0.7, ",atrim=0:2.5,afade=t=out:st=2.1:d=0.4")
    add(f"{SFX}/damga.mp3", T_CTA - 0.75, 0.8)
    m0 = T["uzgun"][0]
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
