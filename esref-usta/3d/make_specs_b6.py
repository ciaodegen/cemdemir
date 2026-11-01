import json, math
V = [0, 0.625, 0.725, 4.0]; W, H = 1500, 1950
specs = []
def add(name, char, **k):
    d = dict(name=name, char=char, w=W, h=H, view=V); d.update(k); specs.append(d)
def mouths(base, char, **k):
    for m in range(5):
        add(f"{base}_m{m}", char, mouth=m / 4, **k)
    if "blink" not in k:
        add(f"{base}_b", char, mouth=0, blink=1.0, **k)
        add(f"{base}_h", char, mouth=0, blink=0.5, **k)
mouths("R_front", 10, headYaw=0.06, gaze=[0.12, 0.0], brow=0.35)
mouths("R_sad", 10, headPitch=0.3, headYaw=0.05, gaze=[0.0, -0.8], brow=0.6)
mouths("R_stun", 10, headYaw=0.05, gaze=[0.05, 0.05], brow=0.85)
mouths("R_soft", 10, headYaw=0.06, gaze=[0.1, -0.1], brow=0.4, smile=0.45)
add("R_back", 10, yaw=math.pi)
json.dump(specs, open("specs_b6.json", "w"), indent=0); print(len(specs))
