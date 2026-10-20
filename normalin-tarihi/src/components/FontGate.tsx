import React, {useEffect, useState} from 'react';
import {continueRender, delayRender} from 'remotion';
import '@fontsource/kalam/700.css';
import '@fontsource/dm-sans/400.css';
import '@fontsource/dm-sans/500.css';
import '@fontsource/dm-sans/600.css';
import '@fontsource/inter/500.css';

const TR = 'Neden tokalaşıyoruz? İıŞşĞğÇçÖöÜü…’';

/** Blocks rendering until Kalam + DM Sans (incl. Turkish glyphs) are ready. */
export const FontGate: React.FC<{children: React.ReactNode}> = ({children}) => {
  const [handle] = useState(() => delayRender('Loading fonts'));
  useEffect(() => {
    Promise.all([
      document.fonts.load("700 80px 'Kalam'", TR),
      document.fonts.load("500 40px 'DM Sans'", TR),
      document.fonts.load("400 40px 'DM Sans'", TR),
      document.fonts.load("500 40px 'Inter'", 'NORMALİN TARİHİ'),
    ])
      .then(() => document.fonts.ready)
      .then(() => continueRender(handle))
      .catch(() => continueRender(handle));
  }, [handle]);
  return <>{children}</>;
};
