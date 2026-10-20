import React from 'react';
import {AbsoluteFill} from 'remotion';
import {COLORS, FONTS} from '../brand/theme';
import {LogoMark} from '../brand/Logo';
import {ArtSvg} from './Canvas';

/**
 * Instagram cover (1080×1920). Everything that matters sits inside the
 * central 1080×1080 square so the profile-grid crop (1:1 or 3:4) keeps it.
 */
export const Cover: React.FC<{titleLines: string[]; children: React.ReactNode}> = ({titleLines, children}) => (
  <AbsoluteFill style={{background: COLORS.paper}}>
    <div style={{position: 'absolute', top: 470, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      <LogoMark width={110} color={COLORS.ink} />
      <div
        style={{
          marginTop: 22,
          fontFamily: "'Inter', sans-serif",
          fontWeight: 500,
          fontSize: 24,
          letterSpacing: '0.34em',
          paddingLeft: '0.34em',
          color: COLORS.ink,
        }}
      >
        NORMALİN TARİHİ
      </div>
    </div>
    <div
      lang="tr"
      style={{
        position: 'absolute',
        top: 620,
        left: 60,
        right: 60,
        textAlign: 'center',
        fontFamily: FONTS.hand,
        fontWeight: 700,
        fontSize: 132,
        lineHeight: 1.02,
        color: COLORS.ink,
      }}
    >
      {titleLines.map((l) => (
        <div key={l}>{l}</div>
      ))}
    </div>
    <ArtSvg>{children}</ArtSvg>
  </AbsoluteFill>
);
