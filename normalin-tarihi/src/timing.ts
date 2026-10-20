/*
 * Narration-driven timeline. Scene lengths come from the narration audio
 * (measured by scripts/build-timing.mjs). When a line has no audio yet, its
 * length is estimated from the text so the edit stays usable and re-times
 * itself automatically once real voice-over files are added.
 */

export type ScriptLine = {
  id: string;
  /** exact narration text (sent to TTS) */
  text: string;
  /** subtitle text with " | " marking cue breaks; null hides the subtitle */
  subtitle: string | null;
};

export type MeasuredLine = {
  file: string | null;
  duration: number | null;
  /** start time (s, from the line start) of each whitespace-separated word, from TTS alignment */
  words?: number[] | null;
};

export type Block =
  | {scene: string; lines: string[]; lead?: number; tail?: number}
  | {scene: string; fixed: number};

export type TimedLine = ScriptLine & {start: number; end: number; file: string | null; estimated: boolean; wordStarts: number[] | null};
export type TimedScene = {scene: string; from: number; duration: number; lines: Record<string, TimedLine>};
export type Cue = {text: string; from: number; to: number; wordStarts?: number[]};

export type Timeline = {
  fps: number;
  totalFrames: number;
  scenes: TimedScene[];
  lines: TimedLine[];
  cues: Cue[];
  estimated: boolean;
};

/** Calm documentary Turkish ≈ 15.5 characters per second. */
export const estimateSeconds = (text: string) => 0.25 + text.replace(/\s+/g, ' ').length / 15.5;

const LINE_GAP = 0.35;

export const buildTimeline = (
  script: ScriptLine[],
  measured: Record<string, MeasuredLine>,
  blocks: Block[],
  fps: number,
): Timeline => {
  const byId = Object.fromEntries(script.map((l) => [l.id, l]));
  const toF = (s: number) => Math.round(s * fps);
  let cursor = 0;
  const scenes: TimedScene[] = [];
  const lines: TimedLine[] = [];
  for (const b of blocks) {
    if ('fixed' in b) {
      const d = toF(b.fixed);
      scenes.push({scene: b.scene, from: cursor, duration: d, lines: {}});
      cursor += d;
      continue;
    }
    const sceneFrom = cursor;
    let t = cursor + toF(b.lead ?? 0.5);
    const local: Record<string, TimedLine> = {};
    b.lines.forEach((id, i) => {
      const line = byId[id];
      if (!line) throw new Error(`Unknown script line ${id}`);
      const m = measured[id];
      const secs = m?.duration ?? estimateSeconds(line.text);
      const words = m?.words && m.words.length === line.text.split(/\s+/).filter(Boolean).length ? m.words : null;
      const tl: TimedLine = {
        ...line,
        start: t,
        end: t + toF(secs),
        file: m?.file ?? null,
        estimated: !m?.duration,
        wordStarts: words ? words.map((w) => t + w * fps) : null,
      };
      lines.push(tl);
      local[id] = {...tl, start: tl.start - sceneFrom, end: tl.end - sceneFrom};
      t = tl.end + (i < b.lines.length - 1 ? toF(LINE_GAP) : 0);
    });
    t += toF(b.tail ?? 0.5);
    scenes.push({scene: b.scene, from: sceneFrom, duration: t - sceneFrom, lines: local});
    cursor = t;
  }
  // subtitle cues: split each line at " | "; use measured word times when present
  const cues: Cue[] = [];
  for (const l of lines) {
    if (!l.subtitle) continue;
    const parts = l.subtitle.split('|').map((p) => p.trim());
    if (l.wordStarts) {
      let wi = 0;
      parts.forEach((p, i) => {
        const n = p.split(/\s+/).filter(Boolean).length;
        const ws = l.wordStarts!.slice(wi, wi + n);
        const next = i < parts.length - 1 ? l.wordStarts![wi + n] - 2 : l.end;
        cues.push({text: p, from: Math.round(ws[0]), to: Math.round(next), wordStarts: ws});
        wi += n;
      });
      continue;
    }
    const total = parts.reduce((a, p) => a + p.length, 0);
    let f = l.start;
    parts.forEach((p, i) => {
      const len = i === parts.length - 1 ? l.end - f : Math.round(((l.end - l.start) * p.length) / total);
      cues.push({text: p, from: f, to: f + len});
      f += len;
    });
  }
  return {fps, totalFrames: cursor, scenes, lines, cues, estimated: lines.some((l) => l.estimated)};
};

export const sceneOf = (tl: Timeline, scene: string) => {
  const s = tl.scenes.find((x) => x.scene === scene);
  if (!s) throw new Error(`Scene ${scene} missing from timeline`);
  return s;
};

/** Frame inside a line (0 = line start, 1 = line end), scene-relative. */
export const atLine = (s: TimedScene, id: string, fraction = 0) => {
  const l = s.lines[id];
  if (!l) throw new Error(`Line ${id} not in scene ${s.scene}`);
  return l.start + (l.end - l.start) * fraction;
};
