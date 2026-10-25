import React from 'react';
import {AbsoluteFill, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame, Easing} from 'remotion';
import data from './shots.json';
import {C, POPPINS, MONO} from './theme';
import {EndCard, Led, ScrApproved, ScrDirectory, ScrEligible, ScrMarket, ScrProfile, ScrTicket} from './screens/Screens';

export const FPS = 30;
const f = (s: number) => Math.round(s * FPS);
export const TOTAL = f(data.runtime);
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Drop finished Higgsfield clips in public/plates/<ID>.mp4 and list them here.
// e.g. PLATES = {S01: {file: 'S01.mp4', start: 0.4}}
export const PLATES: Record<string, {file: string; start?: number; speed?: number}> = {};

// Which Remotion screen goes into which shot, and how it's framed in the animatic.
const PHONE: Record<string, React.FC> = {S04: ScrProfile, S06: ScrEligible, S12: ScrApproved, S15: ScrMarket};
const TABLET: Record<string, React.FC> = {S09: ScrTicket, S02: ScrDirectory};
const LED: Record<string, [number, number]> = {S03: [1, 1], S04: [1, 3], S05: [3, 4], S06: [5, 5], S07: [5, 8], S08: [9, 9], S09: [9, 10], S10: [11, 11], S11: [12, 23], S12: [24, 24], S13: [24, 24]};

const Board: React.FC<{s: any; dur: number}> = ({s, dur}) => {
  const fr = useCurrentFrame();
  const o = interpolate(fr, [0, 9], [0, 1], {...clamp, easing: Easing.inOut(Easing.quad)});
  const day = s.id === 'S11' ? interpolate(fr, [0, dur], [0, 1], clamp) : null;
  const bg = s.id === 'S11'
    ? `linear-gradient(180deg, ${mix(day!)} , #0E1418)`
    : s.act === 'Doors opening' ? 'linear-gradient(135deg,#F7E3BF,#E8B77A)' : 'linear-gradient(135deg,#1A2025,#0E1216)';
  const dark = s.act !== 'Doors opening';
  return (
    <AbsoluteFill style={{background: bg, fontFamily: POPPINS, color: dark ? '#E9EEF2' : '#2A1406', padding: '120px 140px', opacity: o}}>
      <div style={{fontFamily: MONO, fontSize: 24, letterSpacing: 4, color: dark ? '#8A98A3' : '#7A4A28'}}>{s.id} · {s.maker.toUpperCase()} · {s.model}</div>
      <div style={{fontWeight: 700, fontSize: 88, letterSpacing: -2, marginTop: 14}}>{s.name}</div>
      <div style={{fontSize: 36, lineHeight: 1.45, maxWidth: ['S02', 'S09'].includes(s.id) ? 500 : ['S04', 'S06', 'S12', 'S15'].includes(s.id) ? 1080 : 1300, marginTop: 24, opacity: 0.9}}>{s.frame}</div>
    </AbsoluteFill>
  );
};

const mix = (t: number) => {
  // morning → noon → sunset → night → dawn
  const stops = ['#9EC3DD', '#BFE0F2', '#F09A5B', '#101B2E', '#F4B98A'];
  const k = Math.min(stops.length - 2, Math.floor(t * (stops.length - 1)));
  const u = t * (stops.length - 1) - k;
  const a = stops[k].match(/\w\w/g)!.map((h) => parseInt(h, 16));
  const b = stops[k + 1].match(/\w\w/g)!.map((h) => parseInt(h, 16));
  return `rgb(${a.map((v, i) => Math.round(v + (b[i] - v) * u)).join(',')})`;
};

