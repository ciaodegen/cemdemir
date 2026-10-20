import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONTS} from '../brand/theme';
import {InkLine} from './Ink';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/**
 * Text uncovered left→right by a soft-edged mask, like ink following the
 * pen. Never pops: opacity is always carried by the moving edge.
 */
export const WipeText: React.FC<{
  progress: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
  feather?: number;
}> = ({progress, children, style, feather = 14}) => {
  const p = Math.min(1, Math.max(0, progress));
  const edge = -feather + p * (100 + feather * 2);
  const mask = `linear-gradient(90deg, #000 0%, #000 ${edge - feather}%, transparent ${edge}%, transparent 100%)`;
  return (
    <span
      style={{
        display: 'inline-block',
        WebkitMaskImage: p >= 1 ? undefined : mask,
        maskImage: p >= 1 ? undefined : mask,
        opacity: p <= 0 ? 0 : 1,
        ...style,
      }}
    >
      {children}
    </span>
  );
};

/** Hand-lettered multi-line title; lines are written one after another. */
export const HandTitle: React.FC<{
  lines: string[];
  from: number;
  /** frames per line */
  perLine?: number;
  size?: number;
  top: number;
  out?: number;
  underline?: boolean;
  color?: string;
}> = ({lines, from, perLine = 22, size = 112, top, out, underline = true, color = COLORS.ink}) => {
  const frame = useCurrentFrame();
  const fade = out !== undefined ? interpolate(frame, [out, out + 14], [1, 0], clamp) : 1;
  const ulStart = from + perLine * lines.length - 4;
  const ul = interpolate(frame, [ulStart, ulStart + 14], [0, 1], {...clamp, easing: Easing.inOut(Easing.quad)});
  return (
    <div lang="tr" style={{position: 'absolute', top, left: 70, right: 70, textAlign: 'center', opacity: fade}}>
      {lines.map((l, i) => (
        <div key={i} style={{lineHeight: 1.08}}>
          <WipeText
            progress={interpolate(frame, [from + i * perLine, from + (i + 1) * perLine], [0, 1], {...clamp, easing: Easing.inOut(Easing.sin)})}
            style={{fontFamily: FONTS.hand, fontWeight: 700, fontSize: size, color, letterSpacing: '-0.005em'}}
          >
            {l}
          </WipeText>
        </div>
      ))}
      {underline ? (
        <svg width={360} height={30} viewBox="0 0 360 30" style={{display: 'block', margin: '14px auto 0'}}>
          <InkLine d="M 8 18 C 90 10 200 8 352 14" draw={ul} width={4} />
        </svg>
      ) : null}
    </div>
  );
};

/** Small historical place/period label, written on in Kalam. */
export const HandLabel: React.FC<{text: string; from?: number; to?: number; top?: number; size?: number}> = ({
  text,
  from = 8,
  to,
  top = 300,
  size = 54,
}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [from, from + 20], [0, 1], {...clamp, easing: Easing.inOut(Easing.sin)});
  const o = to !== undefined ? interpolate(frame, [to - 12, to], [1, 0], clamp) : 1;
  return (
    <div lang="tr" style={{position: 'absolute', top, left: 80, right: 80, textAlign: 'center', opacity: o}}>
      <WipeText progress={p} style={{fontFamily: FONTS.hand, fontWeight: 700, fontSize: size, color: COLORS.labelInk}}>
        {text}
      </WipeText>
    </div>
  );
};
