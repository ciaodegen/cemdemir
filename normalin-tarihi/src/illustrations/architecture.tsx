/*
 * Architecture & landscape strokes. Every helper returns plain path strings
 * in canvas coordinates so scenes can feed them straight into <Ink>.
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

/** Mud-brick wall segment with crenellated top, from (x0..x1), ground at y. */
export const wall = (x0: number, x1: number, ground: number, h: number, step = 14): string[] => [
  `M ${f(x0)} ${f(ground)} L ${f(x0)} ${f(ground - h)}`,
  crenellations(x0, x1, ground - h, step),
  `M ${f(x1)} ${f(ground - h)} L ${f(x1)} ${f(ground)}`,
];

export const tower = (cx: number, ground: number, w: number, h: number): string[] => [
  ...wall(cx - w / 2, cx + w / 2, ground, h, w / 5),
  `M ${f(cx - 5)} ${f(ground - h * 0.62)} L ${f(cx - 5)} ${f(ground - h * 0.5)} M ${f(cx + 5)} ${f(ground - h * 0.62)} L ${f(cx + 5)} ${f(ground - h * 0.5)}`,
];

export const archGate = (cx: number, ground: number, w: number, h: number): string =>
  `M ${f(cx - w / 2)} ${f(ground)} L ${f(cx - w / 2)} ${f(ground - h + w / 2)} A ${f(w / 2)} ${f(w / 2)} 0 0 1 ${f(cx + w / 2)} ${f(ground - h + w / 2)} L ${f(cx + w / 2)} ${f(ground)}`;

/** Stepped ziggurat with a central stair and a small shrine on top. */
export const ziggurat = (cx: number, ground: number, baseW: number, tierH: number, tiers = 3): string[] => {
  const out: string[] = [];
  let w = baseW;
  let y = ground;
  for (let i = 0; i < tiers; i++) {
    const top = y - tierH;
    out.push(`M ${f(cx - w / 2)} ${f(y)} L ${f(cx - w / 2 + 6)} ${f(top)} L ${f(cx + w / 2 - 6)} ${f(top)} L ${f(cx + w / 2)} ${f(y)}`);
    y = top;
    w *= 0.66;
  }
  // shrine
  const sw = w * 0.8;
  out.push(`M ${f(cx - sw / 2)} ${f(y)} L ${f(cx - sw / 2)} ${f(y - tierH * 0.8)} L ${f(cx + sw / 2)} ${f(y - tierH * 0.8)} L ${f(cx + sw / 2)} ${f(y)}`);
  out.push(`M ${f(cx - 6)} ${f(y)} L ${f(cx - 6)} ${f(y - tierH * 0.45)} L ${f(cx + 6)} ${f(y - tierH * 0.45)} L ${f(cx + 6)} ${f(y)}`);
  // central stair
  out.push(`M ${f(cx - 12)} ${f(ground)} L ${f(cx - 8)} ${f(ground - tierH * tiers)}`);
  out.push(`M ${f(cx + 12)} ${f(ground)} L ${f(cx + 8)} ${f(ground - tierH * tiers)}`);
  return out;
};

/** Date palm: curved trunk with ring ticks and drooping fronds. */
export const palm = (x: number, ground: number, h: number, lean = 10): string[] => {
  const tx = x + lean;
  const ty = ground - h;
  const out: string[] = [];
  out.push(`M ${f(x - 4)} ${f(ground)} Q ${f(x - 4 + lean * 0.2)} ${f(ground - h * 0.5)} ${f(tx - 2)} ${f(ty)}`);
  out.push(`M ${f(x + 4)} ${f(ground)} Q ${f(x + 4 + lean * 0.2)} ${f(ground - h * 0.5)} ${f(tx + 2)} ${f(ty)}`);
  const ticks: string[] = [];
  for (let i = 1; i < 7; i++) {
    const t = i / 7;
    const cx = x + lean * t * t;
    const cy = ground - h * t;
    ticks.push(`M ${f(cx - 4)} ${f(cy)} L ${f(cx + 4)} ${f(cy - 3)}`);
  }
  out.push(ticks.join(' '));
  const fronds: [number, number][] = [
    [-1, 0.2],
    [-0.8, -0.35],
    [-0.2, -0.6],
    [0.4, -0.5],
    [0.9, -0.2],
    [1, 0.25],
  ];
  const r = h * 0.42;
  out.push(
    fronds
      .map(([dx, dy]) => {
        const ex = tx + dx * r;
        const ey = ty + dy * r * 0.6 + r * 0.35;
        const cx = tx + dx * r * 0.6;
        const cy = ty + dy * r * 0.9 - r * 0.15;
        return `M ${f(tx)} ${f(ty)} Q ${f(cx)} ${f(cy)} ${f(ex)} ${f(ey)}`;
      })
      .join(' '),
  );
  return out;
};

