import React from 'react';
import {Ink, InkPath} from '../components/Ink';
import {COLORS} from '../brand/theme';

/*
 * Hands — the recurring motif of the episode.
 *
 * Local coordinates: the wrist sits at (0, 0) and the hand points toward +x.
 * Sleeves extend toward −x far enough to leave the frame. Mirror with
 * scale(-1, 1) for the partner hand.
 */

export type SleeveStyle =
  | 'modern'
  | 'modernOlive'
  | 'mesopotamian'
  | 'royal'
  | 'royalSand'
  | 'greek'
  | 'medieval'
  | 'medievalMail'
  | 'bare';

export type Tone = 'light' | 'deep';
export const skinOf = (tone: Tone) => (tone === 'light' ? COLORS.skin : COLORS.skinDeep);

/** Open right hand offered for a handshake: thumb up, fingers forward. */
export const OPEN_HAND: string[] = [
  // silhouette: back of hand → thumb → web → index → fingertips → palm → wrist
  'M -6 -40 C 14 -42 30 -44 44 -48 C 64 -60 84 -80 102 -92 C 112 -98 124 -94 122 -82 C 120 -70 106 -58 96 -50 C 100 -47 106 -46 112 -46 C 144 -48 180 -48 206 -42 C 222 -39 226 -25 212 -21 C 228 -19 234 -4 220 0 C 232 4 232 18 216 21 C 222 27 214 38 198 38 C 172 42 142 48 110 52 C 74 56 36 52 -6 44',
  // finger separations
  'M 212 -21 C 182 -21 150 -21 124 -19',
  'M 220 0 C 190 1 160 1 132 2',
  'M 216 21 C 194 21 170 22 148 22',
  // thumb / thenar crease
  'M 96 -50 C 84 -32 66 -22 44 -16',
];

export const openHandPaths = (tone: Tone): InkPath[] => [
  {d: OPEN_HAND[0] + ' L -6 -40 Z', fill: skinOf(tone)},
  ...OPEN_HAND.slice(1),
];

const zigzag = (x0: number, x1: number, y: number, h: number, step = 14) => {
  let d = `M ${x0} ${y}`;
  for (let x = x0, up = true; x < x1; x += step, up = !up) d += ` L ${x + step} ${up ? y - h : y}`;
  return d;
};

