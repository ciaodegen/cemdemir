import json, math
V = [0, 0.625, 0.725, 4.0]
W, H = 1500, 1950
specs = []
def add(name, char, **k):
    d = dict(name=name, char=char, w=W, h=H, view=V); d.update(k); specs.append(d)
def mouths(base, char, **k):
    for m in range(5):
        add(f"{base}_m{m}", char, mouth=m / 4, **k)
    if "blink" not in k:
        add(f"{base}_b", char, mouth=0, blink=1.0, **k)
        add(f"{base}_h", char, mouth=0, blink=0.5, **k)
# Elif
mouths("F_front", 3, headYaw=0.06, gaze=[0.12, 0.0], brow=0.35, smile=0.1)
mouths("F_shy", 3, headPitch=0.3, headYaw=0.05, gaze=[0.0, -0.8], brow=0.55)
mouths("F_soft", 3, headYaw=0.06, gaze=[0.1, -0.2], brow=0.3, smile=0.55)
mouths("F_stun", 3, headYaw=-0.25, gaze=[-0.6, 0.15], brow=0.75)
for m in range(3):
    add(f"F_smile_m{m}", 3, headYaw=0.04, gaze=[0.1, 0.05], brow=0.45, smile=1.0, mouth=0.15 + m * 0.1)
add("F_smile_b", 3, headYaw=0.04, gaze=[0.1, 0.05], brow=0.45, smile=1.0, mouth=0.15, blink=1.0)
add("F_smile_h", 3, headYaw=0.04, gaze=[0.1, 0.05], brow=0.45, smile=1.0, mouth=0.15, blink=0.5)
add("F_back", 3, yaw=math.pi)
# Deniz looks up at Elif, sincere
mouths("D_sincere", 1, yaw=-0.35, headYaw=-0.25, gaze=[-0.6, 0.1], brow=0.6, smile=0.25)
# Usta proud of Deniz
mouths("E_proud", 0, yaw=0.3, headYaw=0.5, gaze=[0.8, 0.0], brow=0.45, blink=0.3)
json.dump(specs, open("specs_b2.json", "w"), indent=0)
print(len(specs))
