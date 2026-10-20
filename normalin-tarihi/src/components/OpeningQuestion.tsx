import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONT_FAMILY, LAYOUT} from '../brand/theme';

/** The episode's hook question, set large at the top of the frame. */
export const OpeningQuestion: React.FC<{text: string; from: number; out?: number}> = ({text, from, out}) => {
  const frame = useCurrentFrame();
  let o = interpolate(frame, [from, from + 14], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.quad)});
  if (out !== undefined) o = Math.min(o, interpolate(frame, [out, out + 12], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  return (
    <div
      lang="tr"
      style={{
        position: 'absolute',
        top: LAYOUT.questionY,
        left: 90,
        right: 90,
        textAlign: 'center',
        fontFamily: FONT_FAMILY,
        fontWeight: 500,
        fontSize: 82,
        letterSpacing: '-0.015em',
        lineHeight: 1.12,
        color: COLORS.ink,
        opacity: o,
        transform: `translateY(${(1 - o) * 10}px)`,
      }}
    >
      {text}
    </div>
  );
};
