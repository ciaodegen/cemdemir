import type {InkPath} from '../components/Ink';
import {COLORS} from '../brand/theme';

/*
 * Architecture & landscape in canvas coordinates. Helpers return InkPath
 * lists (outline + optional flat fill) ready for <Ink>, or fill-only masses
 * for <Wash>.
 */

const f = (n: number) => n.toFixed(1);

export const crenellations = (x0: number, x1: number, y: number, size = 14): string => {
  let d = `M ${f(x0)} ${f(y)}`;
  let x = x0;
  let up = true;
  while (x < x1 - 0.1) {
    const nx = Math.min(x + size, x1);
    if (up) d += ` L ${f(x)} ${f(y - size)} L ${f(nx)} ${f(y - size)} L ${f(nx)} ${f(y)}`;
    else d += ` L ${f(nx)} ${f(y)}`;
    x = nx;
    up = !up;
  }
  return d;
};

/** Crenellated block (wall or tower body) as one closed, filled shape. */
const crenBlock = (x0: number, x1: number, ground: number, h: number, step: number, fill: string): InkPath => ({
  d: `M ${f(x0)} ${f(ground)} L ${f(x0)} ${f(ground - h)} ` + crenellations(x0, x1, ground - h, step).replace(/^M [^L]+/, '') + ` L ${f(x1)} ${f(ground)} Z`,
  fill,
});

export const wall = (x0: number, x1: number, ground: number, h: number, step = 14, fill: string = COLORS.sandLight): InkPath[] => [
  crenBlock(x0, x1, ground, h, step, fill),
];

export const tower = (cx: number, ground: number, w: number, h: number, fill: string = COLORS.sand): InkPath[] => [
  crenBlock(cx - w / 2, cx + w / 2, ground, h, w / 5, fill),
  {d: `M ${f(cx - 5)} ${f(ground - h * 0.64)} L ${f(cx - 5)} ${f(ground - h * 0.5)} L ${f(cx + 5)} ${f(ground - h * 0.5)} L ${f(cx + 5)} ${f(ground - h * 0.64)} Z`, fill: COLORS.ink},
];

export const archGate = (cx: number, ground: number, w: number, h: number, fill: string = COLORS.camel): InkPath => ({
  d: `M ${f(cx - w / 2)} ${f(ground)} L ${f(cx - w / 2)} ${f(ground - h + w / 2)} A ${f(w / 2)} ${f(w / 2)} 0 0 1 ${f(cx + w / 2)} ${f(ground - h + w / 2)} L ${f(cx + w / 2)} ${f(ground)} Z`,
  fill,
});

/** Stepped ziggurat with a central stair and a small shrine on top. */
export const ziggurat = (cx: number, ground: number, baseW: number, tierH: number, tiers = 3): InkPath[] => {
  const out: InkPath[] = [];
  let w = baseW;
  let y = ground;
  const tones = [COLORS.sand, COLORS.sandLight, COLORS.sand];
  for (let i = 0; i < tiers; i++) {
    const top = y - tierH;
    out.push({d: `M ${f(cx - w / 2)} ${f(y)} L ${f(cx - w / 2 + 6)} ${f(top)} L ${f(cx + w / 2 - 6)} ${f(top)} L ${f(cx + w / 2)} ${f(y)} Z`, fill: tones[i % 3]});
    y = top;
    w *= 0.66;
  }
  const sw = w * 0.8;
  out.push({d: `M ${f(cx - sw / 2)} ${f(y)} L ${f(cx - sw / 2)} ${f(y - tierH * 0.8)} L ${f(cx + sw / 2)} ${f(y - tierH * 0.8)} L ${f(cx + sw / 2)} ${f(y)} Z`, fill: COLORS.terracottaLight});
  out.push({d: `M ${f(cx - 6)} ${f(y)} L ${f(cx - 6)} ${f(y - tierH * 0.45)} L ${f(cx + 6)} ${f(y - tierH * 0.45)} L ${f(cx + 6)} ${f(y)} Z`, fill: COLORS.ink});
  out.push({d: `M ${f(cx - 12)} ${f(ground)} L ${f(cx - 8)} ${f(ground - tierH * tiers)} L ${f(cx + 8)} ${f(ground - tierH * tiers)} L ${f(cx + 12)} ${f(ground)} Z`, fill: COLORS.camel});
  return out;
};

