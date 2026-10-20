import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {LAYOUT, TYPE} from '../brand/theme';
import type {Cue} from '../timing';
import {WordReveal} from './Type';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/**
 * Word-by-word Turkish subtitles. With measured word timings (from the TTS
 * alignment) each word appears as it is spoken; otherwise words are spread
 * across the cue. Revealed words stay until the phrase ends.
 */
export const Subtitles: React.FC<{cues: Cue[]}> = ({cues}) => {
  const frame = useCurrentFrame();
  const cue = cues.find((c) => frame >= c.from - 2 && frame < c.to + 6);
  if (!cue) return null;
  const out = interpolate(frame, [cue.to - 2, cue.to + 6], [1, 0], clamp);
  return (
    <div style={{position: 'absolute', left: 110, right: 110, top: LAYOUT.subtitleY, opacity: out}}>
      <WordReveal
        text={cue.text}
        from={cue.from}
        to={cue.from + (cue.to - cue.from) * 0.82}
        times={cue.wordStarts}
        type={TYPE.subtitle}
        wordFrames={7}
      />
    </div>
  );
};
