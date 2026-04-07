# Brand Consistency Checklist

Use this checklist to validate any component or page against the design system.

## Token Usage

- [ ] All colors reference semantic tokens, not primitive values or hex codes
- [ ] All font sizes use the type scale tokens
- [ ] All spacing values use the spacing scale tokens
- [ ] All border-radius values use the radius scale tokens
- [ ] All shadows use the elevation tokens
- [ ] All transitions use the motion tokens (easing + duration)
- [ ] No hardcoded values found in component styles

## Accessibility

- [ ] All text meets WCAG AA contrast minimum (4.5:1 normal, 3:1 large)
- [ ] All interactive elements have visible focus states
- [ ] All form elements have associated labels
- [ ] Keyboard navigation works for all interactive elements
- [ ] prefers-reduced-motion is respected for all animations
- [ ] Color is never the only indicator of state (icons or text accompany it)

## Typography

- [ ] Cormorant Garamond used only for display/heading text
- [ ] IBM Plex Sans used for body and general content
- [ ] IBM Plex Mono used only for code and technical content
- [ ] Font weights match the type system rules
- [ ] Line heights follow the defined ratios

## Visual Identity

- [ ] Editorial command center metaphor is preserved (not generic SaaS)
- [ ] Warm earth tone palette is maintained (paper, ink, clay, ember, gold)
- [ ] Component follows atomic design hierarchy (atom/molecule/organism)
- [ ] Hover and interactive states follow motion token patterns
- [ ] Layout respects the defined grid system

## Brand Voice (UI Text)

- [ ] Microcopy follows UX writing guide tone
- [ ] Portuguese language is consistent
- [ ] Eyebrow labels use uppercase and gold accent
- [ ] CTAs are clear and action-oriented
- [ ] Empty states provide helpful guidance

## Responsive

- [ ] Component renders correctly at mobile breakpoint (< 640px)
- [ ] Component renders correctly at tablet breakpoint (640-1024px)
- [ ] Component renders correctly at desktop breakpoint (> 1024px)
- [ ] Typography scales appropriately across breakpoints
- [ ] Grid layout adapts without breaking visual hierarchy
