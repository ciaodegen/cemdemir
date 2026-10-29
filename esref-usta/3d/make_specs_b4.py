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
mouths("S_front", 6, headYaw=0.06, gaze=[0.12, 0.05], brow=0.4, smile=0.15)
mouths("S_sad", 6, headPitch=0.25, headYaw=0.05, gaze=[0.0, -0.7], brow=0.65)
mouths("S_smile", 6, headYaw=0.05, gaze=[0.1, 0.0], brow=0.6, smile=0.55)
add("S_back", 6, yaw=math.pi)
json.dump(specs, open("specs_b4.json", "w"), indent=0); print(len(specs))
