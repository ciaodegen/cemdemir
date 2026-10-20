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

### Narration (required for the final render)
The script is in `src/episodes/ep01/script.json`. Use it exactly as written. The "Bu arada…" pause is built in through `ttsParts` and `pauses`.

1. Store **one** of these in the environment, never in code:
   - `ELEVENLABS_API_KEY` together with `ELEVENLABS_VOICE_ID`, a native Turkish voice. ElevenLabs also returns word timings, which the subtitles use.
   - `GOOGLE_TTS_API_KEY`. The default voice is `tr-TR-Chirp3-HD-Charon`.
2. Run `npm run tts 01`. It writes `public/audio/ep01/<line>.mp3` and `<line>.words.json`, then re-times the episode.
   A human recording also works: put `<line>.wav` files in that folder and run `npm run timing`.
3. Run `npm run render:ep01`. It refuses to render if any line has no audio, renders the video, then checks the MP4 for an audible narration track.

`npm run preview:ep01` renders a visual-only preview that uses estimated timing.

## Visual system (v3)
- Background `#FEF9EE` and emblem/text anthracite `#25221E`, both sampled from the official logo.
- The logo intro always plays on beige with an anthracite emblem. It never uses a dark background.
- Palette: sand `#D9C3A3`, camel `#B89470`, terracotta `#BC8066`, olive `#858B74`, taupe `#A69B8B`, outlines `#292724`. Tints are listed in `src/brand/theme.ts`.
- Illustrations use thin charcoal outlines with flat muted fills. Fills wash in after each outline is drawn.
- Typography uses **one family only, DM Sans**, with hierarchy from size and weight (`TYPE` in `theme.ts`).
  - Titles, labels, subtitles, the logo wordmark and the sign-off all use the same word-by-word reveal.
  - There are no underlines, rules or text boxes.

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
