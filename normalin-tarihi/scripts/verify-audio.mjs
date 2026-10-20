#!/usr/bin/env node
// Checks that a rendered MP4 really carries audible narration.
//   node scripts/verify-audio.mjs out/normalin-tarihi-ep01.mp4
import {execFileSync, spawnSync} from 'node:child_process';

const file = process.argv[2];
const streams = execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_name,sample_rate,channels', '-of', 'csv=p=0', file]).toString().trim();
if (!streams) {
  console.error('FAIL: no audio stream');
  process.exit(1);
}
const vd = spawnSync('ffmpeg', ['-i', file, '-vn', '-af', 'volumedetect,silencedetect=n=-40dB:d=2.5', '-f', 'null', '-'], {encoding: 'utf8'}).stderr;
const mean = Number(/mean_volume: (-?[\d.]+) dB/.exec(vd)?.[1]);
const max = Number(/max_volume: (-?[\d.]+) dB/.exec(vd)?.[1]);
const silences = [...vd.matchAll(/silence_start: ([\d.]+)[\s\S]*?silence_duration: ([\d.]+)/g)].map((m) => [Number(m[1]), Number(m[2])]);
console.log(`audio: ${streams} | mean ${mean} dB | max ${max} dB | silent gaps > 2.5 s: ${silences.length ? silences.map(([s, d]) => `${s.toFixed(1)}s(+${d.toFixed(1)})`).join(', ') : 'none'}`);
if (!(max > -20 && mean > -45)) {
  console.error('FAIL: audio track is silent or far too quiet');
  process.exit(1);
}
console.log('OK: audible narration present');
