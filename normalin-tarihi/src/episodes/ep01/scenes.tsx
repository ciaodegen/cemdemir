import React from 'react';
import {Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, FONT_FAMILY, LAYOUT, TYPE} from '../../brand/theme';
import {ArtSvg, Paper, cameraTransform} from '../../components/Canvas';
import {Ink, InkPath, Wash} from '../../components/Ink';
import {HandshakeMoment} from '../../components/HandshakeMoment';
import {Label, Title} from '../../components/Type';
import {SpecialEndingText} from '../../components/SpecialEnding';
import {dissolve} from '../../components/SceneFade';
import {atLine, TimedScene} from '../../timing';
import {CLASP_HANDS, ClaspSkin, ClaspSleeves, MeetSpark, SleeveStyle} from '../../illustrations/hands';
import {Figure, FigureSpec, Pt, REST_WRIST, SheathedSword, StoneMode, toLocal} from '../../illustrations/figures';
import {
  archGate,
  castle,
  cypress,
  groundMass,
  hillMasses,
  hourglass,
  naiskos,
  oliveBranch,
  palm,
  reliefSlab,
  shrub,
  skyline,
  templeFront,
  tower,
  wall,
  ziggurat,
} from '../../illustrations/architecture';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const soft = Easing.bezier(0.42, 0, 0.3, 1);

const useSec = () => {
  const {fps} = useVideoConfig();
  return (s: number) => s * fps;
};

const progress = (frame: number, from: number, to: number, easing = soft) =>
  interpolate(frame, [from, to], [0, 1], {...clamp, easing});

const lerpPt = (a: Pt, b: Pt, t: number): Pt => ({x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t});

const C = COLORS;
const STONE: StoneMode = {fill: '#E3D5BE', line: '#8E7B66'};

/* ------------------------------------------------------------------ */
/* Cast                                                                */
/* ------------------------------------------------------------------ */

const MESO_A: FigureSpec = {headwear: 'band', beard: 'long', hair: 'long', robe: 'mesopotamian', sleeve: 'short', cloth: C.terracotta, accent: C.sand, hat: C.camel};
const MESO_B: FigureSpec = {headwear: 'cap', beard: 'long', hair: 'long', robe: 'mesopotamian', sleeve: 'short', cloth: C.sand, accent: C.olive, hat: C.camel, skin: 'deep'};
const ASSYRIAN_KING: FigureSpec = {headwear: 'assyrian', beard: 'long', hair: 'long', robe: 'royal', sleeve: 'royal', cloth: C.terracotta, accent: C.sand, hat: C.sand};
const BABYLONIAN_KING: FigureSpec = {headwear: 'babylonian', beard: 'long', hair: 'long', robe: 'royal', sleeve: 'royal', cloth: C.sand, accent: C.terracotta, hat: C.camel, skin: 'deep'};
const GREEK_A: FigureSpec = {headwear: 'laurel', beard: 'short', hair: 'curly', robe: 'himation', sleeve: 'bare', cloth: C.linen, accent: C.sand};
const GREEK_B: FigureSpec = {headwear: 'none', beard: 'none', hair: 'curly', robe: 'greek', sleeve: 'bare', cloth: C.sandLight, accent: C.linen, skin: 'deep'};
const MEDIEVAL: FigureSpec = {headwear: 'none', beard: 'short', hair: 'short', robe: 'tunic', sleeve: 'long', cloth: C.olive, accent: C.terracotta, legs: C.taupe};
const MODERN: FigureSpec = {headwear: 'none', beard: 'none', hair: 'short', robe: 'suit', sleeve: 'suit', cloth: C.camel, accent: C.camel, legs: C.camel, skin: 'deep'};

/* ------------------------------------------------------------------ */
/* Shared backdrop pieces                                              */
/* ------------------------------------------------------------------ */

/** Horizon hills + ground plane fading in; ground ends above the subtitles. */
const Land: React.FC<{horizon: number; opacity: number; hills?: boolean; ground?: string}> = ({horizon, opacity, hills = true, ground = C.sandPale}) => (
  <g>
    {hills ? hillMasses(horizon).map((h, i) => <Wash key={i} d={h.d} fill={h.fill} opacity={opacity * 0.9} />) : null}
    <Wash d={groundMass(horizon, LAYOUT.artBottom)} fill={ground} opacity={opacity} />
  </g>
);

const Sun: React.FC<{x: number; y: number; r?: number; opacity: number}> = ({x, y, r = 46, opacity}) => (
  <circle cx={x} cy={y} r={r} fill={C.terracottaLight} opacity={opacity * 0.85} />
);

