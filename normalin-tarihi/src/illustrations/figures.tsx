import React from 'react';
import {Ink, InkPath} from '../components/Ink';
import {COLORS} from '../brand/theme';
import {OPEN_HAND, Tone, skinOf} from './hands';

/*
 * Parametric historical figure: thin charcoal outlines + flat muted fills.
 *
 * Local coordinates: feet on y = 0, figure faces +x, ~640 units tall.
 * Mirror the whole figure with `facing={-1}`. The near arm is driven by a
 * wrist target (two-bone IK) so gestures stay anatomically plausible.
 */

export type Headwear = 'none' | 'band' | 'cap' | 'assyrian' | 'babylonian' | 'laurel';
export type Beard = 'none' | 'long' | 'short';
export type Hair = 'long' | 'short' | 'curly';
export type Robe = 'mesopotamian' | 'royal' | 'greek' | 'himation' | 'tunic' | 'suit';
export type ArmSleeve = 'short' | 'long' | 'royal' | 'bare' | 'suit';

export type Pt = {x: number; y: number};

export type FigureSpec = {
  headwear: Headwear;
  beard: Beard;
  hair: Hair;
  robe: Robe;
  sleeve: ArmSleeve;
  /** main garment colour */
  cloth: string;
  /** shawl / drape / cloak / band colour */
  accent: string;
  /** headwear colour (defaults to accent) */
  hat?: string;
  /** trousers / hose colour for legged costumes */
  legs?: string;
  skin?: Tone;
  hairColor?: string;
};

/** Carved-relief rendering: every fill becomes stone, lines go soft brown. */
export type StoneMode = {fill: string; line: string};

export const SHOULDER: Pt = {x: 2, y: -446};
const UPPER = 108;
const FORE = 98;
const HAND_SCALE = 0.3;
const HEAD: Pt = {x: 6, y: -556};
const HEAD_SCALE = 0.8;
const HIP: Pt = {x: 0, y: -236};
const LEG = 236;

/** Relaxed wrist position (arm hanging, slightly forward). */
export const REST_WRIST: Pt = {x: 18, y: SHOULDER.y + 196};

const fmt = (n: number) => n.toFixed(1);

const FACE =
  'M -14 52 C -34 40 -42 10 -38 -14 C -34 -38 -12 -52 10 -50 C 32 -48 44 -32 44 -14 C 44 -6 46 0 50 6 C 54 14 58 20 56 24 C 54 27 50 27 47 27 C 48 31 48 34 46 36 C 47 39 46 42 43 44 C 44 50 40 56 32 58 C 22 60 12 56 6 52';

