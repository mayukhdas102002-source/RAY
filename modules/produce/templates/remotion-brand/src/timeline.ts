import type {Caption} from '@remotion/captions';
import captionsJson from './captions.json';
import timelineJson from './timeline.json';

// timeline.json  <- scripts/timeline_from_vo.py   (scene timing in SECONDS on the master clock)
// captions.json  <- scripts/captions_convert.py --to remotion  (Remotion Caption[], ms on the master clock)

export type SceneKind =
  | 'title'
  | 'statement'
  | 'stat'
  | 'list'
  | 'quote'
  | 'lowerThird'
  | 'footage'
  | 'image'
  | 'endCard';

export type Scene = {
  id: string;
  kind: SceneKind;
  start: number;
  duration: number;
  kicker?: string;
  headline?: string;
  body?: string;
  stat?: string;
  items?: string[];
  name?: string;
  role?: string;
  /** public/ path of a video or image for footage / image / lowerThird scenes */
  media?: string | null;
  /** seconds into the source media to start from */
  mediaStart?: number;
  /** public/ path of this scene's voiceover WAV */
  vo?: string | null;
  /** seconds after the scene start that the VO begins (lead-in breath) */
  voDelay?: number;
  /** extra gain for this scene's VO (1 = unchanged) */
  voVolume?: number;
};

export type Timeline = {
  title: string;
  fps: number;
  music: null | {src: string; volume: number; duckTo: number; fadeInSeconds?: number; fadeOutSeconds?: number};
  scenes: Scene[];
};

export const TIMELINE = timelineJson as unknown as Timeline;
export const CAPTIONS = captionsJson as unknown as Caption[];

export const totalSeconds = (t: Timeline) =>
  t.scenes.reduce((max, s) => Math.max(max, s.start + s.duration), 0);
