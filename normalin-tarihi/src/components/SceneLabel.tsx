import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONT_FAMILY} from '../brand/theme';

/** Small tracked caption naming the place / period of a scene. */
export const SceneLabel: React.FC<{text: string; from?: number; to?: number; y?: number}> = ({text, from = 6, to, y = 330}) => {
  const frame = useCurrentFrame();
  let o = interpolate(frame, [from, from + 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (to !== undefined) o = Math.min(o, interpolate(frame, [to - 10, to], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  return (
    <div
      lang="tr"
      style={{
        position: 'absolute',
        top: y,
        left: 0,
        right: 0,
        textAlign: 'center',
        fontFamily: FONT_FAMILY,
        fontWeight: 500,
        fontSize: 24,
        letterSpacing: '0.32em',
        paddingLeft: '0.32em',
        color: COLORS.accent,
        opacity: o,
      }}
    >
      {text}
    </div>
  );
};