/* ------------------------------------------------------------------ */
/* Two figures that reach for each other and clasp hands               */
/* ------------------------------------------------------------------ */

type Pair = {
  a: FigureSpec;
  b: FigureSpec;
  ax: number;
  bx: number;
  ground: number;
  scale: number;
  meet: Pt;
  reachA: number;
  reachB: number;
  offerA?: number;
  clasp: number;
  drawA: number;
  drawB: number;
  shake?: number;
  extrasA?: InkPath[];
  stone?: StoneMode;
};

const HAND_CLASP_SCALE = 0.3; // matches the figures' hand scale

const FigurePair: React.FC<Pair> = (p) => {
  const figA = {x: p.ax, y: p.ground, scale: p.scale, facing: 1 as const};
  const figB = {x: p.bx, y: p.ground, scale: p.scale, facing: -1 as const};
  const cs = HAND_CLASP_SCALE * p.scale;
  const meet = {x: p.meet.x, y: p.meet.y + (p.shake ?? 0)};
  const aTarget = toLocal({x: meet.x - 150 * cs, y: meet.y + 8 * cs}, figA);
  const bTarget = toLocal({x: meet.x + 150 * cs, y: meet.y - 20 * cs}, figB);
  const aOffer = toLocal({x: meet.x - 150 * cs - 24 * p.scale, y: meet.y + 14 * p.scale}, figA);
  const aStop = lerpPt(aOffer, aTarget, p.offerA === undefined ? 1 : 1 - p.offerA);
  const aWrist = lerpPt(REST_WRIST, aStop, p.reachA);
  const bWrist = lerpPt(REST_WRIST, bTarget, p.reachB);
  const claspDraw = Math.min(p.drawA, p.drawB);
  return (
    <g>
      <Figure spec={p.a} {...figA} wrist={aWrist} draw={p.drawA} showHand={p.clasp < 0.5} extras={p.extrasA} stone={p.stone} />
      <Figure spec={p.b} {...figB} wrist={bWrist} draw={p.drawB} showHand={p.clasp < 0.5} stone={p.stone} />
      {p.clasp > 0 ? (
        <g transform={`translate(${meet.x} ${meet.y}) scale(${cs})`} opacity={p.clasp}>
          {p.stone ? (
            <path d="M -150 -30 C -100 -60 0 -90 54 -60 C 100 -64 150 -58 150 -58 L 150 18 C 80 40 0 80 -56 74 C -90 70 -150 46 -150 46 Z" fill={p.stone.fill} />
          ) : (
            <ClaspSkin opacity={claspDraw >= 1 ? 1 : 0} />
          )}
          <Ink paths={CLASP_HANDS} color={p.stone?.line} />
        </g>
      ) : null}
    </g>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 1 — Opening: hands meet, then the long walk of history        */
/* ------------------------------------------------------------------ */

export const HAND_Y = 1010;

const WALKERS: {spec: FigureSpec; x: number}[] = [
  {spec: MESO_A, x: 150},
  {spec: GREEK_A, x: 385},
  {spec: MEDIEVAL, x: 615},
  {spec: MODERN, x: 845},
];

/** Symbolic passage of time: people of different eras walking one path. */
const HistoryWalk: React.FC<{start: number; opacity: number}> = ({start, opacity}) => {
  const frame = useCurrentFrame();
  const sec = useSec();
  const t = frame - start;
  const land = progress(frame, start, start + sec(0.8));
  const arrow = progress(frame, start + sec(0.2), start + sec(2.2));
  const ground = 1236;
  return (
    <g opacity={opacity}>
      <Sun x={830} y={560} opacity={land} />
      <Land horizon={820} opacity={land} />
      <Ink paths={[...cypress(70, 840, 220), ...cypress(1010, 835, 180)]} draw={land} />
      {WALKERS.map((w, i) => {
        const appear = progress(frame, start + sec(0.15 + i * 0.28), start + sec(0.9 + i * 0.28));
        const phase = (t / 30) * Math.PI * 2 * 0.85 + i * 0.9;
        const step = Math.sin(phase);
        const drift = t * 0.45;
        const legged = w.spec.robe === 'tunic' || w.spec.robe === 'suit';
        return (
          <g key={i} transform={`translate(${drift} ${-Math.abs(Math.cos(phase)) * 4})`} opacity={appear}>
            <Figure
              spec={w.spec}
              x={w.x}
              y={ground}
              scale={0.86}
              swing={legged ? step * 17 : 0}
              wrist={{x: REST_WRIST.x - step * (legged ? 34 : 18), y: REST_WRIST.y - Math.abs(step) * 6}}
            />
          </g>
        );
      })}
      <Ink paths={['M 110 1262 L 960 1262', 'M 936 1248 L 962 1262 L 936 1276']} draw={arrow} overlap={0.1} />
    </g>
  );
};

export const OpeningScene: React.FC<{s: TimedScene; questionLines: string[]}> = ({s, questionLines}) => {
  const frame = useCurrentFrame();
  const q1 = atLine(s, 'q1');
  const meet = Math.round(atLine(s, 'q2', 0.12));
  const toWalk = Math.round(atLine(s, 'q2', 0.42));
  const walkIn = dissolve(frame, toWalk, 16);
  return (
    <Paper>
      <div style={{opacity: 1 - walkIn}}>
        <Title lines={questionLines} from={Math.max(0, q1 - 4)} to={atLine(s, 'q1', 0.7)} top={LAYOUT.titleY + 10} />
      </div>
      <ArtSvg>
        <g opacity={1 - walkIn}>
          <HandshakeMoment cy={HAND_Y + 60} enter={2} meet={meet} />
        </g>
        {walkIn > 0 ? <HistoryWalk start={toWalk} opacity={walkIn} /> : null}
      </ArtSvg>
    </Paper>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 3 — Ancient Mesopotamia                                       */
/* ------------------------------------------------------------------ */

const MESO_CITY: {back: InkPath[]; walls: InkPath[]; trees: InkPath[]} = (() => {
  const g = 930;
  return {
    back: ziggurat(540, 820, 430, 62, 3),
    walls: [...wall(150, 930, g, 110, 18), ...tower(200, g, 86, 160), ...tower(400, g, 74, 140), ...tower(680, g, 74, 140), ...tower(880, g, 86, 160), archGate(540, g, 70, 96)],
    trees: [...palm(96, 1010, 290, 16), ...palm(990, 990, 250, -14), shrub(260, 1000, 30), shrub(830, 995, 26)],
  };
})();

export const MesopotamiaScene: React.FC<{s: TimedScene}> = ({s}) => {
  const frame = useCurrentFrame();
  const sec = useSec();
  const land = progress(frame, 0, sec(0.9));
  const walkStart = atLine(s, 'm2', 0.0);
  const arrive = atLine(s, 'm2', 0.55);
  const walk = progress(frame, walkStart, arrive, Easing.bezier(0.3, 0, 0.3, 1));
  const meetAt = atLine(s, 'm2', 0.7);
  const reach = progress(frame, arrive, meetAt);
  const clasp = dissolve(frame, meetAt - 2, 5);
  const bob = (1 - walk) * walk * 4 * Math.abs(Math.sin(frame / 7)) * 5;
  const figDraw = progress(frame, sec(1.6), sec(2.8));
  return (
    <Paper>
      <Label text="*Mezopotamya*" />
      <ArtSvg>
        <Sun x={830} y={560} opacity={land} />
        <Land horizon={930} opacity={land} />
        <Ink paths={MESO_CITY.back} draw={progress(frame, sec(0.1), sec(1.6))} overlap={0.4} />
        <Ink paths={MESO_CITY.walls} draw={progress(frame, sec(0.5), sec(2.2))} overlap={0.5} />
        <Ink paths={MESO_CITY.trees} draw={progress(frame, sec(1.0), sec(2.4))} overlap={0.4} />
        <g transform={`translate(0 ${-bob})`}>
          <FigurePair
            a={MESO_A}
            b={MESO_B}
            ax={interpolate(walk, [0, 1], [250, 360])}
            bx={interpolate(walk, [0, 1], [830, 720])}
            ground={1300}
            scale={0.92}
            meet={{x: 540, y: 1010}}
            reachA={reach}
            reachB={reach}
            clasp={clasp}
            drawA={figDraw}
            drawB={figDraw}
          />
        </g>
      </ArtSvg>
    </Paper>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 4 — The empty-hand theory                                     */
/* ------------------------------------------------------------------ */

const THEORY_BACK: InkPath[] = [
  ...cypress(160, 930, 230),
  ...cypress(205, 930, 170),
  ...cypress(930, 925, 210),
];

export const TheoryScene: React.FC<{s: TimedScene}> = ({s}) => {
  const frame = useCurrentFrame();
  const sec = useSec();
  const offerStart = atLine(s, 't1', 0.3);
  const offerEnd = atLine(s, 't1', 0.72);
  const answerStart = atLine(s, 't2', 0.0);
  const meetAt = atLine(s, 't2', 0.32);
  const reachA = progress(frame, offerStart, offerEnd);
  const reachB = progress(frame, answerStart, meetAt);
  const offerA = 1 - progress(frame, answerStart + sec(0.4), meetAt);
  const clasp = dissolve(frame, meetAt - 2, 5);
  const t = frame - meetAt;
  const shake = t > 0 && t < 30 ? Math.sin((t / 15) * Math.PI * 2) * 6 * (1 - t / 34) : 0;
  const land = progress(frame, 0, sec(0.9));
  // B turns towards A (small step in) when answering
  const step = progress(frame, answerStart - sec(0.3), answerStart + sec(0.5));
  return (
    <Paper>
      <Label text="Yaygın bir *teori*" />
      <ArtSvg>
        <Land horizon={930} opacity={land} />
        <Ink paths={THEORY_BACK} draw={progress(frame, sec(0.2), sec(1.6))} overlap={0.4} />
        <FigurePair
          a={MESO_A}
          b={MESO_B}
          ax={290}
          bx={interpolate(step, [0, 1], [820, 790])}
          ground={1312}
          scale={1.24}
          meet={{x: 548, y: 905}}
          reachA={reachA}
          reachB={reachB}
          offerA={offerA}
          clasp={clasp}
          drawA={progress(frame, sec(0.05), sec(1.6))}
          drawB={progress(frame, sec(0.35), sec(1.9))}
          shake={shake}
          extrasA={SheathedSword}
        />
      </ArtSvg>
    </Paper>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 5 — Ancient alliance: the relief, then the clasp up close     */
/* ------------------------------------------------------------------ */

const SLAB = reliefSlab(70, 470, 940, 840);

export const AllianceScene: React.FC<{s: TimedScene}> = ({s}) => {
  const frame = useCurrentFrame();
  const sec = useSec();
  const slab = progress(frame, 0, sec(1.4));
  const carve = progress(frame, sec(0.6), sec(2.4));
  const closeAt = atLine(s, 'a1', 0.86);
  const close = dissolve(frame, closeAt, 16);
  const zoom = progress(frame, closeAt, s.duration, Easing.bezier(0.3, 0, 0.3, 1));
  const ct = frame - (closeAt + 20);
  const shake = ct > 0 && ct < 34 ? Math.sin((ct / 17) * Math.PI * 2) * 8 * (1 - ct / 40) : 0;
  return (
    <Paper>
      <Label text="*MÖ 9. yüzyıl* · kabartma" to={closeAt + 8} />
      <Label text="Bir *ittifak*" from={closeAt + 10} />
      <ArtSvg>
        <g opacity={1 - close}>
          <Ink paths={SLAB} draw={slab} overlap={0.4} />
          <FigurePair
            a={ASSYRIAN_KING}
            b={BABYLONIAN_KING}
            ax={420}
            bx={760}
            ground={1250}
            scale={0.98}
            meet={{x: 590, y: 945}}
            reachA={1}
            reachB={1}
            clasp={carve >= 1 ? 1 : 0}
            drawA={carve}
            drawB={carve}
            stone={STONE}
          />
        </g>
        {close > 0 ? (
          <g opacity={close}>
            <Sun x={540} y={640} r={60} opacity={1} />
            <Land horizon={930} opacity={1} />
            <Ink paths={[...cypress(170, 935, 220), ...cypress(900, 930, 190)]} />
            <g transform={`translate(540 ${960 + shake}) scale(${1.55 + zoom * 0.12})`}>
              <ClaspSleeves a="royal" b="royalSand" />
              <ClaspSkin />
              <Ink paths={CLASP_HANDS} />
              <MeetSpark draw={progress(frame, closeAt + 22, closeAt + 34)} opacity={1 - progress(frame, closeAt + 60, closeAt + 74)} />
            </g>
          </g>
        ) : null}
      </ArtSvg>
    </Paper>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 6 — Ancient Greece → funerary stele                           */
/* ------------------------------------------------------------------ */

const GREEK_SET: InkPath[] = [...templeFront(250, 930, 330, 290, 5), ...cypress(880, 935, 300), ...cypress(950, 935, 220), shrub(620, 935, 30)];
const STELE = naiskos(540, 1250, 600, 690);
const OLIVE = [...oliveBranch(900, 1262, 230, -72), ...oliveBranch(170, 1262, 190, -112)];

export const GreeceScene: React.FC<{s: TimedScene}> = ({s}) => {
  const frame = useCurrentFrame();
  const sec = useSec();
  const reachStart = atLine(s, 'g1', 0.12);
  const meetAt = atLine(s, 'g1', 0.42);
  const reach = progress(frame, reachStart, meetAt);
  const clasp = dissolve(frame, meetAt - 2, 5);
  const switchAt = atLine(s, 'g2', 0) - sec(0.25);
  const toStele = dissolve(frame, switchAt, 14);
  const steleDraw = progress(frame, switchAt, switchAt + sec(1.6));
  const steleFigures = progress(frame, switchAt + sec(0.4), switchAt + sec(2.0));
  const land = progress(frame, 0, sec(0.9));
  return (
    <Paper>
      <Label text="*Antik Yunan*" to={switchAt + 10} />
      <Label text="*Mezar* steli" from={switchAt + 8} />
      <ArtSvg>
        <g opacity={1 - toStele}>
          <Sun x={560} y={590} opacity={land} />
          <Land horizon={930} opacity={land} />
          <Ink paths={GREEK_SET} draw={progress(frame, sec(0.1), sec(1.6))} overlap={0.4} />
          <FigurePair
            a={GREEK_A}
            b={GREEK_B}
            ax={300}
            bx={780}
            ground={1312}
            scale={1.22}
            meet={{x: 540, y: 905}}
            reachA={reach}
            reachB={reach}
            clasp={clasp}
            drawA={progress(frame, sec(0.1), sec(1.7))}
            drawB={progress(frame, sec(0.3), sec(1.9))}
          />
        </g>
        {toStele > 0 ? (
          <g opacity={toStele}>
            <Wash d={groundMass(1250, LAYOUT.artBottom)} fill={C.sandPale} opacity={1} />
            <Ink paths={STELE} draw={steleDraw} overlap={0.4} />
            <Ink paths={OLIVE} draw={progress(frame, switchAt + sec(1.0), switchAt + sec(2.4))} overlap={0.3} />
            <FigurePair
              a={GREEK_A}
              b={GREEK_B}
              ax={430}
              bx={650}
              ground={1216}
              scale={0.78}
              meet={{x: 540, y: 945}}
              reachA={1}
              reachB={1}
              clasp={steleFigures >= 1 ? 1 : 0}
              drawA={steleFigures}
              drawB={steleFigures}
              stone={STONE}
            />
          </g>
        ) : null}
      </ArtSvg>
    </Paper>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 7 — Passage of time: hourglass, then one gesture across eras  */
/* ------------------------------------------------------------------ */

const ERAS: {a: SleeveStyle; b: SleeveStyle; label: string; back: InkPath[]}[] = [
  {a: 'mesopotamian', b: 'royalSand', label: 'Mezopotamya', back: ziggurat(540, 800, 360, 56, 3)},
  {a: 'greek', b: 'greek', label: 'Antik Yunan', back: templeFront(540, 800, 330, 250, 5)},
  {a: 'medievalMail', b: 'medieval', label: 'Orta Çağ', back: castle(540, 800, 0.78)},
  {a: 'modern', b: 'modernOlive', label: 'Bugün', back: skyline(800, 250, 830, 0.55)},
];

export const TimeScene: React.FC<{s: TimedScene}> = ({s}) => {
  const frame = useCurrentFrame();
  const sec = useSec();
  const sandEnd = atLine(s, 'p1', 0.5);
  const sandT = progress(frame, sec(0.3), sandEnd, Easing.linear);
  const glass = hourglass(540, 880, sandT, 1.3);
  const toEras = dissolve(frame, sandEnd, 14);
  const start = sandEnd + 6;
  const span = (s.duration - start - sec(0.4)) / ERAS.length;
  const eraFloat = (frame - start) / span;
  const active = Math.max(0, Math.min(ERAS.length - 1, Math.floor(eraFloat)));
  const x0 = 210;
  const x1 = 870;
  const dotX = (i: number) => x0 + ((x1 - x0) * i) / (ERAS.length - 1);
  const eraOpacity = (i: number) => {
    const at = start + span * i;
    const o = i === 0 ? 1 : dissolve(frame, at - 5, 10);
    const out = i === ERAS.length - 1 ? 0 : dissolve(frame, start + span * (i + 1) - 5, 10);
    return Math.max(0, o - out);
  };
  const breathe = Math.sin(frame / 22) * 3;
  return (
    <Paper>
      <ArtSvg>
        <g opacity={1 - toEras}>
          <Land horizon={1180} opacity={progress(frame, 0, sec(0.6))} hills={false} />
          <Ink paths={glass.frame} draw={progress(frame, 0, sec(0.9))} overlap={0.3} />
          {glass.sand.map((d, i) => (
            <path key={i} d={d} fill={C.sand} opacity={progress(frame, sec(0.5), sec(0.9))} />
          ))}
          {glass.stream ? <path d={glass.stream} stroke={C.camel} strokeWidth={3} /> : null}
        </g>
        {toEras > 0 ? (
          <g opacity={toEras}>
            <Wash d={groundMass(800, 1110)} fill={C.sandPale} opacity={1} />
            {ERAS.map((e, i) => {
              const o = eraOpacity(i);
              return o > 0 ? (
                <g key={e.label} opacity={o}>
                  <Ink paths={e.back} />
                </g>
              ) : null;
            })}
            <g transform={`translate(540 ${1000 + breathe}) scale(1.35)`}>
              {ERAS.map((e, i) => {
                const o = eraOpacity(i);
                return o > 0 ? <ClaspSleeves key={e.label} a={e.a} b={e.b} opacity={o} /> : null;
              })}
              <ClaspSkin />
              <Ink paths={CLASP_HANDS} />
            </g>
            {ERAS.map((e, i) => (
              <circle key={e.label} cx={dotX(i)} cy={1196} r={i === active ? 11 : 8} fill={i <= active ? C.terracotta : C.sandLight} />
            ))}
          </g>
        ) : null}
      </ArtSvg>
      {toEras > 0
        ? ERAS.map((e, i) => (
            <div
              key={e.label}
              lang="tr"
              style={{
                position: 'absolute',
                top: 1222,
                left: dotX(i) - 120,
                width: 240,
                textAlign: 'center',
                fontFamily: FONT_FAMILY,
                ...TYPE.small,
                color: C.text,
                opacity: toEras * progress(frame, start + span * i - 8, start + span * i + 6) * (i === active ? 1 : 0.55),
              }}
            >
              {e.label}
            </div>
          ))
        : null}
    </Paper>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 8 — Modern conclusion                                         */
/* ------------------------------------------------------------------ */

const CITY: InkPath[] = [...skyline(900, 60, 1020, 0.62), ...cypress(130, 905, 160), ...cypress(960, 905, 140), shrub(300, 905, 26), shrub(780, 905, 22)];

export const ModernScene: React.FC<{s: TimedScene}> = ({s}) => {
  const frame = useCurrentFrame();
  const sec = useSec();
  const back = progress(frame, 0, sec(1.4)) * (1 - progress(frame, s.duration - sec(0.6), s.duration));
  return (
    <Paper>
      <ArtSvg>
        <g opacity={back}>
          <Wash d={groundMass(900, LAYOUT.artBottom)} fill={C.sandPale} opacity={1} />
          <Ink paths={CITY} draw={progress(frame, 0, sec(1.6))} overlap={0.3} />
        </g>
        <HandshakeMoment cy={HAND_Y} enter={2} meet={Math.round(atLine(s, 'c1', 0.48))} spark={false} />
      </ArtSvg>
      <div style={{opacity: 1 - progress(frame, s.duration - sec(0.6), s.duration)}}>
        <Label text="*Bugün*" />
      </div>
    </Paper>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 9 — Special first-episode ending                              */
/* ------------------------------------------------------------------ */

export const ENDING_TAIL_SECONDS = 6.4;

export const EndingScene: React.FC<{s: TimedScene; text: string}> = ({s, text}) => {
  const sec = useSec();
  const release = Math.round(atLine(s, 'e1', 0) + sec(0.15));
  const lineEnd = atLine(s, 'e1', 1);
  const enter = Math.round(lineEnd + sec(0.6));
  const meet = Math.round(enter + sec(2.0));
  return (
    <Paper>
      <ArtSvg>
        {/* the conclusion's handshake lets go… */}
        <HandshakeMoment cy={HAND_Y} enter={-90} meet={-60} release={release} spark={false} />
        {/* …and the brand greets the viewer */}
        <HandshakeMoment cy={HAND_Y - 40} enter={enter} meet={meet} />
      </ArtSvg>
      <SpecialEndingText text={text} at={meet - 4} y={1150} />
    </Paper>
  );
};
