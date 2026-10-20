import React from 'react';
import {AbsoluteFill} from 'remotion';
import {COLORS, FONT_FAMILY} from '../brand/theme';
import {LogoMark} from '../brand/Logo';
import {ArtSvg} from './Canvas';

/**
 * Instagram cover (1080×1920). Everything that matters sits inside the
 * central 1080×1080 square so the profile-grid crop (1:1 or 3:4) keeps it.
 */
export const Cover: React.FC<{title: string; children: React.ReactNode}> = ({title, children}) => (
  <AbsoluteFill style={{background: COLORS.paper}}>
    <div style={{position: 'absolute', top: 520, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      <LogoMark width={120} color={COLORS.ink} />
      <div
        style={{
          marginTop: 26,
          fontFamily: FONT_FAMILY,
          fontWeight: 500,
          fontSize: 26,
          letterSpacing: '0.34em',
          paddingLeft: '0.34em',
          color: COLORS.ink,
        }}
      >
        NORMALİN TARİHİ
      </div>
    </div>
    <ArtSvg>{children}</ArtSvg>
    <div
      lang="tr"
      style={{
        position: 'absolute',
        top: 1180,
        left: 80,
        right: 80,
        textAlign: 'center',
        fontFamily: FONT_FAMILY,
        fontWeight: 500,
        fontSize: 92,
        letterSpacing: '-0.02em',
        lineHeight: 1.08,
        color: COLORS.ink,
      }}
    >
      {title}
    </div>
  </AbsoluteFill>
);
