# UI Reverse Engineering Prompt Standard 2026-03-18

## 1. Purpose

This document formalizes the UI reverse-engineering approach you described and turns it into a reusable AITOS design standard.

This is valuable because it changes UI generation from:
- "generate a pretty page"

into:
- "extract the visual system first, then implement intentionally"

That is exactly how AITOS should avoid generic AI-made UI.

## 2. Core Idea

Before generating a UI, the system should first reverse-engineer the target visual language.

The analysis should extract:
- color palette
- typography scale
- spacing system
- border radius rules
- shadows/elevation
- motion behavior
- brand personality

Only after that should Lumi generate:
- design tokens
- Tailwind configuration
- component styles
- layout direction

## 3. Why This Is Important For AITOS

AITOS is not trying to produce average frontend work.

Your stated standard is:
- enterprise-grade system quality
- high-end UI taste
- no default AI plasticity

This reverse-engineering method helps because it forces the model to:
- analyze before generating
- identify system-level patterns
- avoid generic component stacking
- ground implementation in a coherent visual language

## 4. Recommended Standard Analysis Fields

Every UI reverse-engineering run should produce these sections:

## 4.1 Color Palette

Extract:
- primary
- secondary
- accent
- neutral
- semantic colors

Output:
- named colors
- hex values
- intended usage

## 4.2 Typography Scale

Extract:
- font family
- heading levels
- body sizes
- line height
- font weight
- letter spacing

Output:
- structured text scale
- likely type hierarchy intent

## 4.3 Spacing System

Extract:
- likely base unit
- common gap/padding values
- macro vs micro spacing rhythm

Output:
- spacing ladder
- likely layout rhythm

## 4.4 Border Radius

Extract:
- small element radius
- medium element radius
- large surface radius
- consistency patterns

## 4.5 Shadow / Elevation

Extract:
- shadow levels
- blur/spread assumptions
- where shadow is used vs avoided

## 4.6 Motion

Extract:
- transition durations
- easing curves
- interaction patterns
- reveal patterns
- hover/press/entry behavior

## 4.7 Brand Personality

Extract:
- 3-5 descriptive keywords
- the visual elements that support those keywords

This is important because implementation should preserve feeling, not only tokens.

## 5. Recommended AITOS Workflow Integration

## 5.1 Lara's role

Lara should:
- choose or approve reference direction
- determine whether the requested UI should:
  - match an existing brand
  - create a new direction
  - borrow a partial reference language

## 5.2 Lumi's role

Lumi should:
- run the reverse-engineering analysis
- convert the analysis into design tokens
- generate Tailwind theme outputs
- produce implementation notes before components

## 5.3 Pixel's role

Pixel should:
- critique visual consistency
- check whether final implementation still matches extracted personality and rhythm

## 6. Recommended Artifact Outputs

A strong run should generate:

1. `design_audit.md`
- extracted design system summary

2. `design_tokens.json`
- normalized tokens

3. `tailwind_theme.ts` or token mapping
- implementation-ready theme extension

4. `ui_direction.md`
- layout, motion, and component usage rules

## 7. How This Improves Tailwind Output

Without reverse engineering, Tailwind output usually fails in predictable ways:
- too many identical cards
- generic radius and shadow patterns
- no typographic hierarchy
- over-reliance on utility defaults
- weak emotional tone

With reverse engineering, Tailwind output becomes:
- token-led
- hierarchy-led
- brand-aware
- less repetitive
- more intentional

## 8. Main Design Trap To Avoid

The single biggest trap is:

`using components as a substitute for design thinking`

In practice this means:
- wrapping every section in the same card
- using the same radius everywhere
- treating spacing as a repetitive utility habit
- generating UI from component memory instead of visual logic

AITOS should instead prioritize:
- hierarchy
- rhythm
- tonal separation
- editorial flow
- intentional motion

## 9. Recommended Prompt Pattern

The prompt structure you shared is strong and should become a reusable internal standard.

Recommended operating flow:

1. reference URL
2. reverse-engineering analysis
3. token extraction
4. implementation constraints
5. React/Tailwind generation

This means the prompt should not jump directly from:
- reference

to:
- final code

It should go through:
- analysis
- tokenization
- implementation

## 10. Future AITOS Skill Expansion

This should become a formal skill for Lumi.

Suggested future skill name:
- `visual-reverse-engineering`

Suggested inputs:
- reference URL
- brand goal
- target page type

Suggested outputs:
- color palette
- type scale
- spacing system
- token map
- Tailwind theme config
- component rules

## 11. Best Inspiration Sources Mentioned

These are useful as discovery pools:
- Awwwards
- Site Inspire
- Dribbble
- Best Website Gallery
- Behance UI/UX
- Admire The Web
- muuuuu.org

Suggested usage:
- do not copy layouts literally
- use them to identify recurring token systems and personality directions

## 12. Recommended AITOS Quality Gate

Before accepting generated frontend work, check:

1. Is there a clear token system?
2. Is there visible type hierarchy?
3. Is spacing consistent and intentional?
4. Are containers used selectively rather than everywhere?
5. Does the final UI match the intended brand personality?
6. Are motion and transitions purposeful rather than generic?

If not, the UI is not ready.

## 13. Bottom Line

This reverse-engineering method is worth adopting as a standard.

It improves AITOS because it makes UI generation:
- more systematic
- more brand-aware
- less generic
- easier to critique
- easier to scale into a real design system

For AITOS, the right rule is:
- do not generate UI from vibes alone
- extract the visual system first, then build