const PhoneMock: React.FC<{Screen: React.FC; right?: boolean}> = ({Screen, right}) => {
  const fr = useCurrentFrame();
  const o = interpolate(fr, [0, 8], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const W = 1080 * 0.36, H = 2340 * 0.36;
  return (
    <div style={{position: 'absolute', right: right ? 170 : undefined, left: right ? undefined : (1920 - W) / 2, top: (1080 - H) / 2 + (1 - o) * 30, width: W + 28, height: H + 28, borderRadius: 64, background: '#0B0B0B', padding: 14, boxShadow: '0 40px 90px rgba(0,0,0,.5)', opacity: o}}>
      <div style={{width: W, height: H, borderRadius: 52, overflow: 'hidden', position: 'relative'}}>
        <div style={{width: 1080, height: 2340, transform: 'scale(0.36)', transformOrigin: 'top left', position: 'absolute'}}><Screen /></div>
      </div>
    </div>
  );
};

const TabletMock: React.FC<{Screen: React.FC; w: number; h: number}> = ({Screen, w, h}) => {
  const k = 1100 / w;
  return (
    <div style={{position: 'absolute', right: 120, top: (1080 - h * k) / 2, width: w * k + 36, height: h * k + 36, borderRadius: 36, background: '#0B0B0B', padding: 18, boxShadow: '0 40px 90px rgba(0,0,0,.5)'}}>
      <div style={{width: w * k, height: h * k, borderRadius: 20, overflow: 'hidden', position: 'relative'}}>
        <div style={{width: w, height: h, transform: `scale(${k})`, transformOrigin: 'top left', position: 'absolute'}}><Screen /></div>
      </div>
    </div>
  );
};

const LedInset: React.FC<{from: number; to: number}> = ({from, to}) => (
  <div style={{position: 'absolute', left: 140, bottom: 250, width: 360, height: 160, borderRadius: 14, overflow: 'hidden', boxShadow: '0 0 0 3px #2B3238'}}>
    <div style={{width: 600, height: 260, transform: 'scale(0.6)', transformOrigin: 'top left'}}><Led from={from} to={to} /></div>
  </div>
);

const Sub: React.FC<{text?: string}> = ({text}) => {
  if (!text) return null;
  const lines = text.split(/(?=\b(?:LIFT VOICE|JOSH|AROHA|LENDER 1|LENDER 2)\b)/).map((l) => l.trim()).filter(Boolean);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 70, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8}}>
      {lines.map((l) => (
        <div key={l} style={{fontFamily: POPPINS, fontWeight: 500, fontSize: 32, color: '#fff', background: 'rgba(0,0,0,.62)', padding: '8px 18px', borderRadius: 8, maxWidth: 1500, textAlign: 'center'}}>{l}</div>
      ))}
    </div>
  );
};

const Burn: React.FC<{id: string; from: number}> = ({id, from}) => {
  const fr = useCurrentFrame();
  const s = (from + fr) / FPS;
  return <div style={{position: 'absolute', right: 40, top: 36, fontFamily: MONO, fontSize: 22, color: 'rgba(255,255,255,.8)', background: 'rgba(0,0,0,.5)', padding: '6px 10px', borderRadius: 4}}>{id} · {s.toFixed(1)}s</div>;
};

export const GoingUp: React.FC<{burnIn: boolean}> = ({burnIn}) => (
  <AbsoluteFill style={{background: '#000'}}>
    {data.shots.map((s: any) => {
      const from = f(s.t[0]);
      const dur = f(s.t[1]) - from;
      const plate = PLATES[s.id];
      const Ph = PHONE[s.id];
      const Tb = TABLET[s.id];
      const led = LED[s.id];
      return (
        <Sequence key={s.id} from={from} durationInFrames={dur} name={`${s.id} ${s.name}`}>
          {s.id === 'S16' ? <EndCard /> : plate
            ? <OffthreadVideo src={staticFile(`plates/${plate.file}`)} startFrom={f(plate.start ?? 0)} playbackRate={plate.speed ?? 1} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
            : <Board s={s} dur={dur} />}
          {!plate && Ph ? <PhoneMock Screen={Ph} right /> : null}
          {!plate && Tb ? <TabletMock Screen={Tb} w={s.id === 'S02' ? 1920 : 1600} h={s.id === 'S02' ? 1080 : 1000} /> : null}
          {!plate && led ? <LedInset from={led[0]} to={led[1]} /> : null}
          {s.id !== 'S16' ? <Sub text={s.sound} /> : null}
          {burnIn ? <Burn id={s.id} from={from} /> : null}
        </Sequence>
      );
    })}
  </AbsoluteFill>
);
