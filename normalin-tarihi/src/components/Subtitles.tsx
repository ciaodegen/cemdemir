import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONT_FAMILY, LAYOUT} from '../brand/theme';
import type {Cue} from '../timing';

/** Minimal Turkish subtitles: small, ink-coloured, centred, no karaoke. */
export const Subtitles: React.FC<{cues: Cue[]}> = ({cues}) => {
  const frame = useCurrentFrame();
  const cue = cues.find((c) => frame >= c.from && frame < c.to);
  if (!cue) return null;
  const fade = 4;
  const o = Math.min(
    interpolate(frame, [cue.from, cue.from + fade], [0, 1], {extrapolateRight: 'clamp'}),
    interpolate(frame, [cue.to - fade, cue.to], [1, 0], {extrapolateLeft: 'clamp'}),
  );
  return (
    <div
      style={{
        position: 'absolute',
        left: 120,
        right: 120,
        top: LAYOUT.subtitleY,
        textAlign: 'center',
        fontFamily: FONT_FAMILY,
        fontWeight: 450,
        fontSize: 40,
        lineHeight: 1.38,
        color: COLORS.ink,
        opacity: o,
        textWrap: 'balance',
      } as React.CSSProperties}
      lang="tr"
    >
      {cue.text}
    </div>
  );
};
