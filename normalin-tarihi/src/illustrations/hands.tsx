import React from 'react';
import {Ink} from '../components/Ink';
import {COLORS} from '../brand/theme';

/*
 * Hands — the recurring motif of the episode.
 *
 * Local coordinates: the wrist sits at (0, 0) and the hand points toward +x.
 * Sleeves extend toward −x far enough to leave the frame. Mirror with
 * scale(-1, 1) for the partner hand.
 */

export type SleeveStyle = 'modern' | 'mesopotamian' | 'greek' | 'medieval' | 'bare';

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

/** Sleeve + cuff that the hand emerges from. */
export const sleevePaths = (style: SleeveStyle): string[] => {
  switch (style) {
    case 'modern':
      return [
        // jacket sleeve
        'M -760 -60 C -500 -60 -260 -58 -58 -56',
        'M -760 64 C -500 62 -260 60 -58 58',
        'M -58 -56 C -54 -20 -54 20 -58 58',
        // shirt cuff
        'M -58 -46 L -16 -44 C -12 -14 -12 16 -16 44 L -58 46',
        'M -34 -45 C -31 -16 -31 16 -34 45',
      ];
    case 'mesopotamian':
      return [
        // wide woven sleeve with fringe and a bracelet
        'M -760 -66 C -480 -64 -240 -62 -64 -58',
        'M -760 70 C -480 68 -240 66 -64 62',
        'M -64 -58 C -60 -20 -60 22 -64 62',
        'M -64 -40 L -82 -40 M -64 -24 L -84 -24 M -63 -8 L -85 -8 M -63 8 L -85 8 M -63 24 L -84 24 M -64 40 L -82 40',
        'M -28 -40 C -24 -14 -24 16 -28 42',
        'M -18 -39 C -14 -14 -14 16 -18 41',
      ];
    case 'greek':
      return [
        // draped himation folds over a bare forearm
        'M -760 -70 C -560 -60 -420 -52 -300 -46 C -250 -44 -220 -40 -200 -36',
        'M -760 80 C -560 74 -420 64 -300 56 C -260 52 -230 48 -210 44',
        'M -200 -36 C -214 -12 -216 18 -210 44',
        'M -420 -50 C -380 -20 -350 20 -330 60',
        'M -560 -60 C -520 -24 -500 30 -480 70',
        // bare forearm
        'M -200 -32 C -130 -38 -60 -38 -6 -36',
        'M -210 40 C -140 44 -60 44 -6 40',
      ];
    case 'medieval':
      return [
        // fitted sleeve with a turned-back cuff
        'M -760 -60 C -500 -60 -260 -56 -110 -52',
        'M -760 62 C -500 62 -260 58 -110 54',
        'M -110 -60 C -60 -60 -30 -56 -14 -50 C -8 -16 -8 18 -14 50 C -30 58 -60 62 -110 62 C -114 20 -114 -20 -110 -60',
        'M -86 -58 C -82 -20 -82 22 -86 60',
      ];
    case 'bare':
      return [
        'M -760 -44 C -480 -46 -220 -42 -6 -36',
        'M -760 54 C -480 54 -220 48 -6 40',
      ];
  }
};

/** A single open hand on a sleeve. */
export const ReachingHand: React.FC<{
  sleeve?: SleeveStyle;
  draw?: number;
  color?: string;
}> = ({sleeve = 'modern', draw = 1, color}) => (
  <Ink paths={[...sleevePaths(sleeve), ...OPEN_HAND]} draw={draw} overlap={0.75} color={color} />
);

/*
 * Clasped handshake, origin at the centre of the grip.
 * The right-hand person (B) is nearer to us: we see the back of B's hand,
 * A's thumb resting across it and A's fingers wrapping up from below.
 */
const CLASP_A_WRIST = {x: -150, y: 8};
const CLASP_B_WRIST = {x: 150, y: -20};

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
export const ClaspSleeves: React.FC<{a: SleeveStyle; b: SleeveStyle; draw?: number; opacity?: number}> = ({a, b, draw = 1, opacity = 1}) => (
  <g opacity={opacity}>
    <g transform={sleeveAt(CLASP_A_WRIST, CLASP_A_ANGLE, false)}>
      <Ink paths={sleevePaths(a)} draw={draw} overlap={0.7} />
    </g>
    <g transform={sleeveAt(CLASP_B_WRIST, CLASP_B_ANGLE, true)}>
      <Ink paths={sleevePaths(b)} draw={draw} overlap={0.7} />
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
