// Normalin Tarihi — brand constants shared by every episode.
export const COLORS = {
  paper: '#F7F6F2',
  ink: '#222222',
  accent: '#A49B8E',
  night: '#111111',
} as const;

export const FONT_FAMILY = "'Inter', 'Helvetica Neue', Arial, sans-serif";

export const VIDEO = {width: 1080, height: 1920, fps: 30} as const;

/** Single line weight for all illustrations (px on the 1080×1920 canvas). */
export const STROKE = 2.6;

/**
 * Instagram Reels safe areas on 1080×1920. The top ~220px (header) and the
 * bottom ~420px (caption, audio label, actions) are covered by UI; the right
 * edge holds the action buttons. Keep text and key art inside SAFE.
 */
export const SAFE = {top: 250, bottom: 1500, left: 90, right: 940} as const;

/** Vertical anchors used across episodes so layouts stay identical. */
export const LAYOUT = {
  questionY: 470,
  artCenterY: 900,
  subtitleY: 1395,
} as const;
