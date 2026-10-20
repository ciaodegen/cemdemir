#!/usr/bin/env node
// Measures narration files and writes the timing manifest the video reads.
// Looks for public/audio/ep<NN>/<lineId>.(wav|mp3|m4a). Lines without audio
// are left null and timed by text-length estimate inside the composition.
//   node scripts/build-timing.mjs [episode=01]
import {execFileSync} from 'node:child_process';
import {existsSync, readFileSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';

const ep = process.argv[2] ?? '01';
const root = new URL('..', import.meta.url).pathname;
const script = JSON.parse(readFileSync(join(root, `src/episodes/ep${ep}/script.json`), 'utf8'));
const out = {};
let found = 0;
for (const line of script.lines) {
  let entry = {file: null, duration: null};
  for (const ext of ['wav', 'mp3', 'm4a']) {
    const rel = `audio/ep${ep}/${line.id}.${ext}`;
    const abs = join(root, 'public', rel);
    if (!existsSync(abs)) continue;
    const d = execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', abs]).toString().trim();
    entry = {file: rel, duration: Number(Number(d).toFixed(3))};
    found++;
    break;
  }
  out[line.id] = entry;
}
writeFileSync(join(root, `src/episodes/ep${ep}/timing.generated.json`), JSON.stringify(out, null, 2) + '\n');
console.log(`ep${ep}: ${found}/${script.lines.length} narration lines have audio` + (found < script.lines.length ? ' (others use text-length estimates)' : ''));
