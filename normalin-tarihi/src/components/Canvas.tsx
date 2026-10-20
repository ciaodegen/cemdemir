import React from 'react';
import {AbsoluteFill} from 'remotion';
import {COLORS, VIDEO} from '../brand/theme';

/** Flat paper background + full-frame SVG in canvas pixel coordinates. */
export const Paper: React.FC<{children?: React.ReactNode; background?: string}> = ({children, background = COLORS.paper}) => (
  <AbsoluteFill style={{background}}>{children}</AbsoluteFill>
);

export const ArtSvg: React.FC<{children?: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <svg
    width={VIDEO.width}
    height={VIDEO.height}
    viewBox={`0 0 ${VIDEO.width} ${VIDEO.height}`}
    style={{position: 'absolute', inset: 0, ...style}}
  >
    {children}
  </svg>
);

/** Gentle camera move applied to an SVG group (scale around a focus point). */
export const cameraTransform = (scale: number, focusX: number, focusY: number, anchorX = 540, anchorY = 900) =>
  `translate(${anchorX} ${anchorY}) scale(${scale}) translate(${-focusX} ${-focusY})`;
