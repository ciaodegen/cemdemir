"""Bölüm 7 — "Boya Tutmayan Atkı" (~43 sn)."""
import sys, subprocess, functools, math
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum7")
from PIL import Image
from engine import W, H, FPS, ROOT, finish, subtitle, envelope, duration, smooth
import scenes3d as s3
from scenes3d import shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU, USTA_BACK_OTS
from scenes import split_sub, plate
import inserts as ins
import atki

REP = f"{ROOT}/bolum7/replikler_hizli"
SFX = f"{ROOT}/efektler"

LINES = [  # file, speaker (E = Cengiz), subtitle
    ("a_01_C", "E", "Usta, Fenerbahçeli olmaktan yoruldum. Şu atkıyı sarı-kırmızıya boyar mısın? Galatasaraylı olmak istiyorum."),
    ("a_02_D", "D", "Doğru seçim kardeşim! Ben boyarım!"),
    ("03_U", "U", "Deniz."),
    ("a_04_D", "D", "Aa… geri döndü?"),
    ("a_05_U", "U", "Dur, bir de ben deneyeyim."),
    ("a_08_U", "U", "Boya tutmuyor evlat. Çünkü bu renk kumaşta değil, kalpte. Kazanmak bir gecelik iş. Kalpteki yer ömürlük."),
    ("b_09_C", "E", "Boyamayın usta. Kalsın. Biz gönülden seviyoruz. Şampiyon olamasak da kalbimiz Fenerbahçe'yle."),
]
START = {0: 0.5, 1: 5.85, 2: 8.1, 3: 12.0, 4: 13.95, 5: 18.7, 6: 28.15}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
TOTAL = 43.9
T_TICKET, T_CTA = 36.9, 41.3
FIELDS = (("Arıza:", "Takım değiştirme talebi."),
          ("Yapılan işlem:", "İki kat boyandı. Tutmadı."),
          ("Not:", "Kazanmak bir gecelik. Kalpteki yer ömürlük."))


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


s3.speaking = speaking
s3.BLINKS["E"] = [30.05, 32.3, 35.1]
s3.BLINKS["U"] = [2.6, 15.2, 36.0]


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
def _ticket(progress, stamp):
    return ins.ticket(progress, stamp, "007", FIELDS, "BOYA TUTMADI")


@functools.lru_cache(None)
def _cta():
    return ins.cta(("Kaybetse de takımından", "vazgeçmeyen arkadaşına gönder."), "Eşref Usta · Bölüm 7")


def S(t0, t1, fn):
    return (t0, t1, fn)


