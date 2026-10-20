import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONTS, LAYOUT} from '../brand/theme';
import type {Cue} from '../timing';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/**
 * Word-by-word Turkish subtitles. Words are laid out from the start (so the
 * line never reflows) and each one eases in with a small rise; revealed
 * words stay until the cue ends, then the whole phrase fades softly.
 */
export const Subtitles: React.FC<{cues: Cue[]}> = ({cues}) => {
  const frame = useCurrentFrame();
  const cue = cues.find((c) => frame >= c.from && frame < c.to + 6);
  if (!cue) return null;
  const words = cue.text.split(/\s+/);
  const span = Math.max(1, (cue.to - cue.from) * 0.82);
  const weights = words.map((w) => w.length + 2);
  const total = weights.reduce((a, b) => a + b, 0);
  let acc = 0;
  const out = interpolate(frame, [cue.to - 2, cue.to + 6], [1, 0], clamp);
  return (
    <div
      lang="tr"
      style={
        {
          position: 'absolute',
          left: 110,
          right: 110,
          top: LAYOUT.subtitleY,
          textAlign: 'center',
          fontFamily: FONTS.sans,
          fontWeight: 500,
          fontSize: 42,
          lineHeight: 1.36,
          color: COLORS.ink,
          opacity: out,
          textWrap: 'balance',
        } as React.CSSProperties
      }
    >
      {words.map((w, i) => {
        const start = cue.from + (span * acc) / total;
        acc += weights[i];
        const p = interpolate(frame, [start, start + 7], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
        return (
          <span key={i} style={{display: 'inline-block', opacity: p, transform: `translateY(${(1 - p) * 7}px)`, marginRight: '0.26em'}}>
            {w}
          </span>
        );
      })}
    </div>
  );
};
