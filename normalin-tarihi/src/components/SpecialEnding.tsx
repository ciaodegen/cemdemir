import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONT_FAMILY, TYPE} from '../brand/theme';
import {WordReveal} from './Type';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** On-screen sign-off (never narrated), revealed word by word, + quiet signature. */
export const SpecialEndingText: React.FC<{text: string; signature?: string; at: number; y?: number}> = ({
  text,
  signature = 'normalin tarihi',
  at,
  y = 1180,
}) => {
  const frame = useCurrentFrame();
  const sig = interpolate(frame, [at + 40, at + 62], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
  return (
    <div style={{position: 'absolute', top: y, left: 40, right: 40, textAlign: 'center'}}>
      <WordReveal text={text} from={at} to={at + 30} type={TYPE.ending} wordFrames={14} style={{whiteSpace: 'nowrap'}} />
      <div
        style={{
          marginTop: 24,
          fontFamily: FONT_FAMILY,
          ...TYPE.small,
          letterSpacing: '0.12em',
          color: COLORS.text,
          opacity: sig * 0.75,
          transform: `translateY(${(1 - sig) * 6}px)`,
        }}
      >
        {signature}
      </div>
    </div>
  );
};
