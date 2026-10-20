import React from 'react';
import {COLORS, STROKE} from '../brand/theme';

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

export type InkPath = string | {d: string; fill?: string; width?: number; color?: string};

/**
 * One line-art stroke that can be drawn on along its real SVG path.
 * `draw` 0 → invisible, 1 → fully drawn.
 */
export const InkLine: React.FC<{
  d: string;
  draw?: number;
  width?: number;
  color?: string;
  fill?: string;
  opacity?: number;
}> = ({d, draw = 1, width = STROKE, color = COLORS.ink, fill, opacity = 1}) => {
  const p = clamp01(draw);
  if (p <= 0.002) return null;
  const done = p >= 0.999;
  return (
    <path
      d={d}
      fill={fill && done ? fill : 'none'}
      stroke={color}
      strokeWidth={width}
      strokeLinecap="round"
      strokeLinejoin="round"
      vectorEffect="non-scaling-stroke"
      pathLength={done ? undefined : 1}
      strokeDasharray={done ? undefined : '1 1'}
      strokeDashoffset={done ? undefined : 1 - p}
      opacity={opacity}
    />
  );
};

/**
 * A group of strokes drawn in order. `draw` is the progress of the whole set;
 * `overlap` lets consecutive strokes start before the previous one finishes,
 * which reads like one continuous hand drawing.
 */
export const Ink: React.FC<{
  paths: InkPath[];
  draw?: number;
  overlap?: number;
  width?: number;
  color?: string;
}> = ({paths, draw = 1, overlap = 0.6, width, color}) => {
  const n = paths.length;
  const span = 1 / (n - (n - 1) * overlap || 1);
  return (
    <>
      {paths.map((p, i) => {
        const start = i * span * (1 - overlap);
        const local = (draw - start) / span;
        const item = typeof p === 'string' ? {d: p} : p;
        return (
          <InkLine
            key={i}
            d={item.d}
            draw={draw >= 1 ? 1 : local}
            width={item.width ?? width}
            color={item.color ?? color}
            fill={item.fill}
          />
        );
      })}
    </>
  );
};