/** Date palm: curved trunk with ring ticks and leaf-shaped fronds. */
export const palm = (x: number, ground: number, h: number, lean = 10): InkPath[] => {
  const tx = x + lean;
  const ty = ground - h;
  const out: InkPath[] = [];
  out.push({
    d: `M ${f(x - 6)} ${f(ground)} Q ${f(x - 5 + lean * 0.2)} ${f(ground - h * 0.5)} ${f(tx - 3)} ${f(ty)} L ${f(tx + 3)} ${f(ty)} Q ${f(x + 5 + lean * 0.2)} ${f(ground - h * 0.5)} ${f(x + 6)} ${f(ground)} Z`,
    fill: COLORS.camel,
  });
  const fronds: [number, number][] = [
    [-1, 0.25],
    [-0.75, -0.35],
    [-0.15, -0.6],
    [0.45, -0.45],
    [0.95, -0.15],
    [1, 0.3],
  ];
  const r = h * 0.45;
  for (const [dx, dy] of fronds) {
    const ex = tx + dx * r;
    const ey = ty + dy * r * 0.6 + r * 0.35;
    const cx = tx + dx * r * 0.6;
    const cy = ty + dy * r * 0.9 - r * 0.2;
    const nx = -(ey - ty) * 0.12;
    const ny = (ex - tx) * 0.12;
    out.push({
      d: `M ${f(tx)} ${f(ty)} Q ${f(cx + nx)} ${f(cy + ny)} ${f(ex)} ${f(ey)} Q ${f(cx - nx)} ${f(cy - ny)} ${f(tx)} ${f(ty)} Z`,
      fill: COLORS.olive,
    });
  }
  return out;
};

/** Two soft hill masses (fill only), sitting on baseline y. */
export const hillMasses = (y: number, fill: string = COLORS.sandLight, fill2: string = COLORS.taupeLight): {d: string; fill: string}[] => [
  {d: `M -20 ${y} C 140 ${y - 120} 300 ${y - 150} 470 ${y - 60} C 560 ${y - 20} 620 ${y - 10} 700 ${y} Z`, fill: fill2},
  {d: `M 380 ${y} C 560 ${y - 90} 760 ${y - 170} 1100 ${y - 80} L 1100 ${y} Z`, fill},
];

/** Ground band from the horizon down, ending in a soft hand-drawn edge. */
export const groundMass = (top: number, bottom: number, x0 = -20, x1 = 1100): string =>
  `M ${x0} ${top} C ${x0 + 300} ${top - 6} ${x1 - 300} ${top + 6} ${x1} ${top} L ${x1} ${bottom - 10} C ${x1 - 200} ${bottom + 8} ${x1 - 520} ${bottom - 12} ${x0 + 300} ${bottom + 4} C ${x0 + 160} ${bottom + 10} ${x0 + 60} ${bottom - 6} ${x0} ${bottom} Z`;

