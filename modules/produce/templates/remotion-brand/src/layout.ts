import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {BRAND} from './brand';

// Safe areas and type scale that reflow from the frame size.
// - 16:9 / 1:1 / 4:5: ~7% side margin, ~9% top/bottom (Remotion skill: 80px sides / 100px top-bottom at 1080 wide).
// - 9:16: phone-safe text box x 90-930, y 200-1600 at 1080x1920 (herk short-form rule), so UI chrome never covers copy.
export const useLayout = () => {
  const {width, height} = useVideoConfig();
  const vertical = height / width > 1.3;
  const u = Math.min(width, height) / 1080; // 1 unit = 1px at 1080 short side
  const pad = vertical
    ? {left: 90 * (width / 1080), right: 150 * (width / 1080), top: 200 * (height / 1920), bottom: 320 * (height / 1920)}
    : {left: width * 0.07, right: width * 0.07, top: height * 0.09, bottom: height * 0.09};
  // Minimum sizes at 1080 short side: headline 84px, supporting 44px (Remotion create rules). Scale with u.
  const type = {
    kicker: 34 * u,
    headline: (vertical ? 96 : 92) * u,
    hero: (vertical ? 128 : 120) * u,
    body: 46 * u,
    stat: (vertical ? 300 : 260) * u,
    caption: (vertical ? 64 : 54) * u,
  };
  return {width, height, vertical, u, pad, type};
};

// Frame-pure entrance: same output for the same frame, no state, no CSS transitions.
export const useEntrance = (delaySeconds = 0) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({
    frame: frame - Math.round(delaySeconds * fps),
    fps,
    config: {damping: BRAND.motion.springDamping},
    durationInFrames: Math.max(1, Math.round(BRAND.motion.entranceSeconds * fps)),
  });
  return {
    opacity: p,
    translateY: interpolate(p, [0, 1], [40, 0]),
    scale: interpolate(p, [0, 1], [0.96, 1]),
    progress: p,
  };
};

// Short fade at the tail of a scene so hard cuts never pop a half-drawn element.
export const useExit = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const n = BRAND.motion.exitFrames;
  return interpolate(frame, [durationInFrames - n, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
};
