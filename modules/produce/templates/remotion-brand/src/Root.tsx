import React from 'react';
import {CalculateMetadataFunction, Composition, Folder, Still} from 'remotion';
import {BrandFilm, BrandFilmProps} from './BrandFilm';
import {EndCardStill, ThumbnailStill} from './Stills';
import {TIMELINE, totalSeconds} from './timeline';

// One composition per delivery aspect. Text, logo and safe areas reflow from the frame size.
export const ASPECTS = {
  '16x9': {width: 1920, height: 1080},
  '9x16': {width: 1080, height: 1920},
  '1x1': {width: 1080, height: 1080},
  '4x5': {width: 1080, height: 1350},
} as const;

// Duration always comes from the data, never hardcoded: the timeline passed in --props wins,
// else src/timeline.json. Batch/personalised renders just pass a different timeline.
const calculateMetadata: CalculateMetadataFunction<BrandFilmProps> = ({props}) => {
  const t = props.timeline ?? TIMELINE;
  const fps = t.fps || 30;
  return {
    fps,
    durationInFrames: Math.max(1, Math.ceil(totalSeconds(t) * fps)),
    defaultOutName: `${props.outName ?? 'brandfilm'}`,
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Folder name="Films">
        {Object.entries(ASPECTS).map(([key, size]) => (
          <Composition
            key={key}
            id={`BrandFilm-${key}`}
            component={BrandFilm}
            durationInFrames={300}
            fps={30}
            width={size.width}
            height={size.height}
            defaultProps={{}}
            calculateMetadata={calculateMetadata}
          />
        ))}
      </Folder>
      <Folder name="Stills">
        {Object.entries(ASPECTS).map(([key, size]) => (
          <Still key={key} id={`EndCard-${key}`} component={EndCardStill} width={size.width} height={size.height} />
        ))}
        <Still id="Thumbnail-16x9" component={ThumbnailStill} width={1280} height={720} />
        <Still id="Thumbnail-9x16" component={ThumbnailStill} width={1080} height={1920} />
      </Folder>
    </>
  );
};