/** Ionic column, base at (x, ground). */
export const ionicColumn = (x: number, ground: number, h: number, w = 46, fill: string = COLORS.sandPale): InkPath[] => {
  const top = ground - h;
  const hw = w / 2;
  return [
    {d: `M ${f(x - hw - 12)} ${f(ground)} L ${f(x + hw + 12)} ${f(ground)} L ${f(x + hw + 8)} ${f(ground - 10)} L ${f(x - hw - 8)} ${f(ground - 10)} Z`, fill: COLORS.sand},
    {d: `M ${f(x - hw)} ${f(ground - 10)} L ${f(x - hw + 3)} ${f(top + 10)} L ${f(x + hw - 3)} ${f(top + 10)} L ${f(x + hw)} ${f(ground - 10)} Z`, fill},
    `M ${f(x - hw * 0.35)} ${f(ground - 16)} L ${f(x - hw * 0.33)} ${f(top + 28)} M ${f(x + hw * 0.35)} ${f(ground - 16)} L ${f(x + hw * 0.33)} ${f(top + 28)}`,
    {d: `M ${f(x - hw - 18)} ${f(top)} L ${f(x + hw + 18)} ${f(top)} L ${f(x + hw + 14)} ${f(top + 10)} L ${f(x - hw - 14)} ${f(top + 10)} Z`, fill: COLORS.sand},
    `M ${f(x - hw - 4)} ${f(top + 10)} c -12 0 -14 14 -4 16 c 6 1 8 -6 3 -8 M ${f(x + hw + 4)} ${f(top + 10)} c 12 0 14 14 4 16 c -6 1 -8 -6 -3 -8`,
  ];
};

/** Mediterranean cypress silhouette. */
export const cypress = (x: number, ground: number, h: number, fill: string = COLORS.olive): InkPath[] => [
  {d: `M ${f(x - 3)} ${f(ground)} L ${f(x - 3)} ${f(ground - 20)} L ${f(x + 3)} ${f(ground - 20)} L ${f(x + 3)} ${f(ground)} Z`, fill: COLORS.camel},
  {
    d: `M ${f(x)} ${f(ground - 16)} C ${f(x - h * 0.075)} ${f(ground - h * 0.3)} ${f(x - h * 0.06)} ${f(ground - h * 0.72)} ${f(x)} ${f(ground - h)} C ${f(x + h * 0.06)} ${f(ground - h * 0.72)} ${f(x + h * 0.075)} ${f(ground - h * 0.3)} ${f(x)} ${f(ground - 16)} Z`,
    fill,
  },
];

/** Round shrub. */
export const shrub = (x: number, ground: number, r: number, fill: string = COLORS.oliveLight): InkPath => ({
  d: `M ${f(x - r)} ${f(ground)} C ${f(x - r * 1.1)} ${f(ground - r * 1.2)} ${f(x - r * 0.2)} ${f(ground - r * 1.5)} ${f(x + r * 0.2)} ${f(ground - r * 1.2)} C ${f(x + r * 0.9)} ${f(ground - r * 1.4)} ${f(x + r * 1.3)} ${f(ground - r * 0.6)} ${f(x + r)} ${f(ground)} Z`,
  fill,
});

/** Olive sprig: a stem with paired leaves. */
export const oliveBranch = (x: number, y: number, len: number, angle = -60): InkPath[] => {
  const a = (angle * Math.PI) / 180;
  const ex = x + Math.cos(a) * len;
  const ey = y + Math.sin(a) * len;
  const out: InkPath[] = [`M ${f(x)} ${f(y)} Q ${f(x + Math.cos(a) * len * 0.5 + 10)} ${f(y + Math.sin(a) * len * 0.5)} ${f(ex)} ${f(ey)}`];
  for (let i = 1; i <= 5; i++) {
    const t = i / 6;
    const px = x + (ex - x) * t + 4;
    const py = y + (ey - y) * t;
    for (const side of [-1, 1]) {
      const la = a + side * 0.9;
      const lx = px + Math.cos(la) * 30;
      const ly = py + Math.sin(la) * 30;
      const nx = -Math.sin(la) * 7;
      const ny = Math.cos(la) * 7;
      out.push({
        d: `M ${f(px)} ${f(py)} Q ${f((px + lx) / 2 + nx)} ${f((py + ly) / 2 + ny)} ${f(lx)} ${f(ly)} Q ${f((px + lx) / 2 - nx)} ${f((py + ly) / 2 - ny)} ${f(px)} ${f(py)} Z`,
        fill: COLORS.olive,
      });
    }
  }
  return out;
};

