# Normalin Tarihi — Reels production system

Remotion + React + TypeScript + SVG. 1080×1920, 30 fps, H.264.

## Episode 01 — "Neden tokalaşıyoruz?"

```bash
npm install
export REMOTION_BROWSER=/path/to/chrome-headless-shell   # optional, otherwise Remotion downloads one
npm run render:ep01      # → out/normalin-tarihi-ep01.mp4
npm run cover:ep01       # → out/normalin-tarihi-ep01-cover.png
npm run studio           # preview / scrub in the browser
```

### Narration (not yet recorded)
The script lives in `src/episodes/ep01/script.json`. You need one audio file per line in
`public/audio/ep01/<lineId>.(wav|mp3|m4a)`, for example `q1.mp3`, `q2.mp3` and so on through `e1.mp3`.

- **TTS:** run `ELEVENLABS_API_KEY=… ELEVENLABS_VOICE_ID=… npm run tts 01` or `GOOGLE_TTS_API_KEY=… npm run tts 01`.
- **Recorded voice:** put the files in that folder and run `npm run timing`.

`scripts/build-timing.mjs` measures the files. Scenes, animation beats and subtitles then re-time themselves to the real audio.
Lines that have no audio are timed from an estimate of 15.5 characters per second.

## Layout
| Path | Purpose |
|---|---|
| `src/brand/` | theme (colours, safe areas), the logo traced 1:1 from the master file (`logoGeometry.ts`), `LogoIntro` signature transition |
| `src/components/` | `Ink` draw-on line primitive, `OpeningQuestion`, `HandshakeMoment`, `SceneFade`/`dissolve`, `SceneLabel`, `Subtitles`, `SpecialEndingText`, `Cover`, `FontGate` |
| `src/illustrations/` | hands and sleeves for each era, parametric IK-driven historical `Figure`, architecture helpers |
| `src/timing.ts` | narration-driven timeline (scenes, lines, subtitle cues) |
| `src/episodes/ep01/` | script, scene compositions, episode assembly |
| `scripts/` | timing, TTS, QA stills, logo re-trace |

## A new episode
Copy `src/episodes/ep01`, then change `script.json`, the `BLOCKS` list and the scene illustrations.
Register the episode in `src/Root.tsx`. Brand, logo intro, subtitles and cover stay as they are.
The special greeting ending is used only in Ep01.
