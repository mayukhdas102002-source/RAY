import React from 'react';
import {AbsoluteFill, interpolate, Sequence, staticFile, useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import type {Caption} from '@remotion/captions';
import {BRAND} from './brand';
import {Captions} from './Captions';
import {SceneView} from './scenes/Scenes';
import {CAPTIONS, Timeline, TIMELINE, totalSeconds} from './timeline';

export type BrandFilmProps = {
  /** Override the whole timeline (batch / personalised renders pass this via --props). */
  timeline?: Timeline;
  /** Override captions (Remotion Caption[] on the master clock). */
  captions?: Caption[];
  /** Turn burned-in captions off for a clean master (deliver an SRT instead). */
  showCaptions?: boolean;
  outName?: string;
};

// Music bed with sidechain-style ducking under every scene that has VO.
// Prefer mixing in scripts/mix.py for the final master; this keeps the Studio preview honest.
const MusicBed: React.FC<{t: Timeline}> = ({t}) => {
  const {fps} = useVideoConfig();
  const m = t.music;
  if (!m) return null;
  const total = Math.ceil(totalSeconds(t) * fps);
  const voRanges = t.scenes
    .filter((s) => s.vo)
    .map((s) => [Math.round((s.start + (s.voDelay ?? 0)) * fps), Math.round((s.start + s.duration) * fps)] as const);
  const ramp = Math.round(0.25 * fps);
  const fadeIn = Math.max(1, Math.round((m.fadeInSeconds ?? 1) * fps));
  const fadeOut = Math.max(1, Math.round((m.fadeOutSeconds ?? 2) * fps));
  return (
    <Audio
      src={staticFile(m.src)}
      volume={(f) => {
        let duck = 1;
        for (const [a, b] of voRanges) {
          const v = interpolate(f, [a - ramp, a, b, b + ramp], [1, m.duckTo, m.duckTo, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          duck = Math.min(duck, v);
        }
        const env = interpolate(f, [0, fadeIn, total - fadeOut, total], [0, 1, 1, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        return m.volume * duck * env;
      }}
    />
  );
};

export const BrandFilm: React.FC<BrandFilmProps> = (props) => {
  const {fps} = useVideoConfig();
  const t = props.timeline ?? TIMELINE;
  const caps = props.captions ?? CAPTIONS;
  const showCaptions = (props.showCaptions ?? BRAND.captions.enabled) && caps.length > 0;
  return (
    <AbsoluteFill style={{backgroundColor: BRAND.colors.bg}}>
      {t.scenes.map((s) => (
        <Sequence
          key={s.id}
          name={`${s.id} · ${s.kind}`}
          from={Math.round(s.start * fps)}
          durationInFrames={Math.max(1, Math.round(s.duration * fps))}
        >
          <SceneView scene={s} />
          {s.vo ? (
            <Sequence from={Math.round((s.voDelay ?? 0) * fps)} name={`${s.id} VO`} layout="none">
              <Audio src={staticFile(s.vo)} volume={s.voVolume ?? 1} />
            </Sequence>
          ) : null}
        </Sequence>
      ))}
      <MusicBed t={t} />
      {showCaptions ? <Captions captions={caps} /> : null}
    </AbsoluteFill>
  );
};
