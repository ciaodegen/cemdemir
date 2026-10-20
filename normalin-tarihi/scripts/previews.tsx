import React from 'react';
import {ReachingHand, ClaspedHands, MeetSpark} from '../src/illustrations/hands';
import {Figure, REST_WRIST, FigureSpec} from '../src/illustrations/figures';

const meso: FigureSpec = {headwear: 'band', beard: 'long', hair: 'long', robe: 'mesopotamian', sleeve: 'short'};
const meso2: FigureSpec = {headwear: 'cap', beard: 'long', hair: 'long', robe: 'mesopotamian', sleeve: 'short'};
const assyr: FigureSpec = {headwear: 'assyrian', beard: 'long', hair: 'long', robe: 'royal', sleeve: 'royal'};
const babyl: FigureSpec = {headwear: 'babylonian', beard: 'long', hair: 'long', robe: 'royal', sleeve: 'royal'};
const greek: FigureSpec = {headwear: 'laurel', beard: 'short', hair: 'curly', robe: 'himation', sleeve: 'bare'};
const greek2: FigureSpec = {headwear: 'laurel', beard: 'none', hair: 'curly', robe: 'greek', sleeve: 'bare'};

export const PREVIEWS: Record<string, {el: React.ReactNode; size?: [number, number]}> = {
  hands: {
    size: [1080, 1080],
    el: (
      <>
        <g transform="translate(250 300)"><ReachingHand /></g>
        <g transform="translate(830 300) scale(-1 1)"><ReachingHand /></g>
        <g transform="translate(540 750) scale(1.3)"><ClaspedHands /><MeetSpark /></g>
      </>
    ),
  },
  figures: {
    size: [1600, 1500],
    el: (
      <>
        <Figure spec={meso} x={150} y={700} />
        <Figure spec={meso2} x={450} y={700} facing={-1} wrist={{x: 180, y: -400}} />
        <Figure spec={assyr} x={700} y={700} wrist={{x: 190, y: -390}} />
        <Figure spec={babyl} x={1050} y={700} facing={-1} />
        <Figure spec={greek} x={200} y={1450} wrist={{x: 200, y: -420}} />
        <Figure spec={greek2} x={600} y={1450} facing={-1} wrist={REST_WRIST} />
        <Figure spec={meso} x={1000} y={1450} wrist={{x: 150, y: -330}} />
      </>
    ),
  },
};
