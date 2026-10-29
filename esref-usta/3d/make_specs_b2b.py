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
mouths("K_front", 4, headPitch=-0.12, gaze=[0.0, 0.4], brow=0.4)
mouths("K_sad", 4, headPitch=0.25, gaze=[0.0, -0.6], brow=0.65)
mouths("K_look", 4, headPitch=0.3, headYaw=-0.15, gaze=[-0.3, -0.8], brow=0.7)
mouths("K_smile", 4, headPitch=-0.1, gaze=[0.0, 0.4], brow=0.3, smile=0.8)
add("K_back", 4, yaw=math.pi)
mouths("E_read", 0, headPitch=0.3, gaze=[0.0, -0.8], brow=0.2)
json.dump(specs, open("specs_b2b.json", "w"), indent=0); print(len(specs))
