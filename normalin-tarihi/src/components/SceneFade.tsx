import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

/**
 * House transition: each scene breathes in from, and out to, the paper.
 * Wrap the contents of a <Sequence> with it.
 */
export const SceneFade: React.FC<{duration: number; fadeIn?: number; fadeOut?: number; children: React.ReactNode}> = ({
  duration,
  fadeIn = 9,
  fadeOut = 9,
  children,
}) => {
  const frame = useCurrentFrame();
  const a = fadeIn > 0 ? interpolate(frame, [0, fadeIn], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1;
  const b = fadeOut > 0 ? interpolate(frame, [duration - fadeOut, duration], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1;
  return <AbsoluteFill style={{opacity: Math.min(a, b)}}>{children}</AbsoluteFill>;
};

/** Cross-dissolve helper for swapping two drawings inside one scene. */
export const dissolve = (frame: number, at: number, length = 8) =>
  interpolate(frame, [at, at + length], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
