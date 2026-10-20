import React from 'react';
import {Composition, Still} from 'remotion';
import {VIDEO} from './brand/theme';
import {FontGate} from './components/FontGate';
import {Cover} from './components/Cover';
import {Episode01, EP01_TIMELINE, EP01_TITLE_LINES} from './episodes/ep01/Episode01';
import {ClaspedHands, MeetSpark} from './illustrations/hands';
import {groundMass} from './illustrations/architecture';
import {COLORS} from './brand/theme';
import {LogoIntro} from './brand/Logo';

const Ep01 = () => (
  <FontGate>
    <Episode01 />
  </FontGate>
);

const Ep01Cover = () => (
  <FontGate>
    <Cover titleLines={EP01_TITLE_LINES}>
      <path d={groundMass(1150, 1560)} fill={COLORS.sandPale} />
      <circle cx={790} cy={1010} r={52} fill={COLORS.terracottaLight} opacity={0.85} />
      <g transform="translate(540 1250) scale(1.3)">
        <ClaspedHands sleeveA="modern" sleeveB="modernOlive" />
        <MeetSpark />
      </g>
    </Cover>
  </FontGate>
);

const Logo = () => (
  <FontGate>
    <LogoIntro />
  </FontGate>
);

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Ep01" component={Ep01} durationInFrames={EP01_TIMELINE.totalFrames} {...VIDEO} />
    <Still id="Ep01Cover" component={Ep01Cover} width={VIDEO.width} height={VIDEO.height} />
    <Composition id="LogoIntro" component={Logo} durationInFrames={60} {...VIDEO} />
  </>
);
