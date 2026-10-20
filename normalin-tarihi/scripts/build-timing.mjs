#!/usr/bin/env node
// Measures narration files and writes the timing manifest the video reads.
// Looks for public/audio/ep<NN>/<lineId>.(wav|mp3|m4a) and optional
// <lineId>.words.json (word start times). Lines without audio are left null
// and timed by a text-length estimate inside the composition.
//   node scripts/build-timing.mjs [episode=01] [--require-audio]
import {execFileSync} from 'node:child_process';
import {existsSync, readFileSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';

const args = process.argv.slice(2);
const ep = args.find((a) => !a.startsWith('--')) ?? '01';
const requireAudio = args.includes('--require-audio');
const root = new URL('..', import.meta.url).pathname;
const script = JSON.parse(readFileSync(join(root, `src/episodes/ep${ep}/script.json`), 'utf8'));
const out = {};
const missing = [];
for (const line of script.lines) {
  let entry = {file: null, duration: null, words: null};
  for (const ext of ['wav', 'mp3', 'm4a']) {
    const rel = `audio/ep${ep}/${line.id}.${ext}`;
    const abs = join(root, 'public', rel);
    if (!existsSync(abs)) continue;
    const d = execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', abs]).toString().trim();
    const wf = join(root, 'public', `audio/ep${ep}/${line.id}.words.json`);
    entry = {file: rel, duration: Number(Number(d).toFixed(3)), words: existsSync(wf) ? JSON.parse(readFileSync(wf, 'utf8')) : null};
    break;
  }
  if (!entry.file) missing.push(line.id);
  out[line.id] = entry;
}
writeFileSync(join(root, `src/episodes/ep${ep}/timing.generated.json`), JSON.stringify(out, null, 2) + '\n');
const n = script.lines.length;
console.log(`ep${ep}: ${n - missing.length}/${n} narration lines have audio`);
if (requireAudio && missing.length) {
  console.error(`Refusing to render the final video without narration. Missing: ${missing.join(', ')}.\nRun \`npm run tts ${ep}\` (needs a TTS key) or add recorded files to public/audio/ep${ep}/.`);
  process.exit(1);
}
