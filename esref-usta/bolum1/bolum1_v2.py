"""Bölüm 1 v2 — kısaltılmış kurgu (~74 sn): telefon ve arkasını dönme sahneleri yok,
konuşmalar 1.1x, film greni/toz yok."""
import sys, subprocess
from PIL import Image
from engine import W, H, FPS, ROOT, finish, subtitle, envelope, duration, smooth
import scenes3d as s3
from scenes3d import (shop, door, push, WIDE, USTA_MCU, USTA_CU, DENIZ_MCU, EMRE_MCU, EMRE_CU,
                      EMRE_BACK_WIDE, USTA_BACK_OTS, loupe_in, loupe_out)
from scenes import LINES, split_sub, plate, _ins

REP = f"{ROOT}/bolum1/replikler_hizli"
SFX = f"{ROOT}/efektler"

START = {0: 0.9, 1: 4.0, 2: 6.2, 3: 9.5, 4: 11.1, 5: 13.0, 6: 14.2, 7: 18.4, 8: 19.7, 9: 21.1,
         10: 26.9, 11: 34.2, 12: 37.3, 13: 39.4, 14: 41.8, 15: 44.1, 16: 54.5, 17: 56.7}
DUR = {i: duration(f"{REP}/{f}.mp3") for i, (f, _, _) in enumerate(LINES)}
TOTAL = 74.0


def speaking(t, who):
    for i, (f, s, _) in enumerate(LINES):
        if s == who and START[i] <= t < START[i] + DUR[i]:
            e = envelope(f"{REP}/{f}.mp3")
            k = int((t - START[i]) * FPS)
            return float(e[min(k, len(e) - 1)])
    return 0.0


# scenes3d reads speech timing through its own speaking(); point it at the new schedule
s3.speaking = speaking


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


def shotD(t):  # loupe goes on
    p = loupe_in(t, 7.7)
    cam = push(USTA_CU, t, 7.5, 9.3, 0.06)
    if p is None:
        return shop(t, cam, usta="E_front", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, bg_blur=9, deniz_blur=8, usta_blinks=False)


def shotI(t):  # loupe comes off, "Bu kopmamış."
    p = loupe_out(t, 18.05)
    cam = push(USTA_CU, t, 18.0, 19.6, 0.03)
    if p is None:
        return shop(t, cam, usta="E_serious", bg_blur=9, deniz_blur=8)
    return shop(t, cam, usta=p, usta_mouth=0, bg_blur=9, deniz_blur=8, usta_blinks=False)


def S(t0, t1, fn):
    return (t0, t1, fn)


