#!/usr/bin/env node
// QA helper: renders selected frames of a composition from one bundle.
//   node scripts/stills.mjs <compId> <outDir> <frame> [frame...]
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {mkdirSync} from 'node:fs';
import {join} from 'node:path';

const [id, outDir, ...frames] = process.argv.slice(2);
mkdirSync(outDir, {recursive: true});
const root = new URL('..', import.meta.url).pathname;
const serveUrl = await bundle({entryPoint: join(root, 'src/index.ts')});
const browserExecutable = process.env.REMOTION_BROWSER ?? null;
const composition = await selectComposition({serveUrl, id, browserExecutable});
for (const f of frames) {
  const output = join(outDir, `${id}-${String(f).padStart(5, '0')}.png`);
  await renderStill({serveUrl, composition, frame: Number(f), output, browserExecutable, overwrite: true});
  console.log(output);
}
