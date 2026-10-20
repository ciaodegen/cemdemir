#!/usr/bin/env node
// Generates one narration file per script line, then re-times the episode.
//   ELEVENLABS_API_KEY=... ELEVENLABS_VOICE_ID=... node scripts/generate-narration.mjs 01
//   GOOGLE_TTS_API_KEY=...  [GOOGLE_TTS_VOICE=tr-TR-Chirp3-HD-Charon] node scripts/generate-narration.mjs 01
// Recorded human voice-over works too: drop <lineId>.wav files into
// public/audio/ep01/ and run `npm run timing`.
import {execFileSync} from 'node:child_process';
import {mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';

const ep = process.argv[2] ?? '01';
const root = new URL('..', import.meta.url).pathname;
const script = JSON.parse(readFileSync(join(root, `src/episodes/ep${ep}/script.json`), 'utf8'));
const outDir = join(root, `public/audio/ep${ep}`);
mkdirSync(outDir, {recursive: true});

const eleven = async (text) => {
  const voice = process.env.ELEVENLABS_VOICE_ID;
  if (!voice) throw new Error('Set ELEVENLABS_VOICE_ID to a Turkish-capable voice.');
  const r = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voice}?output_format=mp3_44100_192`, {
    method: 'POST',
    headers: {'xi-api-key': process.env.ELEVENLABS_API_KEY, 'content-type': 'application/json'},
    body: JSON.stringify({
      text,
      model_id: process.env.ELEVENLABS_MODEL ?? 'eleven_multilingual_v2',
      language_code: 'tr',
      voice_settings: {stability: 0.55, similarity_boost: 0.8, style: 0.15, use_speaker_boost: true},
    }),
  });
  if (!r.ok) throw new Error(`ElevenLabs ${r.status}: ${await r.text()}`);
  return Buffer.from(await r.arrayBuffer());
};

const google = async (text) => {
  const r = await fetch(`https://texttospeech.googleapis.com/v1/text:synthesize?key=${process.env.GOOGLE_TTS_API_KEY}`, {
    method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify({
      input: {text},
      voice: {languageCode: 'tr-TR', name: process.env.GOOGLE_TTS_VOICE ?? 'tr-TR-Chirp3-HD-Charon'},
      audioConfig: {audioEncoding: 'MP3', sampleRateHertz: 44100},
    }),
  });
  if (!r.ok) throw new Error(`Google TTS ${r.status}: ${await r.text()}`);
  return Buffer.from((await r.json()).audioContent, 'base64');
};

const synth = process.env.ELEVENLABS_API_KEY ? eleven : process.env.GOOGLE_TTS_API_KEY ? google : null;
if (!synth) {
  console.error('No TTS provider configured. Set ELEVENLABS_API_KEY (+ ELEVENLABS_VOICE_ID) or GOOGLE_TTS_API_KEY.');
  process.exit(1);
}
for (const line of script.lines) {
  const file = join(outDir, `${line.id}.mp3`);
  writeFileSync(file, await synth(line.text));
  console.log('✓', line.id, line.text);
}
execFileSync('node', [join(root, 'scripts/build-timing.mjs'), ep], {stdio: 'inherit'});
