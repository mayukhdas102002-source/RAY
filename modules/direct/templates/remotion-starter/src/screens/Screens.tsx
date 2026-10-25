import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {C, POPPINS, MONO} from '../theme';
import {Mark, CountUp} from '../ui/kit';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const INK = '#1C1714';
const SUB = '#7A6E68';
const LINE = '#EFE7E2';
const BG = '#FFFAF7';

const useIn = (at: number, dur = 10) => {
  const f = useCurrentFrame();
  return interpolate(f, [at, at + dur], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
};
const usePop = (at: number) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: f - at, fps, config: {damping: 15, stiffness: 170}});
};

const Tick: React.FC<{on: number; size?: number}> = ({on, size = 44}) => {
  const p = usePop(on);
  return (
    <div style={{width: size, height: size, borderRadius: '50%', background: p > 0.05 ? C.orange : LINE, transform: `scale(${0.7 + p * 0.3})`, display: 'grid', placeItems: 'center', flexShrink: 0}}>
      <svg width={size * 0.55} height={size * 0.55} viewBox="0 0 24 24" style={{opacity: p}}><path d="M5 12.5l4.2 4.2L19 7" stroke="#fff" strokeWidth={3} fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
    </div>
  );
};

// ---------- Phone chrome ----------
export const Phone: React.FC<{children: React.ReactNode; title?: string; cta?: string; ctaAt?: number}> = ({children, title, cta, ctaAt = 0}) => (
  <AbsoluteFill style={{background: BG}}><div style={{position: 'absolute', left: 0, top: 0, width: 864, height: 1872, transform: 'scale(1.25)', transformOrigin: 'top left', background: BG, fontFamily: POPPINS, color: INK}}>
    <div style={{height: 130, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', padding: '0 64px 18px', fontWeight: 600, fontSize: 38}}>
      <span>9:0{title === 'late' ? '4' : '1'}</span>
      <span style={{display: 'flex', gap: 12, alignItems: 'center'}}>
        <span style={{width: 44, height: 22, borderRadius: 6, border: `3px solid ${INK}`, position: 'relative'}}><span style={{position: 'absolute', inset: 3, right: 10, background: INK, borderRadius: 2}} /></span>
      </span>
    </div>
    <div style={{display: 'flex', alignItems: 'center', gap: 14, padding: '26px 64px 20px'}}>
      <Mark size={58} color={C.orange} />
      <span style={{fontWeight: 700, fontStyle: 'italic', fontSize: 50, color: C.orange}}>Homely</span>
    </div>
    <div style={{position: 'absolute', left: 64, right: 64, top: 260, bottom: 80, display: 'flex', flexDirection: 'column', gap: 34}}>{children}</div>
    {cta ? <Cta text={cta} at={ctaAt} /> : null}
  </div></AbsoluteFill>
);

const Cta: React.FC<{text: string; at: number}> = ({text, at}) => {
  const o = useIn(at, 12);
  return (
    <div style={{position: 'absolute', left: 64, right: 64, bottom: 90, height: 150, borderRadius: 75, background: C.orange, color: '#fff', display: 'grid', placeItems: 'center', fontWeight: 600, fontSize: 48, opacity: o, transform: `translateY(${(1 - o) * 30}px)`, boxShadow: '0 16px 40px rgba(255,107,61,.35)'}}>{text}</div>
  );
};

const Card: React.FC<{children: React.ReactNode; style?: React.CSSProperties; o?: number}> = ({children, style, o = 1}) => (
  <div style={{background: '#fff', borderRadius: 40, padding: 44, boxShadow: '0 12px 40px rgba(60,30,10,.08)', border: `2px solid ${LINE}`, opacity: o, transform: `translateY(${(1 - o) * 30}px)`, ...style}}>{children}</div>
);
const Eyebrow: React.FC<{children: React.ReactNode; color?: string}> = ({children, color = SUB}) => (
  <div style={{fontFamily: MONO, fontSize: 28, letterSpacing: 4, textTransform: 'uppercase', color}}>{children}</div>
);

// ---------- SCR-Profile · real-time borrower profile (3s) ----------
export const ScrProfile: React.FC = () => {
  const f = useCurrentFrame();
  const phase2 = interpolate(f, [34, 44], [0, 1], clamp);
  const docs = ['Bank connected · Open Finance', 'Payslips verified', 'ID verified'];
  const spend: [string, number, boolean][] = [['Rent', 2480, false], ['Groceries', 1120, false], ['Transport', 410, false], ['Uber Eats', 386, true]];
  const max = 2480;
  return (
    <Phone cta={phase2 > 0.5 ? 'Send to 9 lenders' : 'Connecting…'} ctaAt={4}>
      <div style={{opacity: 1 - phase2, position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', gap: 30}}>
        <div style={{fontWeight: 700, fontSize: 76, lineHeight: 1.05, letterSpacing: -2}}>Let's build your profile.</div>
        {docs.map((d, i) => (
          <Card key={d} o={useIn(2 + i * 6)} style={{display: 'flex', alignItems: 'center', gap: 28, padding: 38}}>
            <Tick on={8 + i * 7} /><span style={{fontSize: 40, fontWeight: 500}}>{d}</span>
          </Card>
        ))}
      </div>
      <div style={{opacity: phase2, position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', gap: 30, transform: `translateY(${(1 - phase2) * 40}px)`}}>
        <Eyebrow color={C.orange}>Borrower profile · ready</Eyebrow>
        <div style={{display: 'flex', gap: 24}}>
          <Card style={{flex: 1, padding: 36}}><Eyebrow>Income</Eyebrow><div style={{fontWeight: 700, fontSize: 60}}><CountUp to={184000} start={40} dur={28} prefix="$" /></div></Card>
          <Card style={{flex: 1, padding: 36}}><Eyebrow>Deposit</Eyebrow><div style={{fontWeight: 700, fontSize: 60}}><CountUp to={142000} start={44} dur={28} prefix="$" /></div></Card>
        </div>
        <Card>
          <Eyebrow>Your spending · per month</Eyebrow>
          <div style={{display: 'flex', flexDirection: 'column', gap: 26, marginTop: 26}}>
            {spend.map(([k, v, hot], i) => {
              const w = interpolate(f, [46 + i * 4, 66 + i * 4], [0, v / max], {...clamp, easing: Easing.out(Easing.cubic)});
              return (
                <div key={k}>
                  <div style={{display: 'flex', justifyContent: 'space-between', fontSize: 38, fontWeight: hot ? 700 : 500, color: hot ? C.orange : INK}}><span>{k}</span><span>${v.toLocaleString('en-NZ')}</span></div>
                  <div style={{height: 18, borderRadius: 9, background: LINE, marginTop: 10}}><div style={{width: `${w * 100}%`, height: '100%', borderRadius: 9, background: hot ? C.orange : '#CDBFB7'}} /></div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>
    </Phone>
  );
};

// ---------- SCR-Eligible (2s) ----------
export const ScrEligible: React.FC = () => {
  const lenders = ['Kōwhai Bank', 'Harbour Home Loans', 'Southern Mutual'];
  return (
    <Phone cta="Lenders are reviewing" ctaAt={34}>
      <Eyebrow color={C.orange}>Real-time eligibility</Eyebrow>
      <div style={{fontWeight: 700, fontSize: 84, lineHeight: 1.02, letterSpacing: -2}}>Pre-approved with <span style={{color: C.orange}}>9 lenders</span></div>
      <Card o={useIn(8)}><Eyebrow>Your buying power</Eyebrow><div style={{fontWeight: 700, fontSize: 104, letterSpacing: -2}}><CountUp to={845000} start={8} dur={30} prefix="$" /></div></Card>
      {lenders.map((l, i) => (
        <Card key={l} o={useIn(20 + i * 6)} style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 36}}>
          <span style={{fontSize: 42, fontWeight: 600}}>{l}</span><span style={{fontFamily: MONO, fontSize: 34, color: SUB}}>{['5.19%', '5.24%', '5.29%'][i]}</span>
        </Card>
      ))}
    </Phone>
  );
};

// ---------- SCR-Approved (2s) ----------
export const ScrApproved: React.FC = () => {
  const f = useCurrentFrame();
  const bloom = interpolate(f, [0, 18], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const word = usePop(10);
  return (
    <AbsoluteFill style={{background: BG, fontFamily: POPPINS, color: INK}}>
      <AbsoluteFill style={{background: `radial-gradient(${40 + bloom * 70}% ${30 + bloom * 50}% at 50% 42%, ${C.orange}, #FF9B6E 55%, ${BG} 100%)`}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', gap: 40, paddingBottom: 200}}>
        <div style={{transform: `scale(${word})`}}><Mark size={200} /></div>
        <div style={{fontWeight: 700, fontSize: 168, letterSpacing: -5, color: '#fff', transform: `scale(${0.9 + word * 0.1})`, opacity: word}}>Approved.</div>
      </AbsoluteFill>
      <div style={{position: 'absolute', left: 64, right: 64, bottom: 110, opacity: useIn(24)}}>
        <Card style={{display: 'flex', flexDirection: 'column', gap: 18}}>
          <div style={{display: 'flex', justifyContent: 'space-between', fontSize: 42, fontWeight: 600}}><span>Kōwhai Bank</span><span>5.19% · 2 yr</span></div>
          <div style={{fontFamily: MONO, fontSize: 30, color: SUB, letterSpacing: 2}}>DECISION IN 23 HRS 38 MIN</div>
        </Card>
      </div>
    </AbsoluteFill>
  );
};

// ---------- SCR-Market · marketplace + cashback (3s) ----------
export const ScrMarket: React.FC = () => {
  const f = useCurrentFrame();
  const toast = usePop(46);
  const items: [string, string, string][] = [['Sofa · Sage', '$2,699', '#A9B7A0'], ['Oak dining', '$1,349', '#C9A27E'], ['Linen bed', '$1,899', '#E6DDD3']];
  return (
    <Phone title="late">
      <div style={{fontWeight: 700, fontSize: 80, lineHeight: 1.02, letterSpacing: -2}}>Welcome home.</div>
      <Card o={useIn(4)} style={{background: C.orange, color: '#fff', border: 'none'}}>
        <Eyebrow color="rgba(255,255,255,.8)">Homely marketplace</Eyebrow>
        <div style={{fontWeight: 700, fontSize: 64, lineHeight: 1.1}}>10% off furniture</div>
      </Card>
      <div style={{display: 'flex', gap: 22}}>
        {items.map(([n, p, c], i) => (
          <Card key={n} o={useIn(12 + i * 5)} style={{flex: 1, padding: 24}}>
            <div style={{height: 200, borderRadius: 26, background: c}} />
            <div style={{fontSize: 30, fontWeight: 600, marginTop: 16}}>{n}</div>
            <div style={{fontFamily: MONO, fontSize: 26, color: SUB}}>{p}</div>
          </Card>
        ))}
      </div>
      <div style={{position: 'absolute', left: -10, right: -10, bottom: 40, transform: `translateY(${(1 - toast) * 260}px)`, opacity: toast}}>
        <Card style={{display: 'flex', alignItems: 'center', gap: 28, background: INK, color: '#fff', border: 'none'}}>
          <div style={{width: 96, height: 96, borderRadius: 30, background: C.orange, display: 'grid', placeItems: 'center', fontWeight: 700, fontSize: 52}}>$</div>
          <div><div style={{fontWeight: 700, fontSize: 56}}>+$2,500 cashback</div><div style={{fontSize: 32, opacity: 0.7}}>Your Homely reward. Spend it on the couch.</div></div>
        </Card>
      </div>
      {f < 0 ? null : null}
    </Phone>
  );
};

// ---------- SCR-Ticket · lender CRM on a tablet (landscape, 1.5s) ----------
export const ScrTicket: React.FC = () => {
  const f = useCurrentFrame();
  const rows: [string, string][] = [['Identity', 'Verified'], ['Income', 'Verified via Open Finance'], ['Expenses', 'Categorised · 12 months'], ['Documents', '12 / 12'], ['Homely profile score', '92']];
  const scan = interpolate(f, [0, 40], [0, rows.length], clamp);
  return (
    <AbsoluteFill style={{background: '#F3F5F8', fontFamily: POPPINS, color: '#16202B'}}>
      <div style={{height: 90, background: '#1B2A3A', color: '#fff', display: 'flex', alignItems: 'center', padding: '0 48px', gap: 30, fontSize: 30}}>
        <span style={{fontWeight: 700}}>Lender CRM</span><span style={{opacity: 0.55}}>Loan tickets</span>
        <span style={{marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 12, background: 'rgba(255,255,255,.1)', padding: '8px 18px', borderRadius: 30}}>
          <Mark size={34} color={C.orange} /><span style={{fontSize: 24}}>Connected to Homely</span>
        </span>
      </div>
      <div style={{padding: 48, display: 'flex', gap: 40}}>
        <div style={{flex: 1.4, background: '#fff', borderRadius: 24, padding: 40, boxShadow: '0 6px 24px rgba(20,40,60,.06)'}}>
          <div style={{fontFamily: MONO, fontSize: 24, color: '#6B7A8C', letterSpacing: 2}}>TICKET HL-4821 · FROM HOMELY</div>
          <div style={{fontWeight: 700, fontSize: 52, margin: '10px 0 26px'}}>A. Ngata & J. Reid</div>
          {rows.map(([k, v], i) => (
            <div key={k} style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '18px 0', borderTop: '2px solid #EEF1F5', fontSize: 30, opacity: scan > i ? 1 : 0.25}}>
              <span style={{color: '#56657A'}}>{k}</span>
              <span style={{display: 'flex', alignItems: 'center', gap: 14, fontWeight: 600}}>{v}<span style={{width: 28, height: 28, borderRadius: '50%', background: scan > i + 0.5 ? '#2FA56B' : '#D9DFE7'}} /></span>
            </div>
          ))}
        </div>
        <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 30}}>
          <div style={{background: '#fff', borderRadius: 24, padding: 36}}>
            <div style={{fontFamily: MONO, fontSize: 22, color: '#6B7A8C', letterSpacing: 2}}>REQUESTED</div>
            <div style={{fontWeight: 700, fontSize: 64}}>$790,000</div>
            <div style={{fontSize: 26, color: '#56657A'}}>Grey Lynn · 2-yr fixed</div>
          </div>
          <div style={{background: '#2FA56B', color: '#fff', borderRadius: 24, padding: 32, fontWeight: 700, fontSize: 38, textAlign: 'center', opacity: interpolate(f, [34, 42], [0.3, 1], clamp)}}>Ready for decision</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- SCR-Directory · lobby screen (landscape, 2s) ----------
export const ScrDirectory: React.FC = () => {
  const rows: [string, string, boolean][] = [['27', 'Harbour Legal', false], ['24', 'Home Lending · 9:00 · A. Ngata & J. Reid', true], ['19', 'Tidewater Architects', false], ['12', 'Kōwhai Bank', false], ['09', 'Southern Mutual', false]];
  return (
    <AbsoluteFill style={{background: '#101418', color: '#E9EEF2', fontFamily: POPPINS, padding: '80px 100px', gap: 10}}>
      <div style={{fontFamily: MONO, fontSize: 30, letterSpacing: 6, color: '#7F8C96', marginBottom: 30}}>DIRECTORY · 88 SHORTLAND ST</div>
      {rows.map(([l, n, hot]) => (
        <div key={l} style={{display: 'flex', gap: 60, alignItems: 'center', padding: '26px 30px', borderRadius: 14, background: hot ? 'rgba(255,107,61,.16)' : 'transparent', borderLeft: hot ? `8px solid ${C.orange}` : '8px solid transparent'}}>
          <span style={{fontFamily: MONO, fontSize: 64, color: hot ? C.orange : '#7F8C96', width: 110}}>{l}</span>
          <span style={{fontSize: 52, fontWeight: hot ? 600 : 400}}>{n}</span>
        </div>
      ))}
    </AbsoluteFill>
  );
};

// ---------- LED floor display (alpha) ----------
export const Led: React.FC<{from: number; to: number; transparent?: boolean}> = ({from, to, transparent}) => {
  const f = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const floor = Math.round(interpolate(f, [0, Math.max(1, durationInFrames - 8)], [from, to], {...clamp, easing: Easing.inOut(Easing.quad)}));
  const blink = from !== to && f % 10 < 6;
  return (
    <AbsoluteFill style={{background: transparent ? 'transparent' : '#050505', alignItems: 'center', justifyContent: 'center'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 34, fontFamily: MONO, fontWeight: 500, color: '#FFB347', textShadow: '0 0 18px rgba(255,160,60,.9), 0 0 4px #FFD08A'}}>
        <svg width="70" height="80" viewBox="0 0 24 28" style={{opacity: blink || from === to ? 1 : 0.35, filter: 'drop-shadow(0 0 8px rgba(255,160,60,.9))'}}><path d="M12 2 L22 14 H15 V26 H9 V14 H2 Z" fill="#FFB347" /></svg>
        <span style={{fontSize: 190, letterSpacing: 6, fontVariantNumeric: 'tabular-nums', minWidth: 240, textAlign: 'right'}}>{floor}</span>
      </div>
    </AbsoluteFill>
  );
};

// ---------- End card (landscape, 4s) ----------
export const EndCard: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const logo = spring({frame: f - 22, fps, config: {damping: 16, stiffness: 90}});
  const l1 = interpolate(f, [4, 16], [0, 1], clamp);
  const l1out = interpolate(f, [34, 42], [1, 0], clamp);
  const l3 = interpolate(f, [60, 74], [0, 1], clamp);
  return (
    <AbsoluteFill style={{background: C.orange, fontFamily: POPPINS, color: '#fff', alignItems: 'center', justifyContent: 'center'}}>
      <div style={{position: 'absolute', fontWeight: 600, fontSize: 84, letterSpacing: -1.5, opacity: Math.min(l1, l1out), transform: `translateY(${(1 - l1) * 20}px)`}}>Approved before the doors open.</div>
      <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24, opacity: logo, transform: `scale(${0.92 + logo * 0.08})`}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 26, fontWeight: 700, fontStyle: 'italic', fontSize: 170, letterSpacing: -3}}>Homely<Mark size={180} /></div>
        <div style={{fontWeight: 600, fontSize: 56, color: C.cream}}>Going up.</div>
      </div>
      <div style={{position: 'absolute', bottom: 70, fontFamily: MONO, fontSize: 24, letterSpacing: 4, opacity: l3, color: 'rgba(255,255,255,.85)'}}>THE FUTURE OF HOME LENDING · 2027 · CONCEPT FILM</div>
    </AbsoluteFill>
  );
};
