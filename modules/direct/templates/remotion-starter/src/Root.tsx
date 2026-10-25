import React from 'react';
import {Composition, Folder} from 'remotion';
import {GoingUp, TOTAL, FPS} from './Film';
import data from './shots.json';
const d = (id: string) => Math.round((data.shots.find((s: any) => s.id === id)!.t[1] - data.shots.find((s: any) => s.id === id)!.t[0]) * FPS);
import {EndCard, Led, ScrApproved, ScrDirectory, ScrEligible, ScrMarket, ScrProfile, ScrTicket} from './screens/Screens';

// Screen compositions are sized for corner-pinning onto the blank screens in the AI plates.
const phone = {width: 1080, height: 2340, fps: FPS};
export const Root: React.FC = () => (
  <>
    <Composition id="GoingUp" component={GoingUp} durationInFrames={TOTAL} fps={FPS} width={1920} height={1080} defaultProps={{burnIn: true}} />
    <Composition id="GoingUpClean" component={GoingUp} durationInFrames={TOTAL} fps={FPS} width={1920} height={1080} defaultProps={{burnIn: false}} />
    <Folder name="Screens">
      <Composition id="SCR-Profile" component={ScrProfile} durationInFrames={d('S04')} {...phone} />
      <Composition id="SCR-Eligible" component={ScrEligible} durationInFrames={d('S06')} {...phone} />
      <Composition id="SCR-Approved" component={ScrApproved} durationInFrames={d('S12')} {...phone} />
      <Composition id="SCR-Market" component={ScrMarket} durationInFrames={d('S15')} {...phone} />
      <Composition id="SCR-Ticket" component={ScrTicket} durationInFrames={d('S09')} fps={FPS} width={1600} height={1000} />
      <Composition id="SCR-Directory" component={ScrDirectory} durationInFrames={d('S02')} fps={FPS} width={1920} height={1080} />
    </Folder>
    <Folder name="LED">
      {([['LED-01', 1, 1, d('S03')], ['LED-05', 5, 5, d('S06')], ['LED-09', 9, 9, d('S08')], ['LED-11', 11, 11, d('S10')], ['LED-12-23', 12, 23, d('S11')], ['LED-24', 24, 24, d('S12')]] as [string, number, number, number][]).map(([id, a, b, d]) => (
        <Composition key={id} id={id} component={Led} durationInFrames={d} fps={FPS} width={600} height={260} defaultProps={{from: a, to: b, transparent: true}} />
      ))}
    </Folder>
    <Composition id="EndCard" component={EndCard} durationInFrames={d('S16')} fps={FPS} width={1920} height={1080} />
  </>
);