/** Sleeve + cuff that the hand emerges from, with its flat colour. */
export const sleevePaths = (style: SleeveStyle, tone: Tone = 'light'): InkPath[] => {
  const skin = skinOf(tone);
  switch (style) {
    case 'modern':
    case 'modernOlive': {
      const jacket = style === 'modern' ? COLORS.camel : COLORS.olive;
      return [
        {d: 'M -760 -60 C -500 -60 -260 -58 -58 -56 C -54 -20 -54 20 -58 58 C -260 60 -500 62 -760 64 Z', fill: jacket},
        {d: 'M -58 -46 L -16 -44 C -12 -14 -12 16 -16 44 L -58 46 Z', fill: COLORS.linen},
        'M -34 -45 C -31 -16 -31 16 -34 45',
        'M -300 -58 C -296 -30 -296 0 -300 20',
      ];
    }
    case 'mesopotamian':
      return [
        {d: 'M -760 -66 C -480 -64 -240 -62 -64 -58 C -60 -20 -60 22 -64 62 C -240 66 -480 68 -760 70 Z', fill: COLORS.terracotta},
        'M -64 -40 L -82 -40 M -64 -24 L -84 -24 M -63 -8 L -85 -8 M -63 8 L -85 8 M -63 24 L -84 24 M -64 40 L -82 40',
        {d: 'M -64 -36 C -40 -38 -20 -40 -6 -40 L -6 44 C -20 44 -40 42 -64 40 Z', fill: skin},
        {d: 'M -32 -40 C -28 -14 -28 16 -32 42 L -20 42 C -16 16 -16 -14 -20 -40 Z', fill: COLORS.camel},
      ];
    case 'royal':
    case 'royalSand': {
      const cloth = style === 'royal' ? COLORS.terracotta : COLORS.sand;
      const band = style === 'royal' ? COLORS.sand : COLORS.terracotta;
      return [
        {d: 'M -760 -64 C -480 -62 -240 -60 -40 -56 C -36 -20 -36 22 -40 60 C -240 64 -480 66 -760 68 Z', fill: cloth},
        {d: 'M -120 -58 C -116 -20 -116 22 -120 61 L -76 60 C -72 22 -72 -20 -76 -57 Z', fill: band},
        zigzag(-118, -78, 6, 12, 10),
        {d: 'M -40 -40 L -6 -40 L -6 44 L -40 44 Z', fill: skin},
        {d: 'M -28 -41 C -25 -14 -25 16 -28 44 L -18 44 C -15 16 -15 -14 -18 -41 Z', fill: COLORS.camel},
      ];
    }
    case 'greek':
      return [
        {d: 'M -760 -70 C -560 -60 -420 -52 -300 -46 C -250 -44 -220 -40 -200 -36 C -214 -12 -216 18 -210 44 C -260 52 -300 56 -420 64 C -560 74 -760 80 -760 80 Z', fill: COLORS.linen},
        'M -420 -50 C -380 -20 -350 20 -330 60',
        'M -560 -60 C -520 -24 -500 30 -480 70',
        {d: 'M -200 -32 C -130 -38 -60 -38 -6 -36 L -6 40 C -60 44 -140 44 -210 40 Z', fill: skin},
      ];
    case 'medieval':
    case 'medievalMail': {
      const cloth = style === 'medieval' ? COLORS.olive : COLORS.taupe;
      return [
        {d: 'M -760 -60 C -500 -60 -260 -56 -110 -52 L -110 54 C -260 58 -500 62 -760 62 Z', fill: cloth},
        {d: 'M -110 -60 C -60 -60 -30 -56 -14 -50 C -8 -16 -8 18 -14 50 C -30 58 -60 62 -110 62 C -114 20 -114 -20 -110 -60 Z', fill: style === 'medieval' ? COLORS.sand : COLORS.taupeLight},
        'M -86 -58 C -82 -20 -82 22 -86 60',
        ...(style === 'medievalMail' ? ['M -400 -40 L -380 -20 L -360 -40 L -340 -20 L -320 -40 M -400 10 L -380 30 L -360 10 L -340 30 L -320 10'] : []),
      ];
    }
    case 'bare':
      return [{d: 'M -760 -44 C -480 -46 -220 -42 -6 -36 L -6 40 C -220 48 -480 54 -760 54 Z', fill: skin}];
  }
};

/*
 * Clasped handshake, origin at the centre of the grip.
 * The right-hand person (B) is nearer to us: we see the back of B's hand,
 * A's thumb resting across it and A's fingers wrapping up from below.
 */
const CLASP_A_WRIST = {x: -150, y: 8};
const CLASP_B_WRIST = {x: 150, y: -20};

/** Skin masses behind the clasp outlines: B (near hand) then A over it. */
export const CLASP_FILL_B =
  'M -150 -30 C -124 -34 -100 -42 -78 -54 C -50 -74 -10 -84 26 -80 C 44 -78 58 -70 54 -60 L 50 -62 C 84 -66 118 -64 150 -58 L 150 18 C 104 22 62 36 28 54 C 2 66 -30 74 -56 74 C -76 76 -84 62 -76 52 C -94 48 -96 32 -84 24 L -90 40 C -106 46 -128 48 -150 46 Z';
export const CLASP_FILL_A =
  'M -150 -30 C -124 -34 -100 -42 -78 -54 C -50 -74 -10 -84 26 -80 C 44 -78 58 -70 54 -60 C 50 -52 36 -52 22 -54 C 2 -58 -18 -56 -36 -50 C -62 -44 -82 -28 -84 -8 C -98 -2 -100 18 -84 24 L -90 40 C -106 46 -128 48 -150 46 Z';

export const ClaspSkin: React.FC<{a?: Tone; b?: Tone; opacity?: number}> = ({a = 'light', b = 'deep', opacity = 1}) => (
  <g opacity={opacity}>
    <path d={CLASP_FILL_B} fill={skinOf(b)} />
    <path d={CLASP_FILL_A} fill={skinOf(a)} />
  </g>
);

