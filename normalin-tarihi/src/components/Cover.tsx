import React from 'react';
import {AbsoluteFill} from 'remotion';
import {COLORS, FONT_FAMILY, TYPE} from '../brand/theme';
import {LogoMark} from '../brand/Logo';
import {ArtSvg} from './Canvas';

/**
 * Instagram cover (1080×1920). Everything that matters sits inside the
 * central 1080×1080 square so the profile-grid crop (1:1 or 3:4) keeps it.
 */
export const Cover: React.FC<{titleLines: string[]; children: React.ReactNode}> = ({titleLines, children}) => (
  <AbsoluteFill style={{background: COLORS.paper}}>
    <div style={{position: 'absolute', top: 470, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      <LogoMark width={130} color={COLORS.text} />
      <div
        style={{
          marginTop: 22,
          fontFamily: FONT_FAMILY,
          fontWeight: 500,
          fontSize: 26,
          letterSpacing: '0.3em',
          paddingLeft: '0.3em',
          color: COLORS.text,
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
        fontFamily: FONT_FAMILY,
        ...TYPE.title,
        fontSize: 104,
        color: COLORS.text,
      }}
    >
      {titleLines.map((l) => (
        <div key={l} style={{color: l.startsWith('*') ? COLORS.highlight : COLORS.text}}>
          {l.replace(/\*/g, '')}
        </div>
      ))}
    </div>
    <ArtSvg>{children}</ArtSvg>
  </AbsoluteFill>
);
