import React from 'react';
import {Composition, Still} from 'remotion';
import {VIDEO} from './brand/theme';
import {FontGate} from './components/FontGate';
import {Cover} from './components/Cover';
import {Episode01, EP01_TIMELINE, EP01_TITLE} from './episodes/ep01/Episode01';
import {ClaspedHands} from './illustrations/hands';
import {LogoIntro} from './brand/Logo';
import {HAND_Y} from './episodes/ep01/scenes';

const Ep01 = () => (
  <FontGate>
    <Episode01 />
  </FontGate>
);

const Ep01Cover = () => (
  <FontGate>
    <Cover title={EP01_TITLE}>
      <g transform={`translate(540 ${HAND_Y}) scale(1.22)`}>
        <ClaspedHands />
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
