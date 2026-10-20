import React, {useEffect, useState} from 'react';
import {continueRender, delayRender} from 'remotion';
import '@fontsource/montserrat/600.css';
import '@fontsource/montserrat/700.css';

const TR = 'Neden tokalaşıyoruz? NORMALİN TARİHİ İıŞşĞğÇçÖöÜü…’';

/** Blocks rendering until Montserrat (incl. Turkish glyphs) is ready. */
export const FontGate: React.FC<{children: React.ReactNode}> = ({children}) => {
  const [handle] = useState(() => delayRender('Loading fonts'));
  useEffect(() => {
    Promise.all(['600', '700'].map((w) => document.fonts.load(`${w} 40px 'Montserrat'`, TR)))
      .then(() => document.fonts.ready)
      .then(() => continueRender(handle))
      .catch(() => continueRender(handle));
  }, [handle]);
  return <>{children}</>;
};
