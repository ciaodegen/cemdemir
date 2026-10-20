import {EP01_TIMELINE as t} from '../src/episodes/ep01/Episode01';
console.log('total', t.totalFrames, (t.totalFrames / t.fps).toFixed(2) + 's', t.estimated ? '(estimated narration)' : '');
for (const s of t.scenes) console.log(s.scene.padEnd(12), s.from, '+', s.duration, Object.values(s.lines).map((l) => `${l.id}:${l.start}-${l.end}`).join(' '));
