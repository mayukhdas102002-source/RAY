import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {C, POPPINS, MONO} from '../theme';

// Approximation of the Homely mark (dome + smile). Swap for the official SVG
// by replacing this component's contents.
export const Mark: React.FC<{size: number; color?: string}> = ({size, color = C.white}) => (
  <svg width={size} height={size * 0.85} viewBox="0 0 40 34">
    <path d="M8 17a12 12 0 0 1 24 0z" fill={color} />
    <path d="M4 21c4 9 28 9 32 0" stroke={color} strokeWidth={3.4} fill="none" strokeLinecap="round" />
  </svg>
);

export const Wordmark: React.FC<{size: number; color?: string}> = ({size, color = C.white}) => (
  <div style={{display: 'flex', alignItems: 'center', gap: size * 0.18, fontFamily: POPPINS, fontStyle: 'italic', fontWeight: 700, fontSize: size, color, letterSpacing: -size * 0.01}}>
    Homely
    <Mark size={size * 1.05} color={color} />
  </div>
);

// Enter/exit helper: 0→1 over `inF` frames from `start`, 1→0 over `outF` frames before `end`.
export const useInOut = (start: number, end: number, inF = 10, outF = 8) => {
  const f = useCurrentFrame();
  const a = interpolate(f, [start, start + inF], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const b = interpolate(f, [end - outF, end], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic)});
  return Math.min(a, b);
};

export const Super: React.FC<{text: string; start?: number; end: number; dark?: boolean; bottom?: number}> = ({text, start = 0, end, dark, bottom = 150}) => {
  const o = useInOut(start, end, 9, 7);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom, textAlign: 'center', opacity: o, transform: `translateY(${(1 - o) * 18}px)`,
      fontFamily: POPPINS, fontWeight: 600, fontSize: 54, color: dark ? '#2A1406' : C.white, letterSpacing: -0.5,
      textShadow: dark ? 'none' : '0 4px 30px rgba(0,0,0,.55)'}}>
      {text}
    </div>
  );
};

export const Glass: React.FC<{style?: React.CSSProperties; children: React.ReactNode; light?: boolean}> = ({style, children, light}) => (
  <div style={{position: 'absolute', borderRadius: 28, padding: 30,
    background: light ? 'rgba(255,255,255,.82)' : 'rgba(18,14,12,.46)',
    border: `1.5px solid ${light ? 'rgba(255,255,255,.9)' : 'rgba(255,180,140,.45)'}`,
    boxShadow: light ? '0 20px 60px rgba(90,40,10,.25)' : '0 0 80px rgba(255,107,61,.28), inset 0 1px 0 rgba(255,255,255,.12)',
    backdropFilter: 'blur(18px)', color: light ? '#2A1406' : C.white, fontFamily: POPPINS, ...style}}>
    {children}
  </div>
);

export const Bubble: React.FC<{text: string; start: number; end: number; from: 'user' | 'homely'; style?: React.CSSProperties; onLight?: boolean}> = ({text, start, end, from, style, onLight}) => {
  const f = useCurrentFrame();
  const o = useInOut(start, end, 8, 6);
  const chars = Math.floor(interpolate(f, [start + 4, start + 4 + text.length * 0.9], [0, text.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const isH = from === 'homely';
  return (
    <div style={{position: 'absolute', maxWidth: 620, padding: '20px 28px', borderRadius: 30,
      borderBottomRightRadius: isH ? 8 : 30, borderBottomLeftRadius: isH ? 30 : 8,
      background: isH ? C.orange : onLight ? 'rgba(255,255,255,.9)' : 'rgba(255,255,255,.14)',
      border: isH ? 'none' : `1.5px solid ${onLight ? 'rgba(0,0,0,.06)' : 'rgba(255,255,255,.28)'}`,
      color: isH ? C.white : onLight ? '#2A1406' : C.white, fontFamily: POPPINS, fontWeight: isH ? 600 : 500, fontSize: 34, lineHeight: 1.3,
      opacity: o, transform: `translateY(${(1 - o) * 14}px) scale(${0.96 + o * 0.04})`, backdropFilter: 'blur(10px)', ...style}}>
      <span>{text.slice(0, chars)}</span><span style={{opacity: 0}}>{text.slice(chars)}</span>
    </div>
  );
};

export const CountUp: React.FC<{to: number; start: number; dur: number; prefix?: string; suffix?: string; decimals?: number}> = ({to, start, dur, prefix = '', suffix = '', decimals = 0}) => {
  const f = useCurrentFrame();
  const v = interpolate(f, [start, start + dur], [0, to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return <span style={{fontVariantNumeric: 'tabular-nums'}}>{prefix}{v.toLocaleString('en-NZ', {minimumFractionDigits: decimals, maximumFractionDigits: decimals})}{suffix}</span>;
};

export const Pop: React.FC<{at: number; children: React.ReactNode; style?: React.CSSProperties}> = ({at, children, style}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: f - at, fps, config: {damping: 14, stiffness: 160}});
  return <div style={{transform: `scale(${s})`, opacity: Math.min(1, s * 1.4), ...style}}>{children}</div>;
};

export const Check: React.FC<{color?: string; size?: number}> = ({color = C.good, size = 30}) => (
  <svg width={size} height={size} viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill={color} /><path d="M7 12.5l3.2 3.2L17 9" stroke="#0A1216" strokeWidth={2.6} fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
);

export const Label: React.FC<{children: React.ReactNode; color?: string}> = ({children, color = 'rgba(255,255,255,.62)'}) => (
  <span style={{fontFamily: MONO, fontWeight: 500, fontSize: 18, letterSpacing: 3, textTransform: 'uppercase', color}}>{children}</span>
);
