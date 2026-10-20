import React from 'react';
import {ReachingHand, ClaspedHands, MeetSpark} from '../src/illustrations/hands';
import {Figure, FigureSpec, REST_WRIST, SheathedSword} from '../src/illustrations/figures';
import {COLORS as C} from '../src/brand/theme';

const meso: FigureSpec = {headwear: 'band', beard: 'long', hair: 'long', robe: 'mesopotamian', sleeve: 'short', cloth: C.terracotta, accent: C.sand, hat: C.camel};
const assyr: FigureSpec = {headwear: 'assyrian', beard: 'long', hair: 'long', robe: 'royal', sleeve: 'royal', cloth: C.terracotta, accent: C.sand, hat: C.sand, skin: 'deep'};
const greek: FigureSpec = {headwear: 'laurel', beard: 'short', hair: 'curly', robe: 'himation', sleeve: 'bare', cloth: C.linen, accent: C.sand};
const med: FigureSpec = {headwear: 'none', beard: 'short', hair: 'short', robe: 'tunic', sleeve: 'long', cloth: C.olive, accent: C.terracotta, legs: C.taupe};
const mod: FigureSpec = {headwear: 'none', beard: 'none', hair: 'short', robe: 'suit', sleeve: 'suit', cloth: C.camel, accent: C.camel, legs: C.camel, skin: 'deep'};

export const PREVIEWS: Record<string, {el: React.ReactNode; size?: [number, number]}> = {
  hands: {
    size: [1080, 1080],
    el: (
      <>
        <g transform="translate(250 300)"><ReachingHand /></g>
        <g transform="translate(830 300) scale(-1 1)"><ReachingHand sleeve="modernOlive" tone="deep" /></g>
        <g transform="translate(540 750) scale(1.3)"><ClaspedHands sleeveA="royal" sleeveB="royalSand" /><MeetSpark /></g>
      </>
    ),
  },
  figures: {
    size: [1600, 760],
    el: (
      <>
        <Figure spec={meso} x={130} y={720} wrist={{x: 180, y: -400}} extras={SheathedSword} />
        <Figure spec={assyr} x={420} y={720} facing={-1} />
        <Figure spec={greek} x={640} y={720} wrist={{x: 200, y: -420}} />
        <Figure spec={med} x={940} y={720} swing={18} />
        <Figure spec={mod} x={1240} y={720} swing={-14} wrist={REST_WRIST} />
        <Figure spec={assyr} x={1480} y={720} stone={{fill: C.stone, line: '#8E7B66'}} wrist={{x: 190, y: -390}} />
      </>
    ),
  },
};
