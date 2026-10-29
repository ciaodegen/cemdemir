import json, math
V = [0, 0.625, 0.725, 4.0]
W, H = 1000, 1300
specs = []
def add(name, char, **k):
    d = dict(name=name, char=char, w=W, h=H, view=V); d.update(k); specs.append(d)
def mouths(base, char, **k):
    for m in range(5):
        add(f"{base}_m{m}", char, mouth=m / 4, **k)
    if "blink" not in k:
        add(f"{base}_b", char, mouth=0, blink=1.0, **k)
        add(f"{base}_h", char, mouth=0, blink=0.5, **k)
# Eşref
mouths("E_front", 0, headYaw=-0.15, gaze=[-0.35, -0.1])
mouths("E_serious", 0, headYaw=-0.12, gaze=[-0.3, -0.15], brow=-0.7)
mouths("E_soft", 0, headYaw=-0.1, gaze=[-0.3, -0.1], brow=0.35, blink=0.3)
mouths("E_side", 0, yaw=0.3, headYaw=0.55, gaze=[0.8, 0.0], brow=-0.4)
mouths("E_loupe", 0, headPitch=0.18, gaze=[-0.2, -0.6], loupe=1.0, blink=0.0)
for i, l in enumerate([0.2, 0.45, 0.7, 0.9]):
    add(f"E_loupe_in{i}", 0, headPitch=0.18 * l, gaze=[-0.2, -0.6], loupe=l)
add("E_back", 0, yaw=math.pi * 0.92)
add("E_turn", 0, yaw=math.pi * 0.55, headYaw=0.3)
# Deniz
mouths("D_phone", 1, yaw=-0.15, headPitch=0.42, gaze=[-0.1, -0.9], brow=0.1)
mouths("D_listen", 1, yaw=-0.3, headYaw=-0.25, gaze=[-0.6, 0.0])
mouths("D_whisper", 1, yaw=-0.2, headYaw=-0.1, gaze=[-0.45, -0.1], brow=0.7)
# Emre
mouths("M_front", 2, headYaw=0.08, gaze=[0.15, 0.05], brow=0.25)
mouths("M_down", 2, headPitch=0.38, gaze=[0.0, -0.8], brow=0.4)
mouths("M_stun", 2, headYaw=0.05, gaze=[0.0, 0.1], brow=0.8)
mouths("M_soft", 2, headYaw=0.08, gaze=[0.15, 0.05], brow=0.3, smile=0.6)
add("M_back", 2, yaw=math.pi)
json.dump(specs, open("specs.json", "w"), indent=0)
print(len(specs))