export const CLASP_HANDS: string[] = [
  // A: wrist rising into the grip, thumb resting across B's knuckles
  'M -150 -30 C -124 -34 -100 -42 -78 -54',
  'M -78 -54 C -50 -74 -10 -84 26 -80 C 44 -78 58 -70 54 -60 C 50 -52 36 -52 22 -54 C 2 -58 -18 -56 -36 -50',
  'M -150 46 C -128 48 -106 46 -90 40',
  // B: back of the hand from the wrist
  'M 150 -58 C 118 -64 84 -66 50 -62',
  'M 150 18 C 104 22 62 36 28 54',
  // B: curled fingers wrapping A's palm
  'M -36 -50 C -62 -44 -82 -28 -84 -8 C -98 -2 -100 18 -84 24 C -96 32 -94 48 -76 52 C -84 62 -76 76 -56 74 C -30 74 2 66 28 54',
  'M -84 -8 C -66 -4 -50 -8 -36 -16',
  'M -84 24 C -64 26 -46 22 -32 14',
  'M -76 52 C -58 52 -40 46 -28 38',
];

const sleeveAt = (wrist: {x: number; y: number}, angleDeg: number, mirror: boolean) =>
  `translate(${wrist.x} ${wrist.y}) ${mirror ? 'scale(-1 1)' : ''} rotate(${angleDeg})`;

export const CLASP_A_ANGLE = -4;
export const CLASP_B_ANGLE = 7;
export {CLASP_A_WRIST, CLASP_B_WRIST};

/** Just the two sleeves of the clasp (lets scenes swap costume eras). */
export const ClaspSleeves: React.FC<{a: SleeveStyle; b: SleeveStyle; draw?: number; opacity?: number; toneA?: Tone; toneB?: Tone}> = ({
  a,
  b,
  draw = 1,
  opacity = 1,
  toneA = 'light',
  toneB = 'deep',
}) => (
  <g opacity={opacity}>
    <g transform={sleeveAt(CLASP_A_WRIST, CLASP_A_ANGLE, false)}>
      <Ink paths={sleevePaths(a, toneA)} draw={draw} overlap={0.7} />
    </g>
    <g transform={sleeveAt(CLASP_B_WRIST, CLASP_B_ANGLE, true)}>
      <Ink paths={sleevePaths(b, toneB)} draw={draw} overlap={0.7} />
    </g>
  </g>
);

export const ClaspedHands: React.FC<{
  sleeveA?: SleeveStyle;
  sleeveB?: SleeveStyle;
  draw?: number;
  sleeveOpacity?: number;
}> = ({sleeveA = 'modern', sleeveB = 'modern', draw = 1, sleeveOpacity = 1}) => (
  <g>
    {sleeveOpacity > 0 ? <ClaspSleeves a={sleeveA} b={sleeveB} draw={draw} opacity={sleeveOpacity} /> : null}
    <ClaspSkin opacity={draw >= 1 ? 1 : Math.max(0, (draw - 0.5) * 2)} />
    <Ink paths={CLASP_HANDS} draw={draw} overlap={0.7} />
  </g>
);

/** Small burst of three strokes above the meeting point, as in the reference. */
export const MeetSpark: React.FC<{draw?: number; opacity?: number}> = ({draw = 1, opacity = 1}) => (
  <g opacity={opacity}>
    <Ink
      paths={['M 0 -150 L 0 -118', 'M -44 -136 L -30 -110', 'M 44 -136 L 30 -110']}
      draw={draw}
      overlap={0.3}
      color={COLORS.ink}
    />
  </g>
);

/** A single open hand on a sleeve. */
export const ReachingHand: React.FC<{sleeve?: SleeveStyle; tone?: Tone; draw?: number}> = ({sleeve = 'modern', tone = 'light', draw = 1}) => (
  <Ink paths={[...sleevePaths(sleeve, tone), ...openHandPaths(tone)]} draw={draw} overlap={0.75} />
);