def k01(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def lerp(p, q, k):
    return (p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k)


CU = (623, 2090, 420)
OFF = (900, 1800)                 # brush parked off-frame, upper right
W0 = atki.HX0 - 6; WW = atki.HX1 - atki.HX0 + 12


def tip1(p):
    x = W0 + p * WW
    return (x, atki.HY0 + atki.STRIPE * 1.5 + (x - atki.HX0) * 0.08)


NAVIES = [1, 3, 5, 7]


def tip2(p):
    k = min(p * len(NAVIES), len(NAVIES) - 1e-3)
    i = int(k); f = k - i
    return (W0 + f * WW, atki.HY0 + (NAVIES[i] + 0.5) * atki.STRIPE)


def stroke(t, t_in, t0, t1, t_out, tipf):
    """Brush position and paint progress for a stroke: approach, paint, lift away."""
    if t < t_in or t >= t_out + 0.35:
        return None, (1.0 if t >= t1 else 0.0)
    if t < t0:
        return lerp(OFF, tipf(0), smooth(k01(t, t_in, t0))), 0.0
    if t < t1:
        p = k01(t, t0, t1)
        return tipf(p), p
    if t < t_out:
        return tipf(1.0), 1.0
    return lerp(tipf(1.0), OFF, smooth(k01(t, t_out, t_out + 0.35))), 1.0


def paint_shot(t, t0, t1, coat, t_in, ts, te, t_out, r0, r1, tipf):
    pos, p = stroke(t, t_in, ts, te, t_out, tipf)
    r = k01(t, r0, r1)
    brush = (pos[0], pos[1], -32 + 6 * math.sin(t * 9)) if pos else None
    ov = atki.overlay(brush_on=False, coat=coat, p=p, r=r, brush=brush)
    return shop(t, push(CU, t, t0, t1, 0.05), usta="E_serious", rope="none", usta_blur=7, deniz_blur=9, bg_blur=9, overlay=ov)


def hover_shot(t):
    t0, t1 = 20.1, 22.4
    target = (650, atki.HY0 + 3.5 * atki.STRIPE)
    if t < 20.5:
        pos = lerp(OFF, (target[0] + 40, target[1] - 70), smooth(k01(t, 20.1, 20.5)))
    elif t < 22.05:
        k = k01(t, 20.5, 22.05)
        base = lerp((target[0] + 40, target[1] - 70), (target[0] + 12, target[1] - 18), smooth(min(1, k * 1.6)))
        amp = 2.0 + 6.0 * k
        pos = (base[0] + amp * math.sin(t * 41) + 0.6 * amp * math.sin(t * 23), base[1] + amp * 0.8 * math.sin(t * 33 + 1))
    else:
        pos = lerp((target[0] + 12, target[1] - 18), OFF, smooth(k01(t, 22.05, 22.4)))
    ov = atki.overlay(brush_on=False, brush=(pos[0], pos[1], -32))
    return shop(t, push(CU, t, t0, t1, 0.09), usta="E_serious", rope="none", usta_blur=7, deniz_blur=9, bg_blur=9, overlay=ov)


def lift_shot(t):
    k = 1.0 - smooth(k01(t, 27.25, 27.95))
    ov = atki.overlay(brush_on=True, scarf_drop=k)
    return shop(t, push(CU, t, 27.1, 28.0, 0.03), usta="E_soft", rope="none", usta_blur=7, deniz_blur=9, bg_blur=9, usta_blinks=False, overlay=ov)


def arrive(t):
    return atki.overlay(brush_on=True, can_slide=smooth(k01(t, 0.6, 1.0)), scarf_drop=smooth(k01(t, 0.9, 1.3)))


ON = atki.overlay(brush_on=True)
CAN_ONLY = atki.overlay(brush_on=True, scarf=False)

SHOTS = [
    S(0.0, 5.8, lambda t: shop(t, push(WIDE, t, 0, 5.8, 0.04), deniz="D_phone", rope="none", overlay=arrive(t),
                               emre_back=(120 - 220 * (1 - smooth(t / 1.0)), 560, 0.95, 5, "Y_back", 0.82))),
    S(5.8, 8.0, lambda t: shop(t, push(DENIZ_MCU, t, 5.8, 8.0), deniz="D_sincere", rope="none", overlay=ON, deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(8.0, 9.3, lambda t: shop(t, push(USTA_MCU, t, 8.0, 9.3), usta="E_side", deniz="D_sincere", rope="none", overlay=ON, bg_blur=8, deniz_blur=6)),
    S(9.3, 12.0, lambda t: paint_shot(t, 9.3, 12.0, 1, 9.3, 9.6, 10.3, 10.4, 10.8, 11.7, tip1)),
    S(12.0, 13.9, lambda t: shop(t, push(DENIZ_MCU, t, 12.0, 13.9), deniz="D_listen", rope="none", overlay=atki.overlay(brush_on=False), deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(13.9, 15.5, lambda t: shop(t, push(USTA_MCU, t, 13.9, 15.5), usta="E_front", rope="none", overlay=atki.overlay(brush_on=False), bg_blur=8, deniz_blur=6)),
    S(15.5, 18.5, lambda t: paint_shot(t, 15.5, 18.5, 2, 15.5, 15.7, 16.9, 17.0, 17.3, 18.2, tip2)),
    S(18.5, 27.1, lambda t: shop(t, push(USTA_CU, t, 18.5, 27.1, 0.12), usta="E_soft", rope="none", overlay=ON, bg_blur=9, deniz_blur=8, usta_blinks=False)),
    S(27.1, 28.0, lift_shot),
    S(28.0, 35.3, lambda t: door(t, push(EMRE_MCU, t, 28.0, 35.3, 0.2), emre="Y_soft", rope="none", overlay=CAN_ONLY)),
    S(35.3, T_TICKET, lambda t: shop(t, push(USTA_MCU, t, 35.3, T_TICKET, 0.04), usta="E_proud", rope="none", overlay=CAN_ONLY, bg_blur=8, deniz_blur=6, usta_blinks=False)),
    S(T_TICKET, T_CTA, plate(lambda t: _ticket(round(k01(t, T_TICKET + 0.2, T_TICKET + 3.2) * 60) / 60, round(k01(t, T_CTA - 0.8, T_CTA - 0.45) * 8) / 8), T_TICKET, T_CTA, 1.04, 1.0)),
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
        img = subtitle(img, sub_at(t), 0.6 if t < 5.8 else 0.705)
    if t > TOTAL - 0.6:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.6: int(v * max(k, 0)))
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
    for i, (f, _, _) in enumerate(LINES):
        add(f"{REP}/{f}.mp3", START[i], 1.0)
    add(f"{SFX}/ortam.mp3", 0.0, 0.32, f",aloop=loop=4:size=2e6,atrim=0:{TOTAL},afade=t=out:st={TOTAL - 4}:d=3")
    add(f"{SFX}/cingirak.mp3", 0.0, 0.6)
    add(f"{SFX}/boya_kutusu.mp3", 0.95, 0.5)
    add(f"{SFX}/firca.mp3", 9.55, 0.8)
    add(f"{SFX}/buyulu_geri.mp3", 10.8, 0.75)
    add(f"{SFX}/firca.mp3", 15.65, 0.8)
    add(f"{SFX}/firca.mp3", 16.3, 0.5, ",atrim=0:0.7,afade=t=out:st=0.4:d=0.3")
    add(f"{SFX}/buyulu_geri.mp3", 17.3, 0.85)
    add(f"{SFX}/cingirak_cikis.mp3", 35.5, 0.35)
    add(f"{SFX}/kalem.mp3", T_TICKET + 0.2, 0.7, ",atrim=0:3.0,afade=t=out:st=2.6:d=0.4")
    add(f"{SFX}/damga.mp3", T_CTA - 0.8, 0.8)
    add(f"{SFX}/muzik.mp3", 18.5, 0.26, f",afade=t=in:st=0:d=2.5,afade=t=out:st={TOTAL - 18.5 - 3.0}:d=3.0")
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
