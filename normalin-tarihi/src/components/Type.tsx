import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONT_FAMILY, TYPE} from '../brand/theme';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

type Style = (typeof TYPE)[keyof typeof TYPE];

/**
 * The house text reveal: words are laid out up front (no reflow) and each
 * one eases in with a soft fade and a small rise. Used by titles, labels,
 * subtitles and the sign-off so every line of text moves the same way.
 * `times` gives each word's start frame; otherwise words are spread evenly
 * (weighted by length) between `from` and `to`.
 */
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
  const words = text.split(/\s+/).filter(Boolean);
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
          <span key={i} style={{display: 'inline-block', opacity: p, transform: `translateY(${(1 - p) * 8}px)`, marginRight: i < words.length - 1 ? '0.26em' : 0}}>
            {w}
          </span>
        );
      })}
    </div>
  );
};

/** Large opening title: a bigger version of the subtitle type, word by word. */
export const Title: React.FC<{text: string; from: number; to: number; top: number; out?: number}> = ({text, from, to, top, out}) => {
  const frame = useCurrentFrame();
  const fade = out !== undefined ? interpolate(frame, [out, out + 14], [1, 0], clamp) : 1;
  return (
    <div style={{position: 'absolute', top, left: 90, right: 90, opacity: fade}}>
      <WordReveal text={text} from={from} to={to} type={TYPE.title} wordFrames={12} />
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
