import React from 'react';
import {Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS} from '../../brand/theme';
import {ArtSvg, Paper, cameraTransform} from '../../components/Canvas';
import {Ink} from '../../components/Ink';
import {HandshakeMoment} from '../../components/HandshakeMoment';
import {OpeningQuestion} from '../../components/OpeningQuestion';
import {SceneLabel} from '../../components/SceneLabel';
import {SpecialEndingText} from '../../components/SpecialEnding';
import {dissolve} from '../../components/SceneFade';
import {atLine, TimedScene} from '../../timing';
import {CLASP_HANDS, ClaspSleeves, SleeveStyle} from '../../illustrations/hands';
import {Figure, FigureSpec, Pt, REST_WRIST, toLocal} from '../../illustrations/figures';
import {
  archGate,
  cypress,
  hills,
  ionicColumn,
  naiskos,
  oliveBranch,
  palm,
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

/* ------------------------------------------------------------------ */
/* Costumes                                                            */
/* ------------------------------------------------------------------ */

const MESO_A: FigureSpec = {headwear: 'band', beard: 'long', hair: 'long', robe: 'mesopotamian', sleeve: 'short'};
const MESO_B: FigureSpec = {headwear: 'cap', beard: 'long', hair: 'long', robe: 'mesopotamian', sleeve: 'short'};
const ASSYRIAN_KING: FigureSpec = {headwear: 'assyrian', beard: 'long', hair: 'long', robe: 'royal', sleeve: 'royal'};
const BABYLONIAN_KING: FigureSpec = {headwear: 'babylonian', beard: 'long', hair: 'long', robe: 'royal', sleeve: 'royal'};
const GREEK_A: FigureSpec = {headwear: 'laurel', beard: 'short', hair: 'curly', robe: 'himation', sleeve: 'bare'};
const GREEK_B: FigureSpec = {headwear: 'laurel', beard: 'none', hair: 'curly', robe: 'greek', sleeve: 'bare'};

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
  /** 0 → rest, 1 → at the clasp, per figure */
  reachA: number;
  reachB: number;
  /** A's open-hand "offer" position used before B answers (0..1 blend) */
  offerA?: number;
  clasp: number;
  drawA: number;
  drawB: number;
  shake?: number;
  extrasA?: string[];
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
  return (
    <g>
      <Figure spec={p.a} {...figA} wrist={aWrist} draw={p.drawA} showHand={p.clasp < 0.5} extras={p.extrasA} />
      <Figure spec={p.b} {...figB} wrist={bWrist} draw={p.drawB} showHand={p.clasp < 0.5} />
      {p.clasp > 0 ? (
        <g transform={`translate(${meet.x} ${meet.y}) scale(${cs})`} opacity={p.clasp}>
          <path
            d="M -150 -30 C -100 -60 0 -90 54 -60 C 100 -64 150 -58 150 -58 L 150 18 C 80 40 0 80 -56 74 C -90 70 -150 46 -150 46 Z"
            fill={COLORS.paper}
          />
          <Ink paths={CLASP_HANDS} />
        </g>
      ) : null}
    </g>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 1 — Opening                                                   */
/* ------------------------------------------------------------------ */

export const HAND_Y = 940;

export const OpeningScene: React.FC<{s: TimedScene; question: string}> = ({s, question}) => {
  return (
    <Paper>
      <OpeningQuestion text={question} from={Math.max(0, atLine(s, 'q1') - 6)} />
      <ArtSvg>
        <HandshakeMoment cy={HAND_Y} enter={4} meet={Math.round(atLine(s, 'q2', 0.42))} />
      </ArtSvg>
    </Paper>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 3 — Ancient Mesopotamia                                       */
/* ------------------------------------------------------------------ */

const MESO_CITY = (() => {
  const g = 870;
  const back = [...ziggurat(540, 770, 400, 56, 3)];
  const walls = [
    ...wall(120, 960, g, 100, 16),
    ...tower(190, g, 80, 150),
    ...tower(410, g, 70, 130),
    ...tower(670, g, 70, 130),
    ...tower(890, g, 80, 150),
    archGate(540, g, 64, 92),
    `M 120 ${g} L 960 ${g}`,
  ];
  const land = [
    ...hills(690, -20, 1100),
    ...palm(110, 960, 210, 14),
    ...palm(980, 940, 180, -12),
    ...palm(300, 990, 130, 8),
    'M 60 960 C 300 950 780 950 1020 960',
  ];
  const road = ['M 520 870 C 500 930 430 980 420 1050 C 412 1110 470 1160 450 1240', 'M 560 870 C 560 940 520 990 520 1060 C 520 1120 590 1170 600 1240'];
  return {back, walls, land, road};
})();

export const MesopotamiaScene: React.FC<{s: TimedScene}> = ({s}) => {
  const frame = useCurrentFrame();
  const sec = useSec();
  const cam = interpolate(frame, [0, s.duration], [1, 1.04], clamp);
  const figDraw = progress(frame, atLine(s, 'm2', 0.05), atLine(s, 'm2', 0.05) + sec(1.8));
  const sun = progress(frame, sec(1.0), sec(1.8));
  return (
    <Paper>
      <SceneLabel text="MEZOPOTAMYA" />
      <ArtSvg>
        <g transform={cameraTransform(cam, 540, 900)}>
          <circle cx={830} cy={520} r={30} fill={COLORS.accent} opacity={sun * 0.75} />
          <Ink paths={MESO_CITY.back} draw={progress(frame, sec(0.1), sec(1.7))} overlap={0.4} />
          <Ink paths={MESO_CITY.walls} draw={progress(frame, sec(0.6), sec(2.6))} overlap={0.5} />
          <Ink paths={MESO_CITY.land} draw={progress(frame, sec(1.1), sec(2.9))} overlap={0.5} />
          <Ink paths={MESO_CITY.road} draw={progress(frame, sec(2.0), sec(3.2))} overlap={0.3} />
          <Figure spec={MESO_A} x={330} y={1300} scale={0.5} draw={figDraw} />
          <Figure spec={MESO_B} x={740} y={1300} scale={0.5} facing={-1} draw={progress(frame, atLine(s, 'm2', 0.15), atLine(s, 'm2', 0.15) + sec(1.8))} />
        </g>
      </ArtSvg>
    </Paper>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 4 — The empty-hand theory                                     */
/* ------------------------------------------------------------------ */

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
  const shake = t > 0 && t < 30 ? Math.sin((t / 15) * Math.PI * 2) * 5 * (1 - t / 34) : 0;
  return (
    <Paper>
      <SceneLabel text="YAYGIN BİR TEORİ" />
      <ArtSvg>
        <line x1={110} y1={1302} x2={970} y2={1302} stroke={COLORS.ink} strokeWidth={2.6} strokeLinecap="round" opacity={progress(frame, 0, sec(0.8))} />
        <FigurePair
          a={MESO_A}
          b={MESO_B}
          ax={320}
          bx={760}
          ground={1300}
          scale={1.12}
          meet={{x: 540, y: 880}}
          reachA={reachA}
          reachB={reachB}
          offerA={offerA}
          clasp={clasp}
          drawA={progress(frame, sec(0.05), sec(1.6))}
          drawB={progress(frame, sec(0.35), sec(1.9))}
          shake={shake}
        />
      </ArtSvg>
    </Paper>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 5 — Ancient alliance (9th c. BCE relief)                      */
/* ------------------------------------------------------------------ */

const RELIEF_FRAME = (() => {
  const rosettes: string[] = [];
  for (let x = 150; x <= 930; x += 65) {
    rosettes.push(`M ${x - 9} 486 A 9 9 0 1 0 ${x + 9} 486 A 9 9 0 1 0 ${x - 9} 486 M ${x - 2} 486 A 2 2 0 1 0 ${x + 2} 486 A 2 2 0 1 0 ${x - 2} 486`);
  }
  return [
    'M 100 460 L 980 460',
    'M 100 512 L 980 512',
    rosettes.join(' '),
    'M 100 1302 L 980 1302',
    'M 100 1322 L 980 1322',
  ];
})();

export const AllianceScene: React.FC<{s: TimedScene}> = ({s}) => {
  const frame = useCurrentFrame();
  const sec = useSec();
  const reachStart = atLine(s, 'a1', 0.28);
  const meetAt = atLine(s, 'a1', 0.56);
  const reach = progress(frame, reachStart, meetAt);
  const clasp = dissolve(frame, meetAt - 2, 5);
  const zoomStart = atLine(s, 'a1', 0.8);
  const zoomEnd = atLine(s, 'a2', 0.9);
  const z = progress(frame, zoomStart, zoomEnd, Easing.bezier(0.45, 0, 0.2, 1));
  const meet = {x: 540, y: 870};
  const cam = 1 + z * 0.75;
  const focus = lerpPt({x: 540, y: 900}, meet, z);
  return (
    <Paper>
      <SceneLabel text="MÖ 9. YÜZYIL · KABARTMA" to={zoomStart + sec(0.6)} />
      <ArtSvg>
        {/* keep the close-up clear of the subtitle zone */}
        <clipPath id="alliance-clip">
          <rect x={0} y={0} width={1080} height={interpolate(z, [0, 1], [1920, 1350])} />
        </clipPath>
        <g clipPath="url(#alliance-clip)">
        <g transform={cameraTransform(cam, focus.x, focus.y, 540, 900)}>
          <Ink paths={RELIEF_FRAME} draw={progress(frame, 0, sec(1.3))} overlap={0.5} />
          <FigurePair
            a={ASSYRIAN_KING}
            b={BABYLONIAN_KING}
            ax={315}
            bx={765}
            ground={1300}
            scale={1.14}
            meet={meet}
            reachA={reach}
            reachB={reach}
            clasp={clasp}
            drawA={progress(frame, sec(0.2), sec(1.9))}
            drawB={progress(frame, sec(0.45), sec(2.1))}
          />
        </g>
        </g>
      </ArtSvg>
    </Paper>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 6 — Ancient Greece → funerary stele                           */
/* ------------------------------------------------------------------ */

const GREEK_SET = [
  ...ionicColumn(960, 1300, 780, 50),
  ...cypress(120, 1290, 470),
  'M 70 1302 L 1010 1302',
];

const STELE = naiskos(540, 1270, 560, 640);
const OLIVE = oliveBranch(870, 1262, 200, -72);

export const GreeceScene: React.FC<{s: TimedScene}> = ({s}) => {
  const frame = useCurrentFrame();
  const sec = useSec();
  const reachStart = atLine(s, 'g1', 0.12);
  const meetAt = atLine(s, 'g1', 0.42);
  const reach = progress(frame, reachStart, meetAt);
  const clasp = dissolve(frame, meetAt - 2, 5);
  const switchAt = atLine(s, 'g2', 0) - sec(0.25);
  const toStele = dissolve(frame, switchAt, 12);
  const steleDraw = progress(frame, switchAt, switchAt + sec(2.0));
  const steleFigures = progress(frame, switchAt + sec(0.5), switchAt + sec(2.3));
  return (
    <Paper>
      <SceneLabel text="ANTİK YUNAN" to={switchAt + 10} />
      <SceneLabel text="MEZAR STELİ" from={switchAt + 6} />
      <ArtSvg>
        <g opacity={1 - toStele}>
          <Ink paths={GREEK_SET} draw={progress(frame, 0, sec(1.6))} overlap={0.4} />
          <FigurePair
            a={GREEK_A}
            b={GREEK_B}
            ax={320}
            bx={740}
            ground={1300}
            scale={1.12}
            meet={{x: 530, y: 885}}
            reachA={reach}
            reachB={reach}
            clasp={clasp}
            drawA={progress(frame, sec(0.1), sec(1.7))}
            drawB={progress(frame, sec(0.3), sec(1.9))}
          />
        </g>
        {toStele > 0 ? (
          <g opacity={toStele}>
            <Ink paths={STELE} draw={steleDraw} overlap={0.4} />
            <Ink paths={OLIVE} draw={progress(frame, switchAt + sec(1.2), switchAt + sec(2.6))} overlap={0.3} />
            <FigurePair
              a={GREEK_A}
              b={GREEK_B}
              ax={432}
              bx={648}
              ground={1238}
              scale={0.74}
              meet={{x: 540, y: 965}}
              reachA={1}
              reachB={1}
              clasp={steleFigures >= 1 ? 1 : 0}
              drawA={steleFigures}
              drawB={steleFigures}
            />
          </g>
        ) : null}
      </ArtSvg>
    </Paper>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 7 — Passage of time                                           */
/* ------------------------------------------------------------------ */

const ERAS: {sleeve: SleeveStyle; label: string}[] = [
  {sleeve: 'mesopotamian', label: 'MEZOPOTAMYA'},
  {sleeve: 'greek', label: 'ANTİK YUNAN'},
  {sleeve: 'medieval', label: 'ORTA ÇAĞ'},
  {sleeve: 'modern', label: 'BUGÜN'},
];

export const TimeScene: React.FC<{s: TimedScene}> = ({s}) => {
  const frame = useCurrentFrame();
  const sec = useSec();
  const start = sec(0.1);
  const span = (s.duration - start - sec(0.5)) / ERAS.length;
  const eraFloat = (frame - start) / span;
  const active = Math.max(0, Math.min(ERAS.length - 1, Math.floor(eraFloat)));
  const scale = 1.3;
  const cy = HAND_Y;
  const x0 = 210;
  const x1 = 870;
  const dotX = (i: number) => x0 + ((x1 - x0) * i) / (ERAS.length - 1);
  const lineTo = interpolate(eraFloat, [0, ERAS.length - 1], [x0, x1], clamp);
  return (
    <Paper>
      <ArtSvg>
        <g transform={`translate(540 ${cy}) scale(${scale})`}>
          {ERAS.map((e, i) => {
            const at = start + span * i;
            const o = i === 0 ? dissolve(frame, 0, 8) : dissolve(frame, at - 4, 9);
            const out = i === ERAS.length - 1 ? 0 : dissolve(frame, start + span * (i + 1) - 4, 9);
            const op = Math.max(0, o - out);
            return op > 0 ? <ClaspSleeves key={e.sleeve} a={e.sleeve} b={e.sleeve} opacity={op} /> : null;
          })}
          <path
            d="M -150 -30 C -100 -60 0 -90 54 -60 C 100 -64 150 -58 150 -58 L 150 18 C 80 40 0 80 -56 74 C -90 70 -150 46 -150 46 Z"
            fill={COLORS.paper}
          />
          <Ink paths={CLASP_HANDS} />
        </g>
        {/* timeline */}
        <g opacity={dissolve(frame, 2, 10)}>
          <line x1={x0} y1={1210} x2={x1} y2={1210} stroke={COLORS.accent} strokeWidth={2} />
          <line x1={x0} y1={1210} x2={lineTo} y2={1210} stroke={COLORS.ink} strokeWidth={2.6} />
          {ERAS.map((e, i) => (
            <circle
              key={e.label}
              cx={dotX(i)}
              cy={1210}
              r={i <= active ? 8 : 6.5}
              fill={i <= active ? COLORS.ink : COLORS.paper}
              stroke={i <= active ? COLORS.ink : COLORS.accent}
              strokeWidth={2.4}
            />
          ))}
        </g>
      </ArtSvg>
      {ERAS.map((e, i) => (
        <div
          key={e.label}
          lang="tr"
          style={{
            position: 'absolute',
            top: 1236,
            left: dotX(i) - 110,
            width: 220,
            textAlign: 'center',
            fontFamily: "'Inter', sans-serif",
            fontWeight: 500,
            fontSize: 18,
            letterSpacing: '0.18em',
            color: i === active ? COLORS.ink : COLORS.accent,
            opacity: dissolve(frame, 2, 10),
          }}
        >
          {e.label}
        </div>
      ))}
    </Paper>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 8 — Modern conclusion                                         */
/* ------------------------------------------------------------------ */

export const ModernScene: React.FC<{s: TimedScene}> = ({s}) => (
  <Paper>
    <ArtSvg>
      <HandshakeMoment cy={HAND_Y} enter={2} meet={Math.round(atLine(s, 'c1', 0.48))} spark={false} />
    </ArtSvg>
  </Paper>
);

/* ------------------------------------------------------------------ */
/* Scene 9 — Special first-episode ending                              */
/* ------------------------------------------------------------------ */

export const ENDING_TAIL_SECONDS = 6.2;

export const EndingScene: React.FC<{s: TimedScene; text: string}> = ({s, text}) => {
  const sec = useSec();
  const release = Math.round(atLine(s, 'e1', 0) + sec(0.15));
  const lineEnd = atLine(s, 'e1', 1);
  const enter = Math.round(lineEnd + sec(0.7));
  const meet = Math.round(enter + sec(1.9));
  return (
    <Paper>
      <ArtSvg>
        {/* the conclusion's handshake lets go… */}
        <HandshakeMoment cy={HAND_Y} enter={-90} meet={-60} release={release} spark={false} />
        {/* …and the brand greets the viewer */}
        <HandshakeMoment cy={HAND_Y} enter={enter} meet={meet} />
      </ArtSvg>
      <SpecialEndingText text={text} at={meet - 2} y={1150} />
    </Paper>
  );
};
