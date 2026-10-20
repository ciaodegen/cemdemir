import React, {useEffect, useState} from 'react';
import {continueRender, delayRender} from 'remotion';
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';

/** Blocks rendering until Inter (incl. Turkish glyphs) is ready. */
export const FontGate: React.FC<{children: React.ReactNode}> = ({children}) => {
  const [handle] = useState(() => delayRender('Loading Inter'));
  useEffect(() => {
    Promise.all([
      document.fonts.load("400 40px 'Inter'", 'İıŞşĞğÇçÖöÜü'),
      document.fonts.load("500 40px 'Inter'", 'İıŞşĞğÇçÖöÜü'),
    ])
      .then(() => document.fonts.ready)
      .then(() => continueRender(handle))
      .catch(() => continueRender(handle));
  }, [handle]);
  return <>{children}</>;
};