export const hills = (y: number, x0 = -20, x1 = 1100): string[] => [
  `M ${x0} ${y} C ${x0 + 160} ${y - 40} ${x0 + 260} ${y - 46} ${x0 + 380} ${y - 12} C ${x0 + 470} ${y + 8} ${x0 + 560} ${y - 30} ${x0 + 680} ${y - 26}`,
  `M ${x1 - 420} ${y - 8} C ${x1 - 330} ${y - 50} ${x1 - 220} ${y - 54} ${x1 - 120} ${y - 22} C ${x1 - 70} ${y - 8} ${x1 - 30} ${y - 10} ${x1} ${y - 16}`,
];

/** Ionic column, base at (x, ground). */
export const ionicColumn = (x: number, ground: number, h: number, w = 46): string[] => {
  const top = ground - h;
  const hw = w / 2;
  return [
    `M ${f(x - hw - 12)} ${f(ground)} L ${f(x + hw + 12)} ${f(ground)} M ${f(x - hw - 8)} ${f(ground - 10)} L ${f(x + hw + 8)} ${f(ground - 10)}`,
    `M ${f(x - hw)} ${f(ground - 10)} L ${f(x - hw + 3)} ${f(top + 22)}`,
    `M ${f(x + hw)} ${f(ground - 10)} L ${f(x + hw - 3)} ${f(top + 22)}`,
    `M ${f(x - hw * 0.35)} ${f(ground - 16)} L ${f(x - hw * 0.33)} ${f(top + 28)} M ${f(x + hw * 0.35)} ${f(ground - 16)} L ${f(x + hw * 0.33)} ${f(top + 28)}`,
    // capital with volutes
    `M ${f(x - hw - 14)} ${f(top + 10)} L ${f(x + hw + 14)} ${f(top + 10)} M ${f(x - hw - 18)} ${f(top)} L ${f(x + hw + 18)} ${f(top)}`,
    `M ${f(x - hw - 4)} ${f(top + 10)} c -12 0 -14 14 -4 16 c 6 1 8 -6 3 -8 M ${f(x + hw + 4)} ${f(top + 10)} c 12 0 14 14 4 16 c -6 1 -8 -6 -3 -8`,
  ];
};

/** Mediterranean cypress silhouette. */
export const cypress = (x: number, ground: number, h: number): string[] => [
  `M ${f(x)} ${f(ground)} C ${f(x - 30)} ${f(ground - h * 0.25)} ${f(x - 26)} ${f(ground - h * 0.7)} ${f(x)} ${f(ground - h)} C ${f(x + 26)} ${f(ground - h * 0.7)} ${f(x + 30)} ${f(ground - h * 0.25)} ${f(x)} ${f(ground)}`,
  `M ${f(x)} ${f(ground)} L ${f(x)} ${f(ground + 14)}`,
];

