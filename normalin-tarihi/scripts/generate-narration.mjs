#!/usr/bin/env node
// Generates one narration file per script line (+ word timings when the
// provider returns them), then re-times the episode.
//
//   ELEVENLABS_API_KEY  (+ ELEVENLABS_VOICE_ID, optional ELEVENLABS_MODEL)
//   GOOGLE_TTS_API_KEY  (optional GOOGLE_TTS_VOICE, default tr-TR-Chirp3-HD-Charon)
//
//   node scripts/generate-narration.mjs 01
//
// Keys are read from the environment only and are never printed.
// A human recording works too: put <lineId>.wav files in public/audio/ep01/
// and run `npm run timing`.
import {execFileSync} from 'node:child_process';
import {mkdirSync, readFileSync, rmSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';

const ep = process.argv[2] ?? '01';
const root = new URL('..', import.meta.url).pathname;
const script = JSON.parse(readFileSync(join(root, `src/episodes/ep${ep}/script.json`), 'utf8'));
const outDir = join(root, `public/audio/ep${ep}`);
mkdirSync(outDir, {recursive: true});

/** char-level alignment → start time of each whitespace-separated word */
const wordStarts = (text, chars, starts) => {
  const out = [];
  let inWord = false;
  for (let i = 0; i < chars.length; i++) {
    const ws = /\s/.test(chars[i]);
    if (!ws && !inWord) out.push(starts[i]);
    inWord = !ws;
  }
  return out.length === text.split(/\s+/).filter(Boolean).length ? out : null;
};

const eleven = async (text) => {
  const voice = process.env.ELEVENLABS_VOICE_ID;
  if (!voice) throw new Error('Set ELEVENLABS_VOICE_ID to a native Turkish voice (Voice Library → language: Turkish).');
  const r = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voice}/with-timestamps?output_format=mp3_44100_192`, {
    method: 'POST',
    headers: {'xi-api-key': process.env.ELEVENLABS_API_KEY, 'content-type': 'application/json'},
    body: JSON.stringify({
      text,
      model_id: process.env.ELEVENLABS_MODEL ?? 'eleven_multilingual_v2',
      language_code: 'tr',
      // calm, warm documentary read: steady but not flat, light style
      voice_settings: {stability: 0.5, similarity_boost: 0.78, style: 0.18, use_speaker_boost: true, speed: 0.96},
    }),
  });
  if (!r.ok) throw new Error(`ElevenLabs HTTP ${r.status}: ${(await r.text()).slice(0, 300)}`);
  const j = await r.json();
  const a = j.normalized_alignment ?? j.alignment;
  return {audio: Buffer.from(j.audio_base64, 'base64'), words: a ? wordStarts(text, a.characters, a.character_start_times_seconds) : null};
};

const google = async (text) => {
  const r = await fetch('https://texttospeech.googleapis.com/v1/text:synthesize', {
    method: 'POST',
    headers: {'content-type': 'application/json', 'x-goog-api-key': process.env.GOOGLE_TTS_API_KEY},
    body: JSON.stringify({
      input: {text},
      voice: {languageCode: 'tr-TR', name: process.env.GOOGLE_TTS_VOICE ?? 'tr-TR-Chirp3-HD-Charon'},
      audioConfig: {audioEncoding: 'MP3', sampleRateHertz: 44100, speakingRate: 0.95},
    }),
  });
  if (!r.ok) throw new Error(`Google TTS HTTP ${r.status}: ${(await r.text()).slice(0, 300)}`);
  return {audio: Buffer.from((await r.json()).audioContent, 'base64'), words: null};
};

const synth = process.env.ELEVENLABS_API_KEY ? eleven : process.env.GOOGLE_TTS_API_KEY ? google : null;
if (!synth) {
  console.error('No TTS provider configured: set ELEVENLABS_API_KEY (+ ELEVENLABS_VOICE_ID) or GOOGLE_TTS_API_KEY.');
  process.exit(1);
}

const probe = (f) => Number(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString().trim());

for (const line of script.lines) {
  const target = join(outDir, `${line.id}.mp3`);
  const parts = line.ttsParts ?? [line.text];
  const tmp = join(tmpdir(), `nt-${line.id}`);
  mkdirSync(tmp, {recursive: true});
  const files = [];
  let words = [];
  let offset = 0;
  for (let i = 0; i < parts.length; i++) {
    const {audio, words: w} = await synth(parts[i]);
    const f = join(tmp, `p${i}.mp3`);
    writeFileSync(f, audio);
    files.push(f);
    words = w && words ? [...words, ...w.map((x) => x + offset)] : null;
    offset += probe(f);
    const pause = line.pauses?.[i];
    if (pause && i < parts.length - 1) {
      const sil = join(tmp, `s${i}.mp3`);
      execFileSync('ffmpeg', ['-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', String(pause), '-q:a', '2', sil]);
      files.push(sil);
      offset += pause;
    }
  }
  if (files.length === 1) writeFileSync(target, readFileSync(files[0]));
  else {
    const list = join(tmp, 'list.txt');
    writeFileSync(list, files.map((f) => `file '${f}'`).join('\n'));
    execFileSync('ffmpeg', ['-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-ar', '44100', '-ac', '1', '-b:a', '192k', target]);
  }
  const wordsFile = join(outDir, `${line.id}.words.json`);
  if (words) writeFileSync(wordsFile, JSON.stringify(words.map((x) => Number(x.toFixed(3)))) + '\n');
  else rmSync(wordsFile, {force: true});
  rmSync(tmp, {recursive: true, force: true});
  console.log('✓', line.id, `${probe(target).toFixed(2)}s`, words ? '(word timings)' : '', '—', line.text);
}
execFileSync('node', [join(root, 'scripts/build-timing.mjs'), ep], {stdio: 'inherit'});
