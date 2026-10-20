// Normalin Tarihi — brand constants shared by every episode.
export const COLORS = {
  /** sampled from the official profile picture */
  paper: '#FEF9EE',
  paperFallback: '#F7F6F2',
  ink: '#292724',
  sand: '#D9C3A3',
  camel: '#B89470',
  terracotta: '#BC8066',
  olive: '#858B74',
  taupe: '#A69B8B',
  /** COLOR A — emblem / text anthracite, sampled from the official logo */
  text: '#25221E',
  /**
   * COLOR B — warm caramel highlight for key words.
   * PROVISIONAL: replace with the value sampled from the approved
   * BECAME reference screenshot once it is available.
   */
  highlight: '#B07D45',
  // derived tints (same hues, lighter) for large areas
  sandLight: '#EADCC6',
  sandPale: '#F3E9D8',
  oliveLight: '#B3B49E',
  taupeLight: '#CFC6B8',
  terracottaLight: '#D9A88F',
  skin: '#E4C3A0',
  skinDeep: '#C99E78',
  hair: '#5F4C3E',
  linen: '#F6EEE0',
  stone: '#DCCDB5',
} as const;

/** One typeface for the whole brand; hierarchy comes from size and weight. */
export const FONT_FAMILY = "'Montserrat', 'Helvetica Neue', Arial, sans-serif";

export const TYPE = {
  title: {fontSize: 100, fontWeight: 700, lineHeight: 1.12, letterSpacing: '-0.02em'},
  ending: {fontSize: 58, fontWeight: 700, lineHeight: 1.2, letterSpacing: '-0.015em'},
  label: {fontSize: 46, fontWeight: 700, lineHeight: 1.2, letterSpacing: '-0.01em'},
  subtitle: {fontSize: 40, fontWeight: 600, lineHeight: 1.4, letterSpacing: '-0.005em'},
  small: {fontSize: 26, fontWeight: 600, lineHeight: 1.2, letterSpacing: '0em'},
  wordmark: {fontSize: 34, fontWeight: 700, lineHeight: 1, letterSpacing: '0.26em'},
} as const;

export const VIDEO = {width: 1080, height: 1920, fps: 30} as const;

/** Single line weight for all illustrations (px on the 1080×1920 canvas). */
export const STROKE = 2.8;

/**
 * Instagram Reels safe areas on 1080×1920. The top ~220px (header) and the
 * bottom ~420px (caption, audio label, actions) are covered by UI; the right
 * edge holds the action buttons. Keep text and key art inside SAFE.
 */
export const SAFE = {top: 250, bottom: 1500, left: 90, right: 940} as const;

/** Vertical anchors used across episodes so layouts stay identical. */
export const LAYOUT = {
  titleY: 300,
  labelY: 300,
  artTop: 440,
  groundY: 1290,
  artBottom: 1330,
  subtitleY: 1372,
} as const;