/** Olive sprig: a stem with paired leaves. */
export const oliveBranch = (x: number, y: number, len: number, angle = -60): string[] => {
  const a = (angle * Math.PI) / 180;
  const ex = x + Math.cos(a) * len;
  const ey = y + Math.sin(a) * len;
  const out = [`M ${f(x)} ${f(y)} Q ${f(x + Math.cos(a) * len * 0.5 + 10)} ${f(y + Math.sin(a) * len * 0.5)} ${f(ex)} ${f(ey)}`];
  const leaves: string[] = [];
  for (let i = 1; i <= 5; i++) {
    const t = i / 6;
    const px = x + (ex - x) * t + 4;
    const py = y + (ey - y) * t;
    for (const side of [-1, 1]) {
      const la = a + side * 0.9;
      const lx = px + Math.cos(la) * 26;
      const ly = py + Math.sin(la) * 26;
      const nx = -Math.sin(la) * 6;
      const ny = Math.cos(la) * 6;
      leaves.push(
        `M ${f(px)} ${f(py)} Q ${f((px + lx) / 2 + nx)} ${f((py + ly) / 2 + ny)} ${f(lx)} ${f(ly)} Q ${f((px + lx) / 2 - nx)} ${f((py + ly) / 2 - ny)} ${f(px)} ${f(py)}`,
      );
    }
  }
  out.push(leaves.join(' '));
  return out;
};

/** Greek funerary stele (naiskos): pediment, pilasters, base. Returns frame strokes. */
export const naiskos = (cx: number, ground: number, w: number, h: number): string[] => {
  const l = cx - w / 2;
  const r = cx + w / 2;
  const top = ground - h;
  const pedH = w * 0.2;
  return [
    `M ${f(l - 24)} ${f(ground)} L ${f(r + 24)} ${f(ground)} L ${f(r + 24)} ${f(ground - 30)} L ${f(l - 24)} ${f(ground - 30)} Z`,
    `M ${f(l)} ${f(ground - 30)} L ${f(l)} ${f(top + 20)} M ${f(l + 22)} ${f(ground - 30)} L ${f(l + 22)} ${f(top + 20)}`,
    `M ${f(r)} ${f(ground - 30)} L ${f(r)} ${f(top + 20)} M ${f(r - 22)} ${f(ground - 30)} L ${f(r - 22)} ${f(top + 20)}`,
    `M ${f(l - 14)} ${f(top + 20)} L ${f(r + 14)} ${f(top + 20)} L ${f(r + 14)} ${f(top)} L ${f(l - 14)} ${f(top)} Z`,
    `M ${f(l - 14)} ${f(top)} L ${f(cx)} ${f(top - pedH)} L ${f(r + 14)} ${f(top)}`,
    `M ${f(l + 30)} ${f(top - 8)} L ${f(cx)} ${f(top - pedH + 18)} L ${f(r - 30)} ${f(top - 8)}`,
    `M ${f(l - 14)} ${f(top)} l -6 -14 M ${f(r + 14)} ${f(top)} l 6 -14 M ${f(cx)} ${f(top - pedH)} l 0 -14`,
  ];
};

/** Simple Greek temple front used as a backdrop. */
export const templeFront = (cx: number, ground: number, w: number, h: number, columns = 4): string[] => {
  const out: string[] = [];
  const l = cx - w / 2;
  const colW = 26;
  out.push(`M ${f(l - 20)} ${f(ground)} L ${f(l + w + 20)} ${f(ground)} M ${f(l - 10)} ${f(ground - 12)} L ${f(l + w + 10)} ${f(ground - 12)}`);
  for (let i = 0; i < columns; i++) {
    const x = l + (w / (columns - 1)) * i;
    out.push(`M ${f(x - colW / 2)} ${f(ground - 12)} L ${f(x - colW / 2 + 2)} ${f(ground - h + 16)} M ${f(x + colW / 2)} ${f(ground - 12)} L ${f(x + colW / 2 - 2)} ${f(ground - h + 16)}`);
  }
  out.push(`M ${f(l - 24)} ${f(ground - h + 16)} L ${f(l + w + 24)} ${f(ground - h + 16)} L ${f(l + w + 24)} ${f(ground - h - 8)} L ${f(l - 24)} ${f(ground - h - 8)} Z`);
  out.push(`M ${f(l - 30)} ${f(ground - h - 8)} L ${f(cx)} ${f(ground - h - 8 - w * 0.22)} L ${f(l + w + 30)} ${f(ground - h - 8)} Z`);
  return out;
};
