// Dev helper: render a static illustration to SVG markup for quick checks.
// npx tsx scripts/preview-svg.tsx <name> > file.svg
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {PREVIEWS} from './previews';

const name = process.argv[2];
const P = PREVIEWS[name];
if (!P) throw new Error('unknown preview ' + name + ' — ' + Object.keys(PREVIEWS).join(', '));
const [w, h] = P.size ?? [1080, 1920];
process.stdout.write(
  renderToStaticMarkup(
    <svg xmlns="http://www.w3.org/2000/svg" width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <rect width={w} height={h} fill="#F7F6F2" />
      {P.el}
    </svg>,
  ),
);