const headPaths = (spec: FigureSpec, c: (x: string) => string): InkPath[] => {
  const out: InkPath[] = [];
  const hairC = c(spec.hairColor ?? COLORS.hair);
  const hat = c(spec.hat ?? spec.accent);
  const skin = c(skinOf(spec.skin ?? 'light'));
  if (spec.hair === 'long') {
    out.push({d: 'M -38 -14 C -50 20 -48 60 -38 94 C -28 98 -18 96 -10 90 L -2 20 Z', fill: hairC});
  }
  out.push({d: 'M -14 50 L -14 84 L 12 84 L 8 50 Z', fill: skin, stroke: false});
  out.push({d: FACE + ' L -14 52 Z', fill: skin});
  out.push('M -14 52 C -12 62 -12 72 -14 84');
  out.push('M 8 52 C 10 60 12 70 12 84');
  out.push('M -2 2 C -10 0 -12 16 -4 18');
  out.push({d: 'M 28 -2 C 32 -6 38 -6 41 -2 C 38 0 32 0 28 -2 Z', fill: COLORS.ink});
  out.push('M 28 -11 C 34 -14 40 -13 45 -10');
  if (spec.beard === 'long') {
    out.push({d: 'M 46 34 C 50 56 50 80 44 98 C 30 102 14 102 2 96 C -2 78 0 60 4 46 C 14 40 30 38 46 34 Z', fill: hairC});
    out.push('M 46 34 C 40 38 34 38 28 35');
    out.push('M 8 60 C 14 64 20 56 26 60 C 32 64 38 56 44 60');
    out.push('M 6 78 C 12 82 18 74 24 78 C 30 82 36 74 42 78');
  } else if (spec.beard === 'short') {
    out.push({d: 'M 46 37 C 48 46 44 58 32 62 C 20 64 10 60 4 52 C 10 46 20 42 30 40 C 36 40 42 38 46 37 Z', fill: hairC});
  }
  if (spec.hair === 'long') {
    out.push('M -46 46 C -40 50 -34 42 -28 46 C -22 50 -18 44 -14 46');
    out.push('M -44 70 C -38 74 -32 66 -26 70 C -20 74 -16 68 -12 70');
  }
  if (spec.hair === 'curly') {
    out.push({d: 'M -38 -10 C -48 -40 -22 -62 8 -58 C 32 -56 48 -42 46 -22 C 30 -30 10 -26 -6 -22 C -20 -14 -30 -6 -38 -10 Z', fill: hairC});
  } else if (spec.hair === 'short') {
    out.push({d: 'M -38 -8 C -44 -40 -20 -58 8 -56 C 30 -54 46 -40 44 -24 C 26 -30 8 -28 -8 -22 C -20 -12 -30 -4 -38 -8 Z', fill: hairC});
  } else {
    out.push({d: 'M -38 -14 C -40 -40 -18 -54 8 -52 C 30 -50 44 -38 44 -22 C 20 -26 -10 -24 -38 -14 Z', fill: hairC});
  }
  switch (spec.headwear) {
    case 'band':
      out.push({d: 'M -40 -22 C -18 -30 20 -30 44 -22 L 45 -14 C 20 -22 -18 -22 -40 -14 Z', fill: hat});
      break;
    case 'cap':
      out.push({d: 'M -40 -16 C -40 -50 -16 -64 10 -62 C 34 -60 46 -44 45 -16 C 22 -24 -16 -24 -40 -16 Z', fill: hat});
      out.push('M -39 -26 C -16 -34 22 -34 45 -26');
      break;
    case 'assyrian':
      out.push({d: 'M -40 -14 L -33 -98 C -12 -104 18 -104 38 -98 L 45 -14 C 20 -22 -14 -22 -40 -14 Z', fill: hat});
      out.push({d: 'M -38 -34 C -12 -42 20 -42 44 -34 L 42 -58 C 20 -64 -12 -64 -36 -58 Z', fill: c(COLORS.terracotta)});
      out.push({d: 'M -1 -103 L 5 -122 L 11 -103 Z', fill: hat});
      break;
    case 'babylonian':
      out.push({d: 'M -40 -14 C -44 -62 -36 -96 4 -100 C 42 -98 48 -62 45 -14 C 20 -22 -14 -22 -40 -14 Z', fill: hat});
      out.push({d: 'M -41 -32 C -14 -40 20 -40 46 -32 L 45 -18 C 20 -26 -14 -26 -40 -18 Z', fill: c(COLORS.terracotta)});
      break;
    case 'laurel': {
      const leaves: string[] = [];
      [-32, -18, -4, 10, 24, 36].forEach((x, i) => {
        const y = -27 - Math.sin((i / 5) * Math.PI) * 6;
        leaves.push(`M ${x} ${fmt(y)} C ${x + 3} ${fmt(y - 10)} ${x + 11} ${fmt(y - 12)} ${x + 12} ${fmt(y - 8)} C ${x + 10} ${fmt(y - 2)} ${x + 4} ${fmt(y)} ${x} ${fmt(y)} Z`);
      });
      out.push('M -40 -22 C -16 -34 22 -34 44 -24');
      out.push({d: leaves.join(' '), fill: c(COLORS.olive)});
      break;
    }
    case 'none':
      break;
  }
  return out;
};

