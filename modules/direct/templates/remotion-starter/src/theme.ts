import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

// Fonts are bundled in public/fonts so renders work offline.
export const POPPINS = 'Poppins';
export const MONO = 'IBM Plex Mono';

const faces: [string, string, string, 'normal' | 'italic'][] = [
  [POPPINS, 'poppins-latin-500-normal.woff2', '500', 'normal'],
  [POPPINS, 'poppins-latin-600-normal.woff2', '600', 'normal'],
  [POPPINS, 'poppins-latin-700-normal.woff2', '700', 'normal'],
  [POPPINS, 'poppins-latin-700-italic.woff2', '700', 'italic'],
  [MONO, 'ibm-plex-mono-latin-500-normal.woff2', '500', 'normal'],
];
faces.forEach(([family, file, weight, style]) => {
  loadFont({family, url: staticFile(`fonts/${file}`), weight, style});
});

export const C = {
  orange: '#FF6B3D',
  ember: '#FFB36B',
  cream: '#FFF1C9',
  dawn: '#FFD28A',
  ink: '#0A1216',
  teal: '#0F3A3C',
  night: '#10262E',
  good: '#7FD6A3',
  white: '#FFFFFF',
};
