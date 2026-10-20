import React, {useId} from 'react';
import {Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, FONT_FAMILY, TYPE} from './theme';
import {LOGO_CENTERLINE, LOGO_LEFT_DOT, LOGO_RIGHT_DOT, LOGO_STROKE_OUTLINE, LOGO_VIEWBOX} from './logoGeometry';

/**
 * The official mark. `line` (0–1) reveals the tapered curve along its own
 * centerline via a mask, so the geometry is never stretched or scaled.
 */
export const LogoMark: React.FC<{
  width: number;
  color?: string;
  leftDot?: number;
  line?: number;
  rightDot?: number;
}> = ({width, color = COLORS.text, leftDot = 1, line = 1, rightDot = 1}) => {
  const id = useId().replace(/:/g, '');
  const {x, y, w, h} = LOGO_VIEWBOX;
  const p = Math.min(1, Math.max(0, line));
  return (
    <svg width={width} height={(width * h) / w} viewBox={`${x} ${y} ${w} ${h}`} style={{display: 'block', overflow: 'visible'}}>
      {p < 1 ? (
        <defs>
          <mask id={`m${id}`} maskUnits="userSpaceOnUse" x={x - 50} y={y - 50} width={w + 100} height={h + 100}>
            <path
              d={LOGO_CENTERLINE}
              fill="none"
              stroke="#fff"
              strokeWidth={150}
              strokeLinecap="butt"
              pathLength={1}
              strokeDasharray="1 1"
              strokeDashoffset={1 - p}
            />
          </mask>
        </defs>
      ) : null}
      {p > 0.001 ? <path d={LOGO_STROKE_OUTLINE} fill={color} mask={p < 1 ? `url(#m${id})` : undefined} /> : null}
      {leftDot > 0 ? <circle cx={LOGO_LEFT_DOT.cx} cy={LOGO_LEFT_DOT.cy} r={LOGO_LEFT_DOT.r * leftDot} fill={color} /> : null}
      {rightDot > 0 ? <circle cx={LOGO_RIGHT_DOT.cx} cy={LOGO_RIGHT_DOT.cy} r={LOGO_RIGHT_DOT.r * rightDot} fill={color} /> : null}
    </svg>
  );
};

/** Duration of the signature intro, in seconds. */
export const LOGO_INTRO_SECONDS = 2.0;

/**
 * Signature brand moment (reusable in every episode), always on the brand
 * beige with the anthracite emblem — exactly as the official logo file:
 * left dot → line drawn along its path → right dot → wordmark revealed.
 */
export const LogoIntro: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = (t: number) => t * fps;
  const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
  const ease = Easing.bezier(0.45, 0, 0.25, 1);
  const leftDot = interpolate(frame, [s(0.12), s(0.34)], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const line = interpolate(frame, [s(0.28), s(1.08)], [0, 1], {...clamp, easing: ease});
  const rightDot = interpolate(frame, [s(1.02), s(1.22)], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const letters = Array.from('NORMALİN TARİHİ');
  return (
    <div style={{position: 'absolute', inset: 0, background: COLORS.paper}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 760, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
        <LogoMark width={540} color={COLORS.text} leftDot={leftDot} line={line} rightDot={rightDot} />
        <div
          lang="tr"
          style={{
            marginTop: 64,
            fontFamily: FONT_FAMILY,
            ...TYPE.wordmark,
            paddingLeft: TYPE.wordmark.letterSpacing,
            color: COLORS.text,
            whiteSpace: 'pre',
          }}
        >
          {letters.map((ch, i) => {
            const st = s(1.14) + i * 1.3;
            const p = interpolate(frame, [st, st + 9], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
            return (
              <span key={i} style={{display: 'inline-block', opacity: p, transform: `translateY(${(1 - p) * 6}px)`}}>
                {ch === ' ' ? '\u00A0' : ch}
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
};