const robePaths = (spec: FigureSpec, c: (x: string) => string): {body: InkPath[]; back: InkPath[]} => {
  const cloth = c(spec.cloth);
  const accent = c(spec.accent);
  const back: InkPath[] = [];
  const body: InkPath[] = [];
  const feet = {d: 'M 40 -18 C 50 -6 70 -2 88 -4 C 94 -7 90 -14 80 -16 Z', fill: c(COLORS.camel)};
  switch (spec.robe) {
    case 'mesopotamian':
    case 'royal': {
      body.push(feet);
      body.push({
        d: 'M 20 -490 C 44 -488 58 -478 60 -458 C 64 -330 70 -150 74 -22 C 36 -14 -36 -14 -70 -22 C -68 -150 -64 -330 -60 -458 C -58 -478 -42 -488 -20 -490 Z',
        fill: cloth,
      });
      body.push({d: 'M 56 -446 C 16 -390 -26 -318 -62 -264 L -64 -214 C -14 -272 26 -334 62 -386 Z', fill: accent});
      const ticks: string[] = [];
      for (let i = 0; i <= 8; i++) {
        const t = i / 8;
        ticks.push(`M ${fmt(62 - 126 * t)} ${fmt(-386 + 172 * t - Math.sin(t * Math.PI) * 6)} l -5 13`);
      }
      body.push(ticks.join(' '));
      body.push('M 34 -300 C 40 -210 46 -120 50 -34');
      body.push('M -26 -190 C -24 -130 -22 -80 -22 -26');
      body.push({d: 'M 73 -52 C 36 -44 -36 -44 -69 -52 L -70 -22 C -36 -14 36 -14 74 -22 Z', fill: accent});
      if (spec.robe === 'royal') {
        const dots: string[] = [];
        for (let i = 0; i < 7; i++) dots.push(`M ${-56 + i * 18} -37 l 4 -5 l 4 5 l -4 5 z`);
        body.push({d: dots.join(' '), fill: c(COLORS.linen)});
        body.push('M 70 -110 C 36 -102 -36 -102 -67 -110');
      }
      break;
    }
    case 'greek':
    case 'himation':
      body.push(feet);
      body.push({
        d: 'M 20 -490 C 46 -488 60 -476 62 -456 C 66 -330 72 -170 84 -24 C 44 -16 -44 -16 -80 -24 C -72 -170 -66 -330 -62 -456 C -60 -478 -44 -488 -20 -490 Z',
        fill: cloth,
      });
      body.push({d: 'M 58 -440 C 10 -390 -28 -330 -62 -310 L -64 -232 C -24 -238 26 -258 62 -310 Z', fill: accent});
      body.push('M 36 -256 C 44 -170 52 -100 60 -26');
      body.push('M 8 -246 C 10 -160 14 -90 16 -22');
      body.push('M -26 -238 C -26 -160 -28 -90 -32 -20');
      body.push('M -48 -234 C -50 -150 -56 -80 -62 -24');
      body.push('M 24 -436 C 22 -392 14 -360 4 -338');
      break;
    case 'tunic':
      back.push({d: 'M -20 -488 C -60 -470 -80 -300 -96 -130 C -60 -118 -30 -120 -10 -128 Z', fill: accent});
      body.push({
        d: 'M 20 -490 C 44 -488 58 -478 60 -458 C 62 -380 66 -260 70 -150 C 30 -140 -30 -140 -64 -150 C -62 -260 -62 -380 -60 -458 C -58 -478 -42 -488 -20 -490 Z',
        fill: cloth,
      });
      body.push({d: 'M -62 -262 C -20 -254 30 -254 64 -262 L 64 -246 C 30 -238 -20 -238 -62 -246 Z', fill: c(COLORS.camel)});
      body.push('M 10 -230 C 14 -200 18 -170 20 -146');
      break;
    case 'suit':
      body.push({
        d: 'M 20 -490 C 44 -488 56 -478 58 -458 C 60 -380 62 -290 62 -218 C 30 -208 -30 -208 -58 -218 C -58 -290 -58 -380 -56 -458 C -54 -478 -40 -488 -20 -490 Z',
        fill: cloth,
      });
      body.push({d: 'M 14 -490 L 44 -474 L 30 -400 Z', fill: c(COLORS.linen)});
      body.push('M 30 -400 L 40 -300 L 60 -296');
      body.push('M 44 -474 L 36 -440 L 42 -420');
      break;
  }
  return {body, back};
};

