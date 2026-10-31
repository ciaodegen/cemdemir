import json, math
V = [0, 0.625, 0.725, 4.0]; W, H = 1500, 1950
specs = []
def add(name, char, **k):
    d = dict(name=name, char=char, w=W, h=H, view=V); d.update(k); specs.append(d)
def mouths(base, char, n=5, **k):
    for m in range(n):
        add(f"{base}_m{m}", char, mouth=m / 4, **k)
    if "blink" not in k:
        add(f"{base}_b", char, mouth=0, blink=1.0, **k)
        add(f"{base}_h", char, mouth=0, blink=0.5, **k)
mouths("L_front", 7, headYaw=0.06, gaze=[0.12, 0.0], brow=0.45)
mouths("L_worried", 7, headYaw=0.05, gaze=[0.1, 0.05], brow=0.75)
mouths("L_tender", 7, headPitch=0.3, headYaw=-0.1, gaze=[-0.2, -0.8], brow=0.6, smile=0.35)
mouths("L_smile", 7, headYaw=0.05, gaze=[0.05, -0.2], brow=0.5, smile=0.8)
add("L_back", 7, yaw=math.pi)
mouths("C_idle", 8, n=1, headYaw=-0.2, gaze=[-0.4, 0.3])
mouths("C_sad", 8, n=1, headPitch=0.25, headYaw=-0.1, gaze=[0.0, -0.5], brow=1.0)
for m in range(5):
    add(f"C_meow_m{m}", 8, headPitch=-0.1, headYaw=0.15, gaze=[0.4, 0.4], mouth=m / 4, brow=0.3)
add("C_meow_b", 8, headPitch=-0.1, headYaw=0.15, gaze=[0.4, 0.4], blink=1.0, brow=0.3)
add("C_meow_h", 8, headPitch=-0.1, headYaw=0.15, gaze=[0.4, 0.4], blink=0.5, brow=0.3)
json.dump(specs, open("specs_b3k.json", "w"), indent=0); print(len(specs))
