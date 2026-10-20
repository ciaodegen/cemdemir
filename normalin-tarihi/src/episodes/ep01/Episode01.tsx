import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import {COLORS, VIDEO} from '../../brand/theme';
import {LOGO_INTRO_SECONDS, LogoIntro} from '../../brand/Logo';
import {SceneFade} from '../../components/SceneFade';
import {Subtitles} from '../../components/Subtitles';
import {Block, buildTimeline, sceneOf, ScriptLine, MeasuredLine} from '../../timing';
import script from './script.json';
import measured from './timing.generated.json';
import {
  AllianceScene,
  ENDING_TAIL_SECONDS,
  EndingScene,
  GreeceScene,
  MesopotamiaScene,
  ModernScene,
  OpeningScene,
  TheoryScene,
  TimeScene,
} from './scenes';

export const EP01_TITLE = script.title;
export const EP01_ENDING_TEXT = 'Tanıştığımıza *memnun olduk.*';
/** Headline lines; *word* = highlight colour. */
export const EP01_TITLE_LINES = ['Neden', '*tokalaşıyoruz?*'];

const BLOCKS: Block[] = [
  {scene: 'opening', lines: ['q1', 'q2'], lead: 0.45, tail: 1.3},
  {scene: 'logo', fixed: LOGO_INTRO_SECONDS},
  {scene: 'mesopotamia', lines: ['m1', 'm2'], lead: 0.5, tail: 0.5},
  {scene: 'theory', lines: ['t1', 't2'], lead: 0.5, tail: 0.6},
  {scene: 'alliance', lines: ['a1', 'a2'], lead: 0.5, tail: 0.9},
  {scene: 'greece', lines: ['g1', 'g2'], lead: 0.4, tail: 0.6},
  {scene: 'time', lines: ['p1'], lead: 0.35, tail: 2.0},
  {scene: 'modern', lines: ['c1'], lead: 0.4, tail: 0.5},
  {scene: 'ending', lines: ['e1'], lead: 0.25, tail: ENDING_TAIL_SECONDS},
];

export const EP01_TIMELINE = buildTimeline(
  script.lines as ScriptLine[],
  measured as Record<string, MeasuredLine>,
  BLOCKS,
  VIDEO.fps,
);

export const Episode01: React.FC = () => {
  const tl = EP01_TIMELINE;
  const sc = (name: string) => sceneOf(tl, name);
  const seq = (name: string, node: React.ReactNode, fadeIn = 9, fadeOut = 9) => {
    const s = sc(name);
    return (
      <Sequence key={name} from={s.from} durationInFrames={s.duration} name={name}>
        <SceneFade duration={s.duration} fadeIn={fadeIn} fadeOut={fadeOut}>
          {node}
        </SceneFade>
      </Sequence>
    );
  };
  return (
    <AbsoluteFill style={{background: COLORS.paper}}>
      {seq('opening', <OpeningScene s={sc('opening')} questionLines={EP01_TITLE_LINES} />, 0, 7)}
      {seq('logo', <LogoIntro />, 0, 8)}
      {seq('mesopotamia', <MesopotamiaScene s={sc('mesopotamia')} />, 6, 9)}
      {seq('theory', <TheoryScene s={sc('theory')} />)}
      {seq('alliance', <AllianceScene s={sc('alliance')} />)}
      {seq('greece', <GreeceScene s={sc('greece')} />)}
      {seq('time', <TimeScene s={sc('time')} />)}
      {seq('modern', <ModernScene s={sc('modern')} />, 9, 0)}
      {seq('ending', <EndingScene s={sc('ending')} text={EP01_ENDING_TEXT} />, 0, 24)}
      <Subtitles cues={tl.cues} />
      {tl.lines
        .filter((l) => l.file)
        .map((l) => (
          <Sequence key={l.id} from={l.start} name={`vo ${l.id}`}>
            <Audio src={staticFile(l.file as string)} />
          </Sequence>
        ))}
    </AbsoluteFill>
  );
};
