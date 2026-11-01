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
mouths("Y_front", 12, headYaw=0.06, gaze=[0.12, 0.0], brow=0.4)
add("Y_back", 12, yaw=math.pi)
mouths("Y_stun", 12, headYaw=0.05, gaze=[0.0, -0.3], brow=0.9)
mouths("Y_soft", 12, headYaw=0.06, gaze=[0.1, -0.05], brow=0.35, smile=0.5, loupe=1.0)
json.dump(specs[:15], open("specs_b7b1.json", "w"), indent=0)
json.dump(specs[15:], open("specs_b7b2.json", "w"), indent=0); print(len(specs))
