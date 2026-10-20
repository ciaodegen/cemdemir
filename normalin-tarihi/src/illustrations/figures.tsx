import React from 'react';
import {Ink, InkLine} from '../components/Ink';
import {COLORS} from '../brand/theme';
import {OPEN_HAND} from './hands';

/*
 * Parametric historical figure in the house line-art style.
 *
 * Local coordinates: feet on y = 0, figure faces +x, ~600 units tall.
 * Mirror the whole figure with `facing={-1}`. The near arm is driven by a
 * wrist target (two-bone IK) so gestures stay anatomically plausible.
 */

export type Headwear = 'none' | 'band' | 'cap' | 'assyrian' | 'babylonian' | 'laurel';
export type Beard = 'none' | 'long' | 'short';
export type Hair = 'long' | 'short' | 'curly';
export type Robe = 'mesopotamian' | 'royal' | 'greek' | 'himation';
export type ArmSleeve = 'short' | 'long' | 'royal' | 'bare';

export type Pt = {x: number; y: number};

export type FigureSpec = {
  headwear: Headwear;
  beard: Beard;
  hair: Hair;
  robe: Robe;
  sleeve: ArmSleeve;
};

export const SHOULDER: Pt = {x: 2, y: -446};
const UPPER = 108;
const FORE = 98;
const HAND_SCALE = 0.3;
const HEAD: Pt = {x: 6, y: -556};
const HEAD_SCALE = 0.8;

/** Relaxed wrist position (arm hanging, slightly forward). */
export const REST_WRIST: Pt = {x: 18, y: SHOULDER.y + 196};

const fmt = (n: number) => n.toFixed(1);

const headPaths = (spec: FigureSpec): string[] => {
  const out: string[] = [];
  const beardy = spec.beard === 'long';
  // cranium + face profile (forehead → nose → lips → chin)
  out.push(
    'M -14 52 C -34 40 -42 10 -38 -14 C -34 -38 -12 -52 10 -50 C 32 -48 44 -32 44 -14 C 44 -6 46 0 50 6 C 54 14 58 20 56 24 C 54 27 50 27 47 27 ' +
      (beardy
        ? 'C 48 30 48 32 46 34'
        : 'C 48 31 48 34 46 36 C 47 39 46 42 43 44 C 44 50 40 56 32 58 C 22 60 12 56 6 52'),
  );
  out.push('M -2 2 C -10 0 -12 16 -4 18'); // ear
  out.push('M 28 -2 C 32 -6 38 -6 41 -2 C 38 0 32 0 28 -2'); // eye
  out.push('M 8 52 C 10 60 12 70 12 82'); // neck
  out.push('M 28 -11 C 34 -14 40 -13 45 -10'); // brow
  if (spec.beard === 'long') {
    out.push('M 46 34 C 50 56 50 80 44 98 C 30 102 14 102 2 96 C -2 78 0 60 4 46');
    out.push('M 46 34 C 40 38 34 38 28 35');
    out.push('M 6 58 C 12 62 18 54 24 58 C 30 62 36 54 42 58 C 45 60 47 59 48 58');
    out.push('M 4 76 C 10 80 16 72 22 76 C 28 80 34 72 40 76 C 44 78 46 77 48 76');
  } else if (spec.beard === 'short') {
    out.push('M 46 36 C 48 46 44 58 32 62 C 20 64 10 60 4 52');
    out.push('M 46 36 C 42 39 37 39 32 37');
  }
  if (spec.hair === 'long') {
    out.push('M -38 -14 C -50 20 -48 60 -38 94 C -28 98 -18 96 -10 90');
    out.push('M -46 46 C -40 50 -34 42 -28 46 C -22 50 -18 44 -14 46');
    out.push('M -44 70 C -38 74 -32 66 -26 70 C -20 74 -16 68 -12 70');
  } else if (spec.hair === 'curly') {
    out.push('M -38 -10 C -48 -40 -22 -62 8 -58 C 32 -56 48 -42 46 -22');
    out.push('M -30 -40 C -26 -46 -18 -46 -16 -40 M -6 -50 C -2 -56 6 -56 8 -50 M 18 -48 C 22 -54 30 -52 30 -46');
  } else {
    out.push('M -38 -12 C -44 -40 -20 -58 8 -56 C 30 -54 44 -40 44 -24');
  }
  // headwear sits on top of the hair
  switch (spec.headwear) {
    case 'band':
      out.push('M -40 -22 C -18 -30 20 -30 44 -22');
      out.push('M -40 -14 C -18 -22 20 -22 45 -14');
      break;
    case 'cap':
      out.push('M -40 -16 C -40 -50 -16 -64 10 -62 C 34 -60 46 -44 45 -16');
      out.push('M -40 -16 C -16 -24 22 -24 45 -16');
      out.push('M -39 -26 C -16 -34 22 -34 45 -26');
      break;
    case 'assyrian':
      out.push('M -40 -14 L -33 -98 C -12 -104 18 -104 38 -98 L 45 -14');
      out.push('M -40 -14 C -14 -22 20 -22 45 -14');
      out.push('M -38 -34 C -12 -42 20 -42 44 -34');
      out.push('M -1 -103 L 5 -122 L 11 -103');
      out.push('M -36 -58 C -12 -64 20 -64 42 -58');
      break;
    case 'babylonian':
      out.push('M -40 -14 C -44 -62 -36 -96 4 -100 C 42 -98 48 -62 45 -14');
      out.push('M -40 -14 C -14 -22 20 -22 45 -14');
      out.push('M -41 -32 C -14 -40 20 -40 46 -32');
      out.push('M -10 -32 L -10 -20 M 4 -34 L 4 -21 M 18 -34 L 18 -21 M 32 -33 L 32 -19');
      break;
    case 'laurel': {
      out.push('M -40 -22 C -16 -34 22 -34 44 -24');
      const leaves = [-32, -18, -4, 10, 24, 36];
      leaves.forEach((x, i) => {
        const y = -27 - Math.sin((i / (leaves.length - 1)) * Math.PI) * 6;
        out.push(`M ${x} ${fmt(y)} C ${x + 3} ${fmt(y - 10)} ${x + 11} ${fmt(y - 12)} ${x + 12} ${fmt(y - 8)} C ${x + 10} ${fmt(y - 2)} ${x + 4} ${fmt(y)} ${x} ${fmt(y)}`);
      });
      break;
    }
    case 'none':
      break;
  }
  return out;
};

