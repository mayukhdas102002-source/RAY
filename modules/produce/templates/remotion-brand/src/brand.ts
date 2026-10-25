import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';
import brandJson from './brand.json';

// brand.json is generated from the project's brand kit by scripts/brand_tokens.py.
// Never hand-type colours or fonts into scenes: read them from BRAND.

type FontRole = {family: string; weight: number; fallback: string};
type FontFile = {family: string; file: string; weight: string; style: 'normal' | 'italic'};

export type Brand = {
  name: string;
  url: string;
  tagline: string;
  colors: Record<
    | 'primary'
    | 'secondary'
    | 'accent'
    | 'bg'
    | 'surface'
    | 'fg'
    | 'muted'
    | 'line'
    | 'captionBox'
    | 'captionText'
    | 'captionHighlight',
    string
  >;
  fonts: {heading: FontRole; body: FontRole; mono: FontRole};
  fontFiles: FontFile[];
  logo: {light: string | null; dark: string | null};
  radius: number;
  motion: {springDamping: number; entranceSeconds: number; stagger: number; exitFrames: number};
  captions: {enabled: boolean; upper: boolean; combineMs: number; position: 'bottom' | 'center' | 'top'; box: boolean};
  endCard: {cta: string; url: string; legal: string};
};

export const BRAND = brandJson as unknown as Brand;

// Font files live in public/brand/fonts/. loadFont blocks rendering until each face is ready.
for (const f of BRAND.fontFiles) {
  loadFont({
    family: f.family,
    url: staticFile(`brand/fonts/${f.file}`),
    weight: f.weight,
    style: f.style,
  }).catch((err) => {
    console.error(`Font failed to load: ${f.file}`, err);
  });
}

export const fontStack = (role: keyof Brand['fonts']) =>
  `'${BRAND.fonts[role].family}', ${BRAND.fonts[role].fallback}`;
