import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {BRAND, fontStack} from '../brand';
import {useEntrance, useLayout} from '../layout';

// End card: official logo file only (never redrawn or generated), tagline, CTA, optional legal line.
// No exit animation: the final frame holds.
export const EndCard: React.FC<{still?: boolean}> = ({still = false}) => {
  const {u, type, pad} = useLayout();
  const logo = useEntrance(still ? -10 : 0);
  const line = useEntrance(still ? -10 : BRAND.motion.stagger * 2);
  const cta = useEntrance(still ? -10 : BRAND.motion.stagger * 4);
  const C = BRAND.colors;
  const logoSrc = BRAND.logo.light; // light logo on the dark brand background
  return (
    <AbsoluteFill
      style={{
        backgroundColor: C.bg,
        justifyContent: 'center',
        alignItems: 'center',
        textAlign: 'center',
        paddingLeft: pad.left,
        paddingRight: pad.left,
      }}
    >
      <div style={{opacity: logo.opacity, scale: String(logo.scale)}}>
        {logoSrc ? (
          <Img src={staticFile(logoSrc)} style={{width: 420 * u, height: 'auto'}} />
        ) : (
          <div
            style={{
              fontFamily: fontStack('heading'),
              fontWeight: BRAND.fonts.heading.weight,
              fontSize: type.hero,
              color: C.fg,
              letterSpacing: '-0.03em',
            }}
          >
            {BRAND.name}
          </div>
        )}
      </div>
      <div
        style={{
          opacity: line.opacity,
          translate: `0 ${line.translateY}px`,
          fontFamily: fontStack('body'),
          fontWeight: BRAND.fonts.body.weight,
          fontSize: type.body,
          color: C.muted,
          marginTop: 36 * u,
        }}
      >
        {BRAND.tagline}
      </div>
      <div
        style={{
          opacity: cta.opacity,
          translate: `0 ${cta.translateY}px`,
          marginTop: 56 * u,
          padding: `${20 * u}px ${44 * u}px`,
          borderRadius: 999,
          backgroundColor: C.primary,
          color: C.bg,
          fontFamily: fontStack('heading'),
          fontWeight: BRAND.fonts.heading.weight,
          fontSize: type.body * 0.9,
        }}
      >
        {BRAND.endCard.cta} · {BRAND.endCard.url}
      </div>
      {BRAND.endCard.legal ? (
        <div
          style={{
            position: 'absolute',
            bottom: pad.bottom * 0.6,
            left: pad.left,
            right: pad.left,
            fontFamily: fontStack('body'),
            fontSize: 22 * u,
            color: C.muted,
            opacity: cta.opacity * 0.85,
          }}
        >
          {BRAND.endCard.legal}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