const legPaths = (spec: FigureSpec, swing: number, c: (x: string) => string): InkPath[] => {
  if (spec.robe !== 'tunic' && spec.robe !== 'suit') return [];
  const w = spec.robe === 'suit' ? 19 : 15;
  const col = c(spec.legs ?? COLORS.taupe);
  const shoe = c(spec.robe === 'suit' ? COLORS.hair : COLORS.camel);
  const leg = (deg: number): InkPath[] => {
    const a = (deg * Math.PI) / 180;
    const fx = HIP.x + Math.sin(a) * LEG;
    const fy = HIP.y + Math.cos(a) * LEG;
    const nx = Math.cos(a);
    const ny = -Math.sin(a);
    const p = (x: number, y: number) => `${fmt(x)} ${fmt(y)}`;
    return [
      {
        d: `M ${p(HIP.x + nx * w, HIP.y + ny * w)} L ${p(fx + nx * (w - 3), fy + ny * (w - 3))} L ${p(fx - nx * (w - 3), fy - ny * (w - 3))} L ${p(HIP.x - nx * w, HIP.y - ny * w)} Z`,
        fill: col,
      },
      {d: `M ${p(fx - 14, fy - 2)} C ${p(fx - 10, fy - 16)} ${p(fx + 22, fy - 16)} ${p(fx + 36, fy - 6)} C ${p(fx + 40, fy)} ${p(fx + 30, fy + 2)} ${p(fx - 14, fy + 1)} Z`, fill: shoe},
    ];
  };
  return [...leg(-swing), ...leg(swing)];
};

const twoBoneIK = (s: Pt, target: Pt, l1: number, l2: number) => {
  const dx = target.x - s.x;
  const dy = target.y - s.y;
  const reach = l1 + l2 - 0.5;
  let dist = Math.hypot(dx, dy);
  const theta = Math.atan2(dy, dx);
  dist = Math.min(dist, reach);
  const cosPhi = (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist);
  const phi = Math.acos(Math.max(-1, Math.min(1, cosPhi)));
  const elbow = {x: s.x + l1 * Math.cos(theta + phi), y: s.y + l1 * Math.sin(theta + phi)};
  const wrist = {x: s.x + dist * Math.cos(theta), y: s.y + dist * Math.sin(theta)};
  return {elbow, wrist};
};

const norm = (a: Pt, b: Pt) => {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const l = Math.hypot(dx, dy) || 1;
  return {x: -dy / l, y: dx / l};
};

export const armGeometry = (target: Pt) => {
  const {elbow, wrist} = twoBoneIK(SHOULDER, target, UPPER, FORE);
  const n1 = norm(SHOULDER, elbow);
  const n2 = norm(elbow, wrist);
  const nE = {x: (n1.x + n2.x) / 2, y: (n1.y + n2.y) / 2};
  const w = [18, 14.5, 11];
  const off = (p: Pt, n: Pt, k: number) => ({x: p.x + n.x * k, y: p.y + n.y * k});
  const sA = off(SHOULDER, n1, w[0]);
  const sB = off(SHOULDER, n1, -w[0]);
  const eA = off(elbow, nE, w[1]);
  const eB = off(elbow, nE, -w[1]);
  const wA = off(wrist, n2, w[2]);
  const wB = off(wrist, n2, -w[2]);
  const P = (p: Pt) => `${fmt(p.x)} ${fmt(p.y)}`;
  const angle = (Math.atan2(wrist.y - elbow.y, wrist.x - elbow.x) * 180) / Math.PI;
  return {elbow, wrist, n1, n2, sA, sB, eA, eB, wA, wB, P, angle};
};

