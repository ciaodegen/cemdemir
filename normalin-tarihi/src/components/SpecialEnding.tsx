import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONTS} from '../brand/theme';
import {WipeText} from './Type';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** On-screen sign-off (never narrated), written on, + quiet brand signature. */
export const SpecialEndingText: React.FC<{text: string; signature?: string; at: number; y?: number}> = ({
  text,
  signature = 'normalin tarihi',
  at,
  y = 1180,
}) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [at, at + 40], [0, 1], {...clamp, easing: Easing.inOut(Easing.sin)});
  const sig = interpolate(frame, [at + 38, at + 62], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
  return (
    <div lang="tr" style={{position: 'absolute', top: y, left: 30, right: 30, textAlign: 'center'}}>
      <WipeText progress={t} style={{fontFamily: FONTS.hand, fontWeight: 700, fontSize: 70, color: COLORS.ink, whiteSpace: 'nowrap'}}>
        {text}
      </WipeText>
      <div
        style={{
          marginTop: 26,
          fontFamily: FONTS.sans,
          fontSize: 26,
          fontWeight: 500,
          letterSpacing: '0.28em',
          paddingLeft: '0.28em',
          color: COLORS.labelInk,
          opacity: sig,
          transform: `translateY(${(1 - sig) * 6}px)`,
        }}
      >
        {signature}
      </div>
    </div>
  );
};
