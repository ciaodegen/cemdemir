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
mouths("H_front", 9, headYaw=0.06, gaze=[0.12, 0.0], brow=0.3, smile=0.25)
mouths("H_sad", 9, headPitch=0.3, headYaw=0.05, gaze=[0.0, -0.8], brow=0.6)
mouths("H_stun", 9, headYaw=0.05, gaze=[0.05, 0.05], brow=0.85)
mouths("H_decided", 9, headYaw=0.06, gaze=[0.12, 0.0], brow=-0.2)
add("H_back", 9, yaw=math.pi)
json.dump(specs, open("specs_b5.json", "w"), indent=0); print(len(specs))