const robePaths = (spec: FigureSpec): {outline: string; details: string[]} => {
  const greek = spec.robe === 'greek' || spec.robe === 'himation';
  const outline = greek
    ? 'M 20 -490 C 46 -488 60 -476 62 -456 C 66 -330 72 -170 84 -24 C 44 -16 -44 -16 -80 -24 C -72 -170 -66 -330 -62 -456 C -60 -478 -44 -488 -20 -490'
    : 'M 20 -490 C 44 -488 58 -478 60 -458 C 64 -330 70 -150 74 -22 C 36 -14 -36 -14 -70 -22 C -68 -150 -64 -330 -60 -458 C -58 -478 -42 -488 -20 -490';
  const d: string[] = [];
  // feet / sandals
  d.push('M 40 -18 C 50 -6 70 -2 88 -4 C 94 -7 90 -14 80 -16');
  if (spec.robe === 'mesopotamian' || spec.robe === 'royal') {
    // diagonal fringed shawl
    d.push('M 56 -446 C 16 -390 -26 -318 -62 -264');
    d.push('M 62 -386 C 26 -334 -14 -272 -64 -214');
    const ticks: string[] = [];
    for (let i = 0; i <= 8; i++) {
      const t = i / 8;
      const x = 62 + (-64 - 62) * t;
      const y = -386 + (-214 + 386) * t - Math.sin(t * Math.PI) * 6;
      ticks.push(`M ${fmt(x)} ${fmt(y)} l -5 13`);
    }
    d.push(ticks.join(' '));
    d.push('M 34 -300 C 40 -210 46 -120 50 -34');
    d.push('M -26 -190 C -24 -130 -22 -80 -22 -26');
    // hem
    d.push('M 73 -52 C 36 -44 -36 -44 -69 -52');
    if (spec.robe === 'royal') {
      const dots: string[] = [];
      for (let i = 0; i < 7; i++) {
        const x = -56 + i * 18;
        dots.push(`M ${x} -37 l 4 -5 l 4 5 l -4 5 z`);
      }
      d.push(dots.join(' '));
      d.push('M 70 -110 C 36 -102 -36 -102 -67 -110');
      d.push('M 59 -416 C 20 -362 -20 -296 -63 -240');
    }
  } else {
    // chiton folds + himation drape across the body
    d.push('M 58 -440 C 10 -390 -28 -330 -62 -310');
    d.push('M 62 -310 C 26 -258 -24 -238 -64 -232');
    d.push('M 36 -256 C 44 -170 52 -100 60 -26');
    d.push('M 8 -246 C 10 -160 14 -90 16 -22');
    d.push('M -26 -238 C -26 -160 -28 -90 -32 -20');
    d.push('M -48 -234 C -50 -150 -56 -80 -62 -24');
    d.push('M 24 -436 C 22 -392 14 -360 4 -338');
  }
  return {outline, details: d};
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
  const w = [17, 14, 11];
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
  /** extra local-space paths (props such as a sheathed dagger) */
  extras?: string[];
}> = ({spec, x, y, scale = 1, facing = 1, wrist = REST_WRIST, showHand = true, draw = 1, extras = []}) => {
  const head = headPaths(spec);
  const robe = robePaths(spec);
  const arm = armGeometry(wrist);
  const {P} = arm;
  const armTop = `M ${P(arm.sA)} Q ${P(arm.eA)} ${P(arm.wA)}`;
  const armBot = `M ${P(arm.sB)} Q ${P(arm.eB)} ${P(arm.wB)}`;
  const armFill = `M ${P(arm.sA)} Q ${P(arm.eA)} ${P(arm.wA)} L ${P(arm.wB)} Q ${P(arm.eB)} ${P(arm.sB)} Z`;
  const armDetails: string[] = [];
  const along = (k: number, t: number) => {
    // point on the forearm at fraction t, offset k along the normal
    const p = {x: arm.elbow.x + (arm.wrist.x - arm.elbow.x) * t, y: arm.elbow.y + (arm.wrist.y - arm.elbow.y) * t};
    return {x: p.x + arm.n2.x * k, y: p.y + arm.n2.y * k};
  };
  if (spec.sleeve === 'short') {
    const a = along(14, 0.05);
    const b = along(-14, 0.05);
    armDetails.push(`M ${P(a)} L ${P(b)}`);
    const c = along(11.5, 0.86);
    const d = along(-11.5, 0.86);
    armDetails.push(`M ${P(c)} L ${P(d)}`); // bracelet
  } else if (spec.sleeve === 'royal') {
    for (const t of [0.72, 0.8]) {
      armDetails.push(`M ${P(along(12, t))} L ${P(along(-12, t))}`);
    }
  } else if (spec.sleeve === 'long') {
    armDetails.push(`M ${P(along(11.5, 0.9))} L ${P(along(-11.5, 0.9))}`);
  }

  // Draw order: robe, arm, head (beard sits over the arm), hand.
  const n = 4;
  const seg = (i: number) => Math.min(1, Math.max(0, draw * n - i * 0.8));
  const headFill =
    'M -38 -14 C -34 -38 -12 -52 10 -50 C 32 -48 44 -32 44 -14 L 56 24 L 46 60 L 12 84 L 8 84 L -14 60 Z' +
    (spec.beard === 'long' ? ' M 46 34 C 50 56 50 80 44 98 C 30 102 14 102 2 96 C -2 78 0 60 4 46 Z' : '') +
    (spec.hair === 'long' ? ' M -38 -14 C -50 20 -48 60 -38 94 C -28 98 -18 96 -10 90 L 0 0 Z' : '') +
    (spec.headwear === 'assyrian' ? ' M -40 -14 L -33 -98 C -12 -104 18 -104 38 -98 L 45 -14 Z' : '') +
    (spec.headwear === 'babylonian' ? ' M -40 -14 C -44 -62 -36 -96 4 -100 C 42 -98 48 -62 45 -14 Z' : '');
  const shown = (i: number) => (seg(i) >= 0.999 ? 1 : 0);
  return (
    <g transform={`translate(${x} ${y}) scale(${scale * facing} ${scale})`}>
      <path d={robe.outline} fill={COLORS.paper} opacity={shown(0)} />
      <Ink paths={[robe.outline, ...robe.details, ...extras]} draw={seg(0)} overlap={0.6} />
      <path d={armFill} fill={COLORS.paper} opacity={shown(2)} />
      <Ink paths={[armTop, armBot, ...armDetails]} draw={seg(2)} overlap={0.5} />
      <g transform={`translate(${HEAD.x} ${HEAD.y}) scale(${HEAD_SCALE})`}>
        <path d={headFill} fill={COLORS.paper} opacity={shown(1)} />
        <Ink paths={head} draw={seg(1)} overlap={0.5} />
      </g>
      {showHand ? (
        <g transform={`translate(${fmt(arm.wrist.x)} ${fmt(arm.wrist.y)}) rotate(${fmt(arm.angle)}) scale(${HAND_SCALE})`}>
          <path d={OPEN_HAND[0] + ' Z'} fill={COLORS.paper} opacity={shown(3)} />
          <Ink paths={OPEN_HAND} draw={seg(3)} overlap={0.5} />
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

export const SheathedDagger = [
  'M -44 -300 L -28 -300 L -24 -176 C -28 -166 -40 -166 -44 -176 Z',
  'M -54 -304 L -18 -304',
  'M -36 -304 L -36 -326 M -42 -326 L -30 -326',
];

// re-export to keep the line primitive close to the figures for one-off strokes
export {InkLine};
