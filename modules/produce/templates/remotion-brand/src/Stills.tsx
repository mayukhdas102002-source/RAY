import React from 'react';
import {AbsoluteFill} from 'remotion';
import {BRAND, fontStack} from './brand';
import {useLayout} from './layout';
import {EndCard} from './scenes/EndCard';
import {TIMELINE} from './timeline';

export const EndCardStill: React.FC = () => <EndCard still />;

// Thumbnail: the film's first headline, big, on brand. Swap in a keyframe behind it if you have one.
export const ThumbnailStill: React.FC = () => {
  const {u, pad} = useLayout();
  const first = TIMELINE.scenes.find((s) => s.headline)?.headline ?? BRAND.tagline;
  const C = BRAND.colors;
  return (
    <AbsoluteFill style={{backgroundColor: C.bg, padding: pad.left, justifyContent: 'center'}}>
      <div style={{width: 160 * u, height: 14 * u, borderRadius: 14 * u, backgroundColor: C.primary, marginBottom: 40 * u}} />
      <div
        style={{
          fontFamily: fontStack('heading'),
          fontWeight: 800,
          fontSize: 140 * u,
          lineHeight: 1,
          letterSpacing: '-0.03em',
          color: C.fg,
          maxWidth: '12ch',
        }}
      >
        {first}
      </div>
      <div style={{fontFamily: fontStack('mono'), fontSize: 36 * u, color: C.accent, marginTop: 40 * u, letterSpacing: '0.12em'}}>
        {BRAND.name.toUpperCase()}
      </div>
    </AbsoluteFill>
  );
};