/** Greek funerary stele (naiskos) in warm stone. */
export const naiskos = (cx: number, ground: number, w: number, h: number): InkPath[] => {
  const l = cx - w / 2;
  const r = cx + w / 2;
  const top = ground - h;
  const pedH = w * 0.2;
  return [
    {d: `M ${f(l)} ${f(ground - 30)} L ${f(l)} ${f(top + 20)} L ${f(r)} ${f(top + 20)} L ${f(r)} ${f(ground - 30)} Z`, fill: COLORS.sandPale, stroke: false},
    {d: `M ${f(l - 24)} ${f(ground)} L ${f(r + 24)} ${f(ground)} L ${f(r + 24)} ${f(ground - 30)} L ${f(l - 24)} ${f(ground - 30)} Z`, fill: COLORS.stone},
    {d: `M ${f(l)} ${f(ground - 30)} L ${f(l)} ${f(top + 20)} L ${f(l + 24)} ${f(top + 20)} L ${f(l + 24)} ${f(ground - 30)} Z`, fill: COLORS.stone},
    {d: `M ${f(r)} ${f(ground - 30)} L ${f(r)} ${f(top + 20)} L ${f(r - 24)} ${f(top + 20)} L ${f(r - 24)} ${f(ground - 30)} Z`, fill: COLORS.stone},
    {d: `M ${f(l - 14)} ${f(top + 20)} L ${f(r + 14)} ${f(top + 20)} L ${f(r + 14)} ${f(top)} L ${f(l - 14)} ${f(top)} Z`, fill: COLORS.stone},
    {d: `M ${f(l - 14)} ${f(top)} L ${f(cx)} ${f(top - pedH)} L ${f(r + 14)} ${f(top)} Z`, fill: COLORS.stone},
    `M ${f(l + 30)} ${f(top - 8)} L ${f(cx)} ${f(top - pedH + 18)} L ${f(r - 30)} ${f(top - 8)}`,
    `M ${f(l - 14)} ${f(top)} l -6 -14 M ${f(r + 14)} ${f(top)} l 6 -14 M ${f(cx)} ${f(top - pedH)} l 0 -14`,
  ];
};

/** Ruined Greek temple used as a backdrop. */
export const templeFront = (cx: number, ground: number, w: number, h: number, columns = 4, fill: string = COLORS.sandPale): InkPath[] => {
  const out: InkPath[] = [];
  const l = cx - w / 2;
  const colW = Math.max(16, w / (columns * 3.2));
  out.push({d: `M ${f(l - 20)} ${f(ground)} L ${f(l + w + 20)} ${f(ground)} L ${f(l + w + 10)} ${f(ground - 12)} L ${f(l - 10)} ${f(ground - 12)} Z`, fill: COLORS.sand});
  for (let i = 0; i < columns; i++) {
    const x = l + (w / (columns - 1)) * i;
    out.push({d: `M ${f(x - colW / 2)} ${f(ground - 12)} L ${f(x - colW / 2 + 2)} ${f(ground - h + 16)} L ${f(x + colW / 2 - 2)} ${f(ground - h + 16)} L ${f(x + colW / 2)} ${f(ground - 12)} Z`, fill});
  }
  out.push({d: `M ${f(l - 24)} ${f(ground - h + 16)} L ${f(l + w + 24)} ${f(ground - h + 16)} L ${f(l + w + 24)} ${f(ground - h - 8)} L ${f(l - 24)} ${f(ground - h - 8)} Z`, fill: COLORS.sand});
  out.push({d: `M ${f(l - 30)} ${f(ground - h - 8)} L ${f(cx)} ${f(ground - h - 8 - w * 0.22)} L ${f(l + w + 30)} ${f(ground - h - 8)} Z`, fill});
  return out;
};