export const Figure: React.FC<{
  spec: FigureSpec;
  x: number;
  y: number;
  scale?: number;
  facing?: 1 | -1;
  /** wrist target in the figure's local coordinates */
  wrist?: Pt;
  showHand?: boolean;
  draw?: number;
  /** extra local-space paths drawn over the robe (props such as a sword) */
  extras?: InkPath[];
  /** leg swing in degrees for walking costumes */
  swing?: number;
  stone?: StoneMode;
}> = ({spec, x, y, scale = 1, facing = 1, wrist = REST_WRIST, showHand = true, draw = 1, extras = [], swing = 0, stone}) => {
  const c = (col: string) => (stone ? stone.fill : col);
  const lineColor = stone?.line;
  const head = headPaths(spec, c);
  const robe = robePaths(spec, c);
  const legs = legPaths(spec, swing, c);
  const arm = armGeometry(wrist);
  const {P} = arm;
  const skin = c(skinOf(spec.skin ?? 'light'));
  const sleeveCol = spec.sleeve === 'bare' ? skin : c(spec.cloth);
  const armFill = `M ${P(arm.sA)} Q ${P(arm.eA)} ${P(arm.wA)} L ${P(arm.wB)} Q ${P(arm.eB)} ${P(arm.sB)} Z`;
  const armTop = `M ${P(arm.sA)} Q ${P(arm.eA)} ${P(arm.wA)}`;
  const armBot = `M ${P(arm.sB)} Q ${P(arm.eB)} ${P(arm.wB)}`;
  const along = (k: number, t: number) => {
    const p = {x: arm.elbow.x + (arm.wrist.x - arm.elbow.x) * t, y: arm.elbow.y + (arm.wrist.y - arm.elbow.y) * t};
    return {x: p.x + arm.n2.x * k, y: p.y + arm.n2.y * k};
  };
  const forearmFrom = (t: number) =>
    `M ${P(along(12.5, t))} L ${P(arm.wA)} L ${P(arm.wB)} L ${P(along(-12.5, t))} Z`;
  const armParts: InkPath[] = [{d: armFill, fill: sleeveCol, stroke: false}];
  if (spec.sleeve === 'short') {
    armParts.push({d: forearmFrom(0.08), fill: skin, stroke: false});
    armParts.push(`M ${P(along(14, 0.08))} L ${P(along(-14, 0.08))}`);
    armParts.push({d: `M ${P(along(11.5, 0.8))} L ${P(along(11.5, 0.9))} L ${P(along(-11.5, 0.9))} L ${P(along(-11.5, 0.8))} Z`, fill: c(COLORS.camel)});
  } else if (spec.sleeve === 'royal') {
    armParts.push({d: forearmFrom(0.86), fill: skin, stroke: false});
    armParts.push({d: `M ${P(along(12, 0.7))} L ${P(along(11.5, 0.84))} L ${P(along(-11.5, 0.84))} L ${P(along(-12, 0.7))} Z`, fill: c(spec.accent)});
  } else if (spec.sleeve === 'suit') {
    armParts.push({d: `M ${P(along(11.5, 0.86))} L ${P(arm.wA)} L ${P(arm.wB)} L ${P(along(-11.5, 0.86))} Z`, fill: c(COLORS.linen)});
  } else if (spec.sleeve === 'long') {
    armParts.push(`M ${P(along(11.5, 0.9))} L ${P(along(-11.5, 0.9))}`);
  }
  armParts.push(armTop, armBot);

  const n = 4;
  const seg = (i: number) => Math.min(1, Math.max(0, draw * n - i * 0.8));
  return (
    <g transform={`translate(${x} ${y}) scale(${scale * facing} ${scale})`}>
      <Ink paths={[...robe.back, ...legs]} draw={seg(0)} overlap={0.6} color={lineColor} />
      <Ink paths={[...robe.body, ...extras]} draw={seg(0)} overlap={0.6} color={lineColor} />
      <Ink paths={armParts} draw={seg(2)} overlap={0.5} color={lineColor} />
      <g transform={`translate(${HEAD.x} ${HEAD.y}) scale(${HEAD_SCALE})`}>
        <Ink paths={head} draw={seg(1)} overlap={0.5} color={lineColor} />
      </g>
      {showHand ? (
        <g transform={`translate(${fmt(arm.wrist.x)} ${fmt(arm.wrist.y)}) rotate(${fmt(arm.angle)}) scale(${HAND_SCALE})`}>
          <Ink paths={[{d: OPEN_HAND[0] + ' L -6 -40 Z', fill: skin}, ...OPEN_HAND.slice(1)]} draw={seg(3)} overlap={0.5} color={lineColor} />
        </g>
      ) : null}
    </g>
  );
};

/** World-space wrist target → figure local coordinates. */
export const toLocal = (world: Pt, fig: {x: number; y: number; scale: number; facing: 1 | -1}): Pt => ({
  x: ((world.x - fig.x) / fig.scale) * fig.facing,
  y: (world.y - fig.y) / fig.scale,
});

export const HAND_LEN = 225 * HAND_SCALE;

/** Sheathed sword hanging at the hip (the "empty hand" theory prop). */
export const SheathedSword: InkPath[] = [
  {d: 'M 36 -292 L 50 -288 L 18 -120 C 14 -112 6 -112 4 -120 Z', fill: COLORS.camel},
  {d: 'M 24 -306 L 64 -296 L 62 -290 L 22 -300 Z', fill: COLORS.taupe},
  {d: 'M 42 -302 L 48 -334 L 54 -332 L 48 -300 Z', fill: COLORS.hair},
];
