import React, {useId} from 'react';
import {Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, FONT_FAMILY} from './theme';
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
}> = ({width, color = COLORS.ink, leftDot = 1, line = 1, rightDot = 1}) => {
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
 * Signature brand transition (reusable in every episode):
 * left dot → line drawn along its path → right dot → wordmark fade-in.
 */
export const LogoIntro: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = (t: number) => t * fps;
  const ease = Easing.bezier(0.45, 0, 0.25, 1);
  const leftDot = interpolate(frame, [s(0.1), s(0.3)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const line = interpolate(frame, [s(0.26), s(1.08)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  const rightDot = interpolate(frame, [s(1.02), s(1.22)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const text = interpolate(frame, [s(1.18), s(1.6)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.quad)});
  return (
    <div style={{position: 'absolute', inset: 0, background: COLORS.night}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 760, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
        <LogoMark width={540} color={COLORS.paper} leftDot={leftDot} line={line} rightDot={rightDot} />
        <div
          style={{
            marginTop: 64,
            fontFamily: FONT_FAMILY,
            fontWeight: 500,
            fontSize: 38,
            letterSpacing: '0.34em',
            paddingLeft: '0.34em',
            color: COLORS.paper,
            opacity: text,
            transform: `translateY(${(1 - text) * 8}px)`,
          }}
        >
          NORMALİN TARİHİ
        </div>
      </div>
    </div>
  );
};