SHOTS = [
    S(0.0, 3.9, lambda t: shop(t, push(WIDE, t, 0, 3.9, 0.04), deniz="D_phone",
                               emre_back=(120 - 220 * (1 - smooth(t / 1.2)), 560, 0.95, 5))),
    S(3.9, 6.1, lambda t: shop(t, push(DENIZ_MCU, t, 3.9, 6.1), deniz="D_phone", deniz_blur=0, bg_blur=8, usta_blur=6)),
    S(6.1, 7.5, lambda t: shop(t, push(USTA_MCU, t, 6.1, 7.5), usta="E_side", deniz="D_phone", bg_blur=8, deniz_blur=6)),
    S(7.5, 9.3, shotD),
    S(9.3, 11.0, plate(lambda t: _ins("rope_end", True), 9.3, 11.0, 1.0, 1.06)),
    S(11.0, 12.9, lambda t: door(t, push(EMRE_MCU, t, 11.0, 12.9, 0.03), emre="M_front", usta_back=USTA_BACK_OTS)),
    S(12.9, 14.1, lambda t: shop(t, push(USTA_MCU, t, 12.9, 14.1), usta="E_loupe", bg_blur=8, deniz_blur=6, usta_blinks=False)),
    S(14.1, 18.0, lambda t: door(t, push(EMRE_MCU, t, 14.1, 18.0, 0.1), emre="M_down")),
    S(18.0, 19.6, shotI),
    S(19.6, 21.0, lambda t: door(t, EMRE_CU, emre="M_stun")),
    S(21.0, 26.8, plate(lambda t: _ins("rope_end", False), 21.0, 26.8, 1.0, 1.1, cx=0.62)),
    S(26.8, 29.0, lambda t: door(t, push(EMRE_MCU, t, 26.8, 29.0, 0.03), emre="M_front", usta_back=USTA_BACK_OTS)),
    S(29.0, 30.4, lambda t: shop(t, push(USTA_CU, t, 29.0, 30.4, 0.04), usta="E_serious", bg_blur=9, deniz_blur=8)),
    S(30.4, 33.0, plate(lambda t: _ins("package", round(min(1, max(0, (t - 30.6) / 1.6)) * 12) / 12), 30.4, 33.0, 1.0, 1.05)),
    S(33.0, 34.1, lambda t: door(t, push(EMRE_CU, t, 33.0, 34.1, 0.03), emre="M_stun")),
    S(34.1, 37.2, lambda t: shop(t, push(USTA_MCU, t, 34.1, 37.2, 0.05), usta="E_serious", bg_blur=8, deniz_blur=6, package=True)),
    S(37.2, 39.3, lambda t: door(t, push(EMRE_MCU, t, 37.2, 39.3, 0.04), emre="M_down", usta_back=USTA_BACK_OTS)),
    S(39.3, 41.7, lambda t: shop(t, push(USTA_CU, t, 39.3, 41.7, 0.05), usta="E_front", bg_blur=9, deniz_blur=8, package=True)),
    S(41.7, 43.9, lambda t: shop(t, push(DENIZ_MCU, t, 41.7, 43.9, 0.05), deniz="D_whisper", deniz_blur=0, bg_blur=8, usta_blur=6, package=True)),
    S(43.9, 51.8, lambda t: shop(t, push(USTA_MCU, t, 43.9, 51.8, 0.15), usta="E_soft", bg_blur=8, deniz_blur=6, package=True, usta_blinks=False)),
    S(51.8, 54.4, plate(lambda t: _ins("rope_halves", t >= 52.9), 51.8, 54.4, 1.0, 1.05)),
    S(54.4, 56.6, lambda t: door(t, push(EMRE_MCU, t, 54.4, 56.6, 0.03), emre="M_soft", rope="knot")),
    S(56.6, 60.4, lambda t: shop(t, push(USTA_MCU, t, 56.6, 60.4, 0.06), usta="E_soft", bg_blur=8, deniz_blur=6, rope="knot", package=True, usta_blinks=False)),
    S(60.4, 63.6, plate(lambda t: _ins("phone", True, "Arkadaşlık · 12 yıl", "Murat", "aranıyor…", True), 60.4, 63.6, 1.0, 1.06)),
    S(63.6, 70.8, plate(lambda t: _ins("ticket", round(min(1, max(0, (t - 63.9) / 5.0)) * 60) / 60, round(min(1, max(0, (t - 69.4) / 0.35)) * 8) / 8), 63.6, 70.8, 1.04, 1.0)),
    S(70.8, 74.0, plate(lambda t: _ins("cta"), 70.8, 74.0, 1.0, 1.0)),
]


def frame_at(t):
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1:
            img = fn(t)
            break
    else:
        img = Image.new("RGB", (W, H))
    img = finish(img, t, dust=False, grain=False)
    if t < 70.8:
        img = subtitle(img, sub_at(t))
    if t < 0.4:
        img = Image.eval(img, lambda v, k=t / 0.4: int(v * k))
    if t > TOTAL - 0.6:
        img = Image.eval(img, lambda v, k=(TOTAL - t) / 0.6: int(v * max(k, 0)))
    if 70.5 <= t < 71.1:
        k = abs(t - 70.8) / 0.3
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
    add(f"{SFX}/ip.mp3", 0.6, 0.5)
    add(f"{SFX}/loupe.mp3", 7.95, 0.8)
    add(f"{SFX}/loupe.mp3", 18.2, 0.5)
    add(f"{SFX}/gazete.mp3", 30.5, 0.7)
    add(f"{SFX}/dugum.mp3", 52.0, 0.7)
    add(f"{SFX}/telefon.mp3", 60.8, 0.45)
    add(f"{SFX}/cingirak_cikis.mp3", 62.4, 0.45)
    add(f"{SFX}/kalem.mp3", 63.9, 0.7)
    add(f"{SFX}/damga.mp3", 69.4, 0.8)
    add(f"{SFX}/muzik.mp3", 39.5, 0.30, ",afade=t=in:st=0:d=3,afade=t=out:st=31:d=3.5")
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