/** Medieval castle with two towers, conical roofs and a pennant. */
export const castle = (cx: number, ground: number, s = 1): InkPath[] => {
  const S = (v: number) => v * s;
  const out: InkPath[] = [];
  out.push(crenBlock(cx - S(120), cx + S(120), ground, S(150), S(16), COLORS.sandLight));
  out.push(archGate(cx, ground, S(54), S(84), COLORS.camel));
  for (const dx of [-140, 140]) {
    const x = cx + S(dx);
    out.push({d: `M ${f(x - S(36))} ${f(ground)} L ${f(x - S(36))} ${f(ground - S(250))} L ${f(x + S(36))} ${f(ground - S(250))} L ${f(x + S(36))} ${f(ground)} Z`, fill: COLORS.sand});
    out.push({d: `M ${f(x - S(44))} ${f(ground - S(250))} L ${f(x)} ${f(ground - S(340))} L ${f(x + S(44))} ${f(ground - S(250))} Z`, fill: COLORS.terracotta});
    out.push({d: `M ${f(x - S(7))} ${f(ground - S(190))} L ${f(x - S(7))} ${f(ground - S(160))} L ${f(x + S(7))} ${f(ground - S(160))} L ${f(x + S(7))} ${f(ground - S(190))} Z`, fill: COLORS.ink});
  }
  const fx = cx + S(140);
  out.push(`M ${f(fx)} ${f(ground - S(340))} L ${f(fx)} ${f(ground - S(390))}`);
  out.push({d: `M ${f(fx)} ${f(ground - S(390))} L ${f(fx + S(40))} ${f(ground - S(378))} L ${f(fx)} ${f(ground - S(366))} Z`, fill: COLORS.terracotta});
  return out;
};

/** Low modern skyline, quiet taupe blocks with window ticks. */
export const skyline = (ground: number, x0 = 40, x1 = 1040, k = 1): InkPath[] => {
  const blocks = [
    [0.0, 0.1, 230],
    [0.1, 0.19, 330],
    [0.2, 0.3, 270],
    [0.31, 0.38, 410],
    [0.39, 0.5, 300],
    [0.52, 0.6, 360],
    [0.61, 0.72, 250],
    [0.73, 0.8, 440],
    [0.81, 0.9, 290],
    [0.91, 1.0, 340],
  ];
  const out: InkPath[] = [];
  blocks.forEach(([a, b, h0], i) => {
    const h = h0 * k;
    const l = x0 + (x1 - x0) * a;
    const r = x0 + (x1 - x0) * b;
    out.push({d: `M ${f(l)} ${f(ground)} L ${f(l)} ${f(ground - h)} L ${f(r)} ${f(ground - h)} L ${f(r)} ${f(ground)} Z`, fill: i % 2 ? COLORS.taupeLight : COLORS.sandLight, color: COLORS.taupe});
    const win: string[] = [];
    for (let y = ground - h + 24; y < ground - 40; y += 48) win.push(`M ${f(l + 14)} ${f(y)} L ${f(r - 14)} ${f(y)}`);
    if (win.length) out.push({d: win.join(' '), width: 1.4, color: COLORS.taupe});
  });
  return out;
};

/** Stone relief slab (carved tablet) with cuneiform-like marks. */
export const reliefSlab = (x: number, y: number, w: number, h: number): InkPath[] => {
  const marks: string[] = [];
  for (let row = 0; row < 6; row++) {
    for (let col = 0; col < 2; col++) {
      const mx = x + 34 + col * 34;
      const my = y + 120 + row * 70;
      marks.push(`M ${mx} ${my} l 14 0 M ${mx + 7} ${my} l 0 22 M ${mx} ${my + 30} l 10 -8 l 10 8`);
    }
  }
  return [
    {
      d: `M ${x + 14} ${y + h} C ${x - 6} ${y + h * 0.6} ${x + 6} ${y + h * 0.2} ${x + 22} ${y + 8} C ${x + w * 0.35} ${y - 8} ${x + w * 0.7} ${y + 6} ${x + w - 10} ${y + 2} C ${x + w + 8} ${y + h * 0.3} ${x + w - 4} ${y + h * 0.7} ${x + w + 6} ${y + h} Z`,
      fill: COLORS.stone,
    },
    {d: `M ${x + 130} ${y + h - 40} L ${x + 130} ${y + 150} C ${x + 130} ${y + 80} ${x + w - 60} ${y + 80} ${x + w - 60} ${y + 150} L ${x + w - 60} ${y + h - 40} Z`, fill: '#E6D9C3', color: '#8E7B66'},
    {d: marks.join(' '), color: '#8E7B66', width: 2.2},
  ];
};

