import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONT_FAMILY} from '../brand/theme';

/** On-screen sign-off (never narrated) + quiet brand signature. */
export const SpecialEndingText: React.FC<{text: string; signature?: string; at: number; y?: number}> = ({
  text,
  signature = 'normalin tarihi',
  at,
  y = 1120,
}) => {
  const frame = useCurrentFrame();
  const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
  const t = interpolate(frame, [at, at + 20], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
  const sig = interpolate(frame, [at + 16, at + 36], [0, 1], clamp);
  return (
    <div lang="tr" style={{position: 'absolute', top: y, left: 90, right: 90, textAlign: 'center', fontFamily: FONT_FAMILY}}>
      <div style={{fontSize: 54, fontWeight: 450, color: COLORS.ink, letterSpacing: '-0.01em', opacity: t, transform: `translateY(${(1 - t) * 10}px)`}}>
        {text}
      </div>
      <div style={{marginTop: 34, fontSize: 24, fontWeight: 500, letterSpacing: '0.3em', paddingLeft: '0.3em', color: COLORS.accent, opacity: sig}}>
        {signature}
      </div>
    </div>
  );
};
