---
version: alpha
name: Study Bright
description: Friendly ed-tech brightness in the spirit of Ellii — indigo action on paper whites, sunny CTA yellow, rounded everything.
colors:
  primary: "#425FE6"
  primary-soft: "#5774FC"
  primary-pale: "#C7D1FE"
  canvas: "#F3F5FD"
  card: "#FFFFFF"
  card-hover: "#EEF1FD"
  border: "#E2E7F5"
  ink: "#241D1F"
  muted: "#5E6D88"
  success: "#1FAA6E"
  cta: "#FED502"
  danger: "#E5484D"
  purple: "#8152E9"
  primary-ink: "#3449B8"
  success-ink: "#0F7A4D"
  purple-ink: "#5B3FD1"
  warning: "#D29922"
  star: "#E6A700"
  level-b1: "#D29922"
  level-b2: "#F0883E"
  level-b3: "#E5484D"
  easy-green: "#7EE787"
typography:
  display:
    fontFamily: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
    fontSize: 2.1rem
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  h1:
    fontFamily: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
    fontSize: 1.4rem
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  h2:
    fontFamily: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
    fontSize: 1.15rem
    fontWeight: 700
    lineHeight: 1.3
  body-md:
    fontFamily: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
    fontSize: 1rem
    fontWeight: 600
    lineHeight: 1.5
  body-sm:
    fontFamily: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
    fontSize: 0.85rem
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
    fontSize: 0.72rem
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0.05em"
rounded:
  sm: 8px
  md: 10px
  lg: 12px
  xl: 16px
  pill: 20px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 20px
  xxl: 24px
elevation:
  card: 0 4px 20px rgba(35,31,32,0.08)
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.md}"
    padding: 10px
  button-cta:
    backgroundColor: "{colors.cta}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: 10px
  button-quiz:
    backgroundColor: "{colors.card}"
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    padding: 10px
  word-definition:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
  word-muted-note:
    backgroundColor: "{colors.card}"
    textColor: "{colors.muted}"
    typography: "{typography.body-sm}"
  badge-sat:
    backgroundColor: "{colors.primary-pale}"
    textColor: "{colors.primary-ink}"
    rounded: "{rounded.pill}"
  badge-ielts:
    backgroundColor: "{colors.card-hover}"
    textColor: "{colors.success-ink}"
    rounded: "{rounded.pill}"
  badge-both:
    backgroundColor: "{colors.card-hover}"
    textColor: "{colors.purple-ink}"
    rounded: "{rounded.pill}"
  page-title:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.primary}"
    typography: "{typography.h1}"
---

## Overview

Study Bright is a friendly ed-tech identity for a SAT/IELTS vocabulary
trainer: indigo drives every interaction, sunny yellow marks the single
most important action per screen, and paper-white cards with big radii
keep 5000 words feeling light. Dark surfaces are never used in the
default theme; depth comes from one soft shadow, never borders alone.

## Colors

- **Primary (#425FE6):** Ellii-sampled indigo. Buttons, links, active states, chart lines.
- **Primary-soft (#5774FC):** Gradient partner for primary buttons.
- **Primary-pale (#C7D1FE):** Tint fills behind active cards and SAT badges.
- **Canvas (#F3F5FD):** Page base under a fixed full-bleed SVG of four
  Ellii-style wave bands — indigo and purple rolling down from the top,
  yellow and green rising from the bottom, all in token hues.
- **Ink (#241D1F):** Warm near-black for all body text.
- **Muted (#5E6D88):** Secondary text, labels, placeholders. Darkened
  from sketch value until it passes AA on white (5.2:1).
- **Ink text on tints:** badge text uses `primary-ink`, `success-ink`,
  `purple-ink` — darker siblings tuned to pass AA on their tint fills.
- **Success (#1FAA6E):** Completion, correct answers, IELTS accents.
- **CTA (#FED502):** Sunny yellow, reserved for the one Continue action.
- **Danger (#E5484D):** Wrong answers, destructive actions.
- **Purple (#8152E9):** Shared/Both category, timer gradient partner.
- **Star (#E6A700):** Mastered-word gold.
- **Level colors:** B1 amber (#D29922), B2 orange (#F0883E), C1 red (#E5484D),
  with soft green (#7EE787) reserved for sub-B1 states if they return.

## Typography

One system stack everywhere. Display (flashcard words) is the only
extra-bold, tight-tracked voice. Labels are small, semibold, wide-tracked
uppercase. Never set body copy in Muted — contrast budget is spent on
large interactive text instead.

## Layout

Content column max 1200px, dashboard grid auto-fits 200px tiles, word
grid auto-fills 250px cards. Single-flashcard pager caps at 780px so one
card owns the screen. Sidebar (notes + progress) sticks as one unit.

## Elevation & Depth

One shadow (`elevation.card`) for resting cards. Hover lifts flashcard
fronts with an accent border rather than a bigger shadow. Timer track has
a shallow inset shadow; nothing else is inset.

## Shapes

16px card radius, 8–12px controls, 20px pills for level badges and SAT
tags. Donut rings use round line caps. Timer is a fully round bar.

## Components

`button-primary` is the high-emphasis action (white on indigo gradient).
`button-cta` is the single sunny Continue per screen (ink on yellow).
`button-quiz` is the secondary outline style shared by Quiz, Timed,
Review, Shuffle and navigation buttons. Badges are tint fills, never
outlines. `word-definition` sets the contrast contract: ink on white.

## Do's and Don'ts

- Do keep exactly one yellow CTA visible per screen.
- Do use Star gold only for mastered state.
- Don't put Muted text on tinted fills — check contrast first.
- Don't invent new accent hues; the palette is closed at these tokens.
- Don't nest component variants; add `*-hover` siblings if needed.

## Dark Theme

Same token names, midnight values: canvas `#14162A`, card `#1F2340`,
ink `#F2F3FA`, primary lifted to `#7C93FF` so interaction stays AA on
dark fills. Badges revert to bright token text on dark tints. The page
switches via `[data-theme="dark"]` overrides; charts read the same
choice in JS. Spec above stays normative for light.
