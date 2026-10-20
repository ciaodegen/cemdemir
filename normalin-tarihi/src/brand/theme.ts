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
  night: '#111111',
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
  labelInk: '#7E6A57',
} as const;

export const FONTS = {
  /** handwritten titles, labels and sign-off */
  hand: "'Kalam', 'Caveat', cursive",
  /** narration subtitles and small UI text */
  sans: "'DM Sans', 'Helvetica Neue', Arial, sans-serif",
} as const;

/** @deprecated kept for older imports — use FONTS.sans */
export const FONT_FAMILY = FONTS.sans;

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
