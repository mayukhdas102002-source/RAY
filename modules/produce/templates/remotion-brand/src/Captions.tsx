import React, {useMemo} from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Caption, TikTokPage} from '@remotion/captions';
import {BRAND, fontStack} from './brand';
import {useLayout} from './layout';

// Word-timed caption pages. Input: Remotion Caption[] in ms on the master clock
// (scripts/captions_convert.py writes src/captions.json). Each word's text starts with a space.
// Rules: short phrase groups, hard swap (no pop), active word highlighted, one dark box, never over a face.

const Page: React.FC<{page: TikTokPage; offsetMs: number}> = ({page, offsetMs}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {type, pad, u, vertical} = useLayout();
  const nowMs = offsetMs + (frame / fps) * 1000; // master-clock ms
  const C = BRAND.colors;
  const pos = BRAND.captions.position;
  return (
    <AbsoluteFill
      style={{
        justifyContent: pos === 'top' ? 'flex-start' : pos === 'center' ? 'center' : 'flex-end',
        alignItems: 'center',
        paddingTop: pad.top,
        paddingBottom: vertical ? pad.bottom : pad.bottom * 0.9,
        paddingLeft: pad.left,
        paddingRight: pad.right,
      }}
    >
      <div
        style={{
          backgroundColor: BRAND.captions.box ? C.captionBox : 'transparent',
          border: BRAND.captions.box ? `${1.5 * u}px solid ${C.line}` : 'none',
          borderRadius: 16 * u,
          padding: `${14 * u}px ${26 * u}px`,
          fontFamily: fontStack('heading'),
          fontWeight: 800,
          fontSize: type.caption,
          lineHeight: 1.15,
          textAlign: 'center',
          textTransform: BRAND.captions.upper ? 'uppercase' : 'none',
          color: C.captionText,
          whiteSpace: 'pre-wrap',
          maxWidth: '100%',
        }}
      >
        {page.tokens.map((t) => {
          const active = t.fromMs <= nowMs && t.toMs > nowMs;
          return (
            <span key={`${t.fromMs}-${t.text}`} style={{color: active ? C.captionHighlight : C.captionText}}>
              {t.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// Phrase pages: break after sentence punctuation, on pauses, at scene ends (pageBreakAfter),
// at the brand's max page length, and at a word cap (3 on vertical, 6 on landscape).
const toPages = (captions: Caption[], maxWords: number, maxMs: number): TikTokPage[] => {
  const pages: TikTokPage[] = [];
  let cur: Caption[] = [];
  const flush = () => {
    if (!cur.length) return;
    pages.push({
      text: cur.map((c) => c.text).join('').trim(),
      startMs: cur[0].startMs,
      durationMs: cur[cur.length - 1].endMs - cur[0].startMs,
      tokens: cur.map((c, i) => ({text: i === 0 ? c.text.trimStart() : c.text, fromMs: c.startMs, toMs: c.endMs})),
    });
    cur = [];
  };
  captions.forEach((c, i) => {
    cur.push(c);
    const next = captions[i + 1];
    const endsSentence = /[.!?;:]$/.test(c.text.trim());
    const pause = next ? next.startMs - c.endMs > 600 : true;
    const long = next ? next.endMs - cur[0].startMs > maxMs : false;
    if (!next || endsSentence || pause || long || c.pageBreakAfter || cur.length >= maxWords) flush();
  });
  return pages;
};

export const Captions: React.FC<{captions: Caption[]}> = ({captions}) => {
  const {fps} = useVideoConfig();
  const {vertical} = useLayout();
  const pages = useMemo(
    () => toPages(captions, vertical ? 3 : 6, Math.max(BRAND.captions.combineMs, 1200)),
    [captions, vertical],
  );
  return (
    <>
      {pages.map((page, i) => {
        const next = pages[i + 1];
        // Appear 2 frames before the first word; hold until the next page (max 1.5 s past the last word).
        const from = Math.max(0, Math.round((page.startMs / 1000) * fps) - 2);
        const lastTo = page.startMs + page.durationMs;
        const endMs = next ? Math.min(next.startMs, lastTo + 1500) : lastTo + 600;
        const dur = Math.max(1, Math.round((endMs / 1000) * fps) - from - 2);
        return (
          <Sequence key={`${page.startMs}-${i}`} from={from} durationInFrames={dur} name={`cap ${page.text.slice(0, 20)}`}>
            <Page page={page} offsetMs={(from / fps) * 1000} />
          </Sequence>
        );
      })}
    </>
  );
};
