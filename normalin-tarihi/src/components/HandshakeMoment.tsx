import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {
  CLASP_A_ANGLE as A_ANGLE,
  CLASP_A_WRIST as A_WRIST,
  CLASP_B_ANGLE as B_ANGLE,
  CLASP_B_WRIST as B_WRIST,
  CLASP_HANDS,
  ClaspSkin,
  MeetSpark,
  SleeveStyle,
  openHandPaths,
  sleevePaths,
} from '../illustrations/hands';
import {Ink} from './Ink';


const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/**
 * Signature handshake: two hands glide in from the frame edges, meet,
 * clasp and shake. Optionally release and withdraw. All timings are frames
 * relative to the enclosing <Sequence>.
 */
export const HandshakeMoment: React.FC<{
  cx?: number;
  cy: number;
  scale?: number;
  enter: number;
  meet: number;
  release?: number;
  sleeveA?: SleeveStyle;
  sleeveB?: SleeveStyle;
  spark?: boolean;
}> = ({cx = 540, cy, scale = 1.25, enter, meet, release, sleeveA = 'modern', sleeveB = 'modernOlive', spark = true}) => {
  const frame = useCurrentFrame();
  const s = scale;
  const offscreen = 760 * s;
  const approach = Easing.bezier(0.25, 0.1, 0.25, 1);
  // 0 = off screen, 1 = at the clasp position
  let reach = interpolate(frame, [enter, meet], [0, 1], {...clamp, easing: approach});
  let clasp = interpolate(frame, [meet - 3, meet + 3], [0, 1], clamp);
  let shakeT = frame - meet - 2;
  if (release !== undefined) {
    const unclasp = interpolate(frame, [release, release + 6], [1, 0], clamp);
    clasp = Math.min(clasp, unclasp);
    const back = interpolate(frame, [release + 4, release + 40], [1, 0], {...clamp, easing: Easing.in(Easing.cubic)});
    if (frame > release) reach = back;
  }
  // gentle rise into the meeting point, then a two-beat shake that settles
  const rise = (1 - reach) * 36 * s;
  const shake = shakeT > 0 && shakeT < 34 && (release === undefined || frame < release)
    ? Math.sin((shakeT / 17) * Math.PI * 2) * 9 * s * (1 - shakeT / 40)
    : 0;
  const tilt = shake * 0.08;

  const ax = cx + A_WRIST.x * s - (1 - reach) * offscreen;
  const bx = cx + B_WRIST.x * s + (1 - reach) * offscreen;
  const ay = cy + A_WRIST.y * s + rise + shake;
  const by = cy + B_WRIST.y * s + rise + shake;
  const sparkOpacity = spark
    ? Math.min(
        interpolate(frame, [meet + 2, meet + 8], [0, 1], clamp),
        interpolate(frame, [meet + 34, meet + 46], [1, 0], clamp),
      )
    : 0;
  const sparkDraw = interpolate(frame, [meet + 2, meet + 12], [0, 1], clamp);
  if (reach <= 0 && frame > enter) return null;
  return (
    <g>
      {/* sleeves (shared by the open and clasped states) */}
      <g transform={`translate(${ax} ${ay}) rotate(${A_ANGLE + tilt}) scale(${s})`}>
        <Ink paths={sleevePaths(sleeveA, 'light')} />
        <g opacity={1 - clasp}>
          <Ink paths={openHandPaths('light')} />
        </g>
      </g>
      <g transform={`translate(${bx} ${by}) scale(-1 1) rotate(${B_ANGLE - tilt}) scale(${s})`}>
        <Ink paths={sleevePaths(sleeveB, 'deep')} />
        <g opacity={1 - clasp}>
          <Ink paths={openHandPaths('deep')} />
        </g>
      </g>
      {clasp > 0 ? (
        <g transform={`translate(${cx} ${cy + rise + shake}) rotate(${tilt}) scale(${s})`} opacity={clasp}>
          <ClaspSkin />
          <Ink paths={CLASP_HANDS} />
        </g>
      ) : null}
      {sparkOpacity > 0 ? (
        <g transform={`translate(${cx} ${cy - 10 * s}) scale(${s})`}>
          <MeetSpark draw={sparkDraw} opacity={sparkOpacity} />
        </g>
      ) : null}
    </g>
  );
};
