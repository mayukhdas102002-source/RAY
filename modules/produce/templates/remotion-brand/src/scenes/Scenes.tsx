import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Video} from '@remotion/media';
import {BRAND, fontStack} from '../brand';
import {useEntrance, useExit, useLayout} from '../layout';
import type {Scene} from '../timeline';
import {EndCard} from './EndCard';

const C = BRAND.colors;

// One focal point per frame. Every scene: entrance on the way in, a short fade at the tail.

const Stage: React.FC<{children: React.ReactNode; align?: 'center' | 'left'; bg?: string}> = ({
  children,
  align = 'left',
  bg = C.bg,
}) => {
  const {pad} = useLayout();
  const exit = useExit();
  return (
    <AbsoluteFill style={{backgroundColor: bg}}>
      <AbsoluteFill
        style={{
          paddingLeft: pad.left,
          paddingRight: pad.right,
          paddingTop: pad.top,
          paddingBottom: pad.bottom,
          justifyContent: 'center',
          alignItems: align === 'center' ? 'center' : 'flex-start',
          textAlign: align,
          opacity: exit,
        }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Rise: React.FC<{delay?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({
  delay = 0,
  children,
  style,
}) => {
  const e = useEntrance(delay);
  return <div style={{opacity: e.opacity, translate: `0 ${e.translateY}px`, ...style}}>{children}</div>;
};

const Kicker: React.FC<{text?: string; delay?: number}> = ({text, delay = 0}) => {
  const {type} = useLayout();
  if (!text) return null;
  return (
    <Rise delay={delay}>
      <div
        style={{
          fontFamily: fontStack('mono'),
          fontWeight: BRAND.fonts.mono.weight,
          fontSize: type.kicker,
          letterSpacing: '0.18em',
          textTransform: 'uppercase',
          color: C.accent,
          marginBottom: type.kicker * 0.8,
        }}
      >
        {text}
      </div>
    </Rise>
  );
};

const Headline: React.FC<{text?: string; size?: number; delay?: number; color?: string}> = ({
  text,
  size,
  delay = 0,
  color = C.fg,
}) => {
  const {type} = useLayout();
  if (!text) return null;
  return (
    <Rise delay={delay}>
      <div
        style={{
          fontFamily: fontStack('heading'),
          fontWeight: BRAND.fonts.heading.weight,
          fontSize: size ?? type.headline,
          lineHeight: 1.05,
          letterSpacing: '-0.02em',
          color,
          maxWidth: '18ch',
        }}
      >
        {text}
      </div>
    </Rise>
  );
};

const Body: React.FC<{text?: string; delay?: number}> = ({text, delay = 0}) => {
  const {type} = useLayout();
  if (!text) return null;
  return (
    <Rise delay={delay}>
      <div
        style={{
          fontFamily: fontStack('body'),
          fontWeight: BRAND.fonts.body.weight,
          fontSize: type.body,
          lineHeight: 1.3,
          color: C.muted,
          marginTop: type.body * 0.7,
          maxWidth: '28ch',
        }}
      >
        {text}
      </div>
    </Rise>
  );
};

const AccentBar: React.FC<{delay?: number}> = ({delay = 0}) => {
  const {u} = useLayout();
  const e = useEntrance(delay);
  return (
    <div
      style={{
        width: 140 * u * e.progress,
        height: 10 * u,
        borderRadius: 10 * u,
        backgroundColor: C.primary,
        marginBottom: 36 * u,
      }}
    />
  );
};

const TitleScene: React.FC<{scene: Scene}> = ({scene}) => {
  const {type} = useLayout();
  return (
    <Stage align="center">
      <Kicker text={scene.kicker} />
      <Headline text={scene.headline} size={type.hero} delay={BRAND.motion.stagger} />
      <Body text={scene.body} delay={BRAND.motion.stagger * 2} />
    </Stage>
  );
};

const StatementScene: React.FC<{scene: Scene}> = ({scene}) => (
  <Stage>
    <AccentBar />
    <Kicker text={scene.kicker} delay={BRAND.motion.stagger * 0.5} />
    <Headline text={scene.headline} delay={BRAND.motion.stagger} />
    <Body text={scene.body} delay={BRAND.motion.stagger * 2} />
  </Stage>
);

const StatScene: React.FC<{scene: Scene}> = ({scene}) => {
  const {type} = useLayout();
  return (
    <Stage>
      <Kicker text={scene.kicker} />
      <Rise>
        <div
          style={{
            fontFamily: fontStack('heading'),
            fontWeight: 800,
            fontSize: type.stat,
            lineHeight: 0.9,
            color: C.primary,
            letterSpacing: '-0.04em',
          }}
        >
          {scene.stat}
        </div>
      </Rise>
      <Headline text={scene.headline} delay={BRAND.motion.stagger} />
      <Body text={scene.body} delay={BRAND.motion.stagger * 2} />
    </Stage>
  );
};

const ListScene: React.FC<{scene: Scene}> = ({scene}) => {
  const {type, u} = useLayout();
  const items = scene.items ?? [];
  return (
    <Stage>
      <Headline text={scene.headline} />
      <div style={{marginTop: 48 * u, display: 'flex', flexDirection: 'column', gap: 28 * u}}>
        {items.map((item, i) => (
          <Rise key={item} delay={BRAND.motion.stagger * (i + 2)}>
            <div style={{display: 'flex', alignItems: 'center', gap: 28 * u}}>
              <div
                style={{
                  width: 64 * u,
                  height: 64 * u,
                  borderRadius: 64 * u,
                  backgroundColor: C.primary,
                  color: C.bg,
                  fontFamily: fontStack('mono'),
                  fontSize: 30 * u,
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                {i + 1}
              </div>
              <div
                style={{
                  fontFamily: fontStack('body'),
                  fontWeight: BRAND.fonts.body.weight,
                  fontSize: type.body * 1.1,
                  color: C.fg,
                }}
              >
                {item}
              </div>
            </div>
          </Rise>
        ))}
      </div>
    </Stage>
  );
};

const QuoteScene: React.FC<{scene: Scene}> = ({scene}) => {
  const {type} = useLayout();
  return (
    <Stage bg={C.surface}>
      <Rise>
        <div style={{fontFamily: fontStack('heading'), fontSize: type.hero * 1.4, color: C.primary, lineHeight: 0.6}}>
          “
        </div>
      </Rise>
      <Headline text={scene.headline} delay={BRAND.motion.stagger} />
      <Body text={scene.body} delay={BRAND.motion.stagger * 2} />
    </Stage>
  );
};

const Media: React.FC<{scene: Scene}> = ({scene}) => {
  const {fps} = useVideoConfig();
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  if (!scene.media) return <AbsoluteFill style={{backgroundColor: C.surface}} />;
  const isImage = /\.(png|jpe?g|webp|avif)$/i.test(scene.media);
  if (isImage) {
    // Gentle push-in. Note: a still with a push is not B-roll; use it for brand stills and keyframes only.
    const scale = interpolate(frame, [0, durationInFrames], [1.04, 1.12]);
    return (
      <AbsoluteFill style={{overflow: 'hidden'}}>
        <Img src={staticFile(scene.media)} style={{width: '100%', height: '100%', objectFit: 'cover', scale: String(scale)}} />
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill>
      <Video
        src={staticFile(scene.media)}
        muted
        objectFit="cover"
        trimBefore={Math.round((scene.mediaStart ?? 0) * fps)}
        style={{width: '100%', height: '100%'}}
      />
    </AbsoluteFill>
  );
};

const LowerThird: React.FC<{scene: Scene}> = ({scene}) => {
  const {pad, u, type, vertical} = useLayout();
  const e = useEntrance(0.3);
  const exit = useExit();
  if (!scene.name && !scene.headline) return null;
  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', paddingLeft: pad.left, paddingBottom: vertical ? pad.bottom : pad.bottom * 1.2}}>
      <div
        style={{
          opacity: e.opacity * exit,
          translate: `${interpolate(e.progress, [0, 1], [-40 * u, 0])}px 0`,
          backgroundColor: C.captionBox,
          borderLeft: `${10 * u}px solid ${C.primary}`,
          borderRadius: BRAND.radius * u * 0.5,
          padding: `${22 * u}px ${34 * u}px`,
          alignSelf: 'flex-start',
        }}
      >
        <div style={{fontFamily: fontStack('heading'), fontWeight: BRAND.fonts.heading.weight, fontSize: type.body * 1.05, color: C.fg}}>
          {scene.name ?? scene.headline}
        </div>
        {scene.role || scene.body ? (
          <div style={{fontFamily: fontStack('body'), fontSize: type.body * 0.7, color: C.muted, marginTop: 6 * u}}>
            {scene.role ?? scene.body}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

export const SceneView: React.FC<{scene: Scene}> = ({scene}) => {
  switch (scene.kind) {
    case 'title':
      return <TitleScene scene={scene} />;
    case 'statement':
      return <StatementScene scene={scene} />;
    case 'stat':
      return <StatScene scene={scene} />;
    case 'list':
      return <ListScene scene={scene} />;
    case 'quote':
      return <QuoteScene scene={scene} />;
    case 'footage':
    case 'image':
      return <Media scene={scene} />;
    case 'lowerThird':
      return (
        <>
          <Media scene={scene} />
          <LowerThird scene={scene} />
        </>
      );
    case 'endCard':
      return <EndCard />;
    default:
      return <StatementScene scene={scene} />;
  }
};
