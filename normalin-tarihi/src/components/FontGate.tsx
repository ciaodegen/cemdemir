import React, {useEffect, useState} from 'react';
import {continueRender, delayRender} from 'remotion';
import '@fontsource/dm-sans/400.css';
import '@fontsource/dm-sans/500.css';
import '@fontsource/dm-sans/600.css';

const TR = 'Neden tokalaşıyoruz? NORMALİN TARİHİ İıŞşĞğÇçÖöÜü…’';

/** Blocks rendering until DM Sans (incl. Turkish glyphs) is ready. */
export const FontGate: React.FC<{children: React.ReactNode}> = ({children}) => {
  const [handle] = useState(() => delayRender('Loading fonts'));
  useEffect(() => {
    Promise.all(['400', '500', '600'].map((w) => document.fonts.load(`${w} 40px 'DM Sans'`, TR)))
      .then(() => document.fonts.ready)
      .then(() => continueRender(handle))
      .catch(() => continueRender(handle));
  }, [handle]);
  return <>{children}</>;
};
