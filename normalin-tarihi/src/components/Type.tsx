import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONT_FAMILY, TYPE} from '../brand/theme';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

type Style = {fontSize: number; fontWeight: number; lineHeight: number; letterSpacing: string};

/**
 * The house text reveal: words are laid out up front (no reflow) and each
 * one eases in with a soft fade and a small rise. Used by titles, labels,
 * subtitles and the sign-off so every line of text moves the same way.
 * `times` gives each word's start frame; otherwise words are spread evenly
 * (weighted by length) between `from` and `to`.
 */
/**
 * Highlight markup: wrap words in *asterisks* (one or several words) to set
 * them in COLOR B. Markers never change the word count, so narration word
 * timings still line up.
 */
export const parseHighlights = (text: string) => {
  let on = false;
  return text
    .split(/\s+/)
    .filter(Boolean)
    .map((raw) => {
      const opens = raw.startsWith('*');
      const closes = raw.endsWith('*') && raw.length > 1;
      if (opens) on = true;
      const word = raw.replace(/\*/g, '');
      const hl = on;
      if (closes) on = false;
      return {word, hl};
    });
};

export const stripHighlights = (text: string) => text.replace(/\*/g, '');

export const WordReveal: React.FC<{
  text: string;
  from: number;
  to: number;
  type: Style;
  times?: number[];
  wordFrames?: number;
  style?: React.CSSProperties;
}> = ({text, from, to, type, times, wordFrames = 8, style}) => {
  const frame = useCurrentFrame();
  const tokens = parseHighlights(text);
  const words = tokens.map((t) => t.word);
  const weights = words.map((w) => w.length + 2);
  const total = weights.reduce((a, b) => a + b, 0);
  let acc = 0;
  return (
    <div
      lang="tr"
      style={
        {
          fontFamily: FONT_FAMILY,
          color: COLORS.text,
          textAlign: 'center',
          textWrap: 'balance',
          ...type,
          ...style,
        } as React.CSSProperties
      }
    >
      {words.map((w, i) => {
        const start = times?.[i] ?? from + ((to - from) * acc) / total;
        acc += weights[i];
        const p = interpolate(frame, [start, start + wordFrames], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              opacity: p,
              transform: `translateY(${(1 - p) * 8}px)`,
              marginRight: i < words.length - 1 ? '0.26em' : 0,
              color: tokens[i].hl ? COLORS.highlight : undefined,
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

/**
 * Large headline: a bigger, bolder version of the subtitle type, revealed
 * word by word. `lines` are stacked and centred; use *word* for COLOR B.
 */
export const Title: React.FC<{lines: string[]; from: number; to: number; top: number; out?: number; size?: number}> = ({
  lines,
  from,
  to,
  top,
  out,
  size,
}) => {
  const frame = useCurrentFrame();
  const fade = out !== undefined ? interpolate(frame, [out, out + 14], [1, 0], clamp) : 1;
  const counts = lines.map((l) => l.split(/\s+/).filter(Boolean).length);
  const total = counts.reduce((a, b) => a + b, 0);
  let seen = 0;
  return (
    <div style={{position: 'absolute', top, left: 70, right: 70, opacity: fade}}>
      {lines.map((l, i) => {
        const a = from + ((to - from) * seen) / total;
        seen += counts[i];
        const b = from + ((to - from) * seen) / total;
        return <WordReveal key={i} text={l} from={a} to={b} type={size ? {...TYPE.title, fontSize: size} : TYPE.title} wordFrames={12} />;
      })}
    </div>
  );
};

/** Small place / period label at the top of a scene. */
export const Label: React.FC<{text: string; from?: number; to?: number; top?: number}> = ({text, from = 8, to, top = 300}) => {
  const frame = useCurrentFrame();
  const o = to !== undefined ? interpolate(frame, [to - 12, to], [1, 0], clamp) : 1;
  return (
    <div style={{position: 'absolute', top, left: 90, right: 90, opacity: o}}>
      <WordReveal text={text} from={from} to={from + 6 * text.split(' ').length} type={TYPE.label} wordFrames={12} />
    </div>
  );
};