/** Hourglass. `t` 0→1 drains the upper bulb into the lower one. */
export const hourglass = (cx: number, cy: number, t: number, s = 1): {frame: InkPath[]; sand: string[]; stream: string | null} => {
  const S = (v: number) => v * s;
  const H = S(190);
  const W = S(120);
  const neck = S(9);
  const top = cy - H;
  const bot = cy + H;
  const frame: InkPath[] = [
    {d: `M ${f(cx - W - S(26))} ${f(top - S(26))} L ${f(cx + W + S(26))} ${f(top - S(26))} L ${f(cx + W + S(26))} ${f(top)} L ${f(cx - W - S(26))} ${f(top)} Z`, fill: COLORS.camel},
    {d: `M ${f(cx - W - S(26))} ${f(bot)} L ${f(cx + W + S(26))} ${f(bot)} L ${f(cx + W + S(26))} ${f(bot + S(26))} L ${f(cx - W - S(26))} ${f(bot + S(26))} Z`, fill: COLORS.camel},
    `M ${f(cx - W - S(12))} ${f(top)} L ${f(cx - W - S(12))} ${f(bot)} M ${f(cx + W + S(12))} ${f(top)} L ${f(cx + W + S(12))} ${f(bot)}`,
    {
      d: `M ${f(cx - W)} ${f(top)} C ${f(cx - W)} ${f(top + H * 0.6)} ${f(cx - neck)} ${f(cy - S(30))} ${f(cx - neck)} ${f(cy)} C ${f(cx - neck)} ${f(cy + S(30))} ${f(cx - W)} ${f(bot - H * 0.6)} ${f(cx - W)} ${f(bot)} L ${f(cx + W)} ${f(bot)} C ${f(cx + W)} ${f(bot - H * 0.6)} ${f(cx + neck)} ${f(cy + S(30))} ${f(cx + neck)} ${f(cy)} C ${f(cx + neck)} ${f(cy - S(30))} ${f(cx + W)} ${f(top + H * 0.6)} ${f(cx + W)} ${f(top)} Z`,
      fill: COLORS.paper,
    },
  ];
  // upper sand: a cone whose surface sinks; lower: a mound that grows
  const k = Math.min(1, Math.max(0, t));
  const upY = top + S(40) + (cy - S(14) - (top + S(40))) * Math.pow(k, 0.85);
  const halfAt = (y: number) => {
    const u = (y - top) / H; // 0 top → 1 neck
    return Math.max(neck, W * (1 - Math.pow(u, 1.6)) + neck * Math.pow(u, 1.6) - S(4));
  };
  const sand: string[] = [];
  if (k < 0.99) {
    const hw = halfAt(upY);
    sand.push(`M ${f(cx - hw)} ${f(upY)} Q ${f(cx)} ${f(upY + S(10))} ${f(cx + hw)} ${f(upY)} L ${f(cx + neck - 2)} ${f(cy - S(4))} L ${f(cx - neck + 2)} ${f(cy - S(4))} Z`);
  }
  const moundH = S(20) + S(150) * Math.pow(k, 0.9);
  const mw = W - S(6);
  sand.push(`M ${f(cx - mw)} ${f(bot - 2)} C ${f(cx - mw * 0.6)} ${f(bot - moundH * 0.55)} ${f(cx - S(16))} ${f(bot - moundH)} ${f(cx)} ${f(bot - moundH)} C ${f(cx + S(16))} ${f(bot - moundH)} ${f(cx + mw * 0.6)} ${f(bot - moundH * 0.55)} ${f(cx + mw)} ${f(bot - 2)} Z`);
  const stream = k > 0.01 && k < 0.99 ? `M ${f(cx)} ${f(cy - S(4))} L ${f(cx)} ${f(bot - moundH)}` : null;
  return {frame, sand, stream};
};
