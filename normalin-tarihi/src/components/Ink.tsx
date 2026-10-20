import React from 'react';
import {COLORS, STROKE} from '../brand/theme';

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

/**
 * A stroke, optionally with a flat colour fill. Strings are outline-only.
 * `stroke: false` gives a fill-only shape (soft background masses).
 */
export type InkPath =
  | string
  | {d: string; fill?: string; fillOpacity?: number; width?: number; color?: string; stroke?: boolean};

/**
 * One line-art stroke that is drawn on along its real SVG path.
 * The fill washes in during the second half of the stroke, like colour
 * laid down after the outline.
 */
export const InkLine: React.FC<{
  d: string;
  draw?: number;
  width?: number;
  color?: string;
  fill?: string;
  fillOpacity?: number;
  stroke?: boolean;
  opacity?: number;
}> = ({d, draw = 1, width = STROKE, color = COLORS.ink, fill, fillOpacity = 1, stroke = true, opacity = 1}) => {
  const p = clamp01(draw);
  if (p <= 0.002) return null;
  const done = p >= 0.999;
  const fillA = fill ? clamp01((p - 0.45) / 0.55) * fillOpacity : 0;
  return (
    <g opacity={opacity}>
      {fill && fillA > 0 ? <path d={d} fill={fill} fillOpacity={fillA} stroke="none" /> : null}
      {stroke ? (
        <path
          d={d}
          fill="none"
          stroke={color}
          strokeWidth={width}
          strokeLinecap="round"
          strokeLinejoin="round"
          vectorEffect="non-scaling-stroke"
          pathLength={done ? undefined : 1}
          strokeDasharray={done ? undefined : '1 1'}
          strokeDashoffset={done ? undefined : 1 - p}
        />
      ) : null}
    </g>
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
  if (n === 0) return null;
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
            fillOpacity={item.fillOpacity}
            stroke={item.stroke ?? true}
          />
        );
      })}
    </>
  );
};

/** Flat colour mass without outline that fades in (skies, hills, ground). */
export const Wash: React.FC<{d: string; fill: string; opacity?: number}> = ({d, fill, opacity = 1}) =>
  opacity > 0.002 ? <path d={d} fill={fill} opacity={clamp01(opacity)} /> : null;
