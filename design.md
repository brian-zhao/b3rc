# B3RC Design Document

**Based on:** [DSM-Firmenich Running Team](https://www.dsm-firmenichrunningteam.com/)
**Date:** 2026-03-21

---

## 1. Design Philosophy

The design follows a **performance-driven, editorial aesthetic** — clean, minimal, and athletic. It communicates ambition, dedication, and elite-level professionalism through generous whitespace, bold typography, and high-impact photography. The overall feel is modern corporate-sport: serious but aspirational.

---

## 2. Layout & Grid System

### Structure
- **Max content width:** ~1200px, centered
- **Grid:** CSS Grid / Flexbox hybrid
  - Content cards: 2-column grid on desktop, single column on mobile
  - Sponsor logos: multi-column grid (4-6 across)
- **Spacing rhythm:** Consistent vertical spacing between sections (~60-80px desktop, ~40px mobile)
- **Approach:** Mobile-first responsive design

### Page Sections (top to bottom)
1. Sticky/fixed top navigation bar
2. Hero section (full-width image)
3. News/press release cards
4. Upcoming events list
5. Featured content blocks (alternating image + text)
6. Newsletter signup CTA
7. Sponsor logo grid
8. Footer with social links + legal

---

## 3. Color Palette

| Role             | Color             | Hex (approx)  | Usage                              |
|------------------|-------------------|---------------|------------------------------------|
| Primary          | Deep Teal/Blue    | `#003D4C`     | Nav, headings, primary buttons     |
| Secondary        | Dark Navy         | `#001A2B`     | Footer background, text overlays   |
| Accent           | Vibrant Green     | `#00A550`     | CTAs, highlights, hover states     |
| Background       | White             | `#FFFFFF`     | Main content background            |
| Surface          | Light Gray        | `#F5F5F5`     | Alternating section backgrounds    |
| Text Primary     | Near Black        | `#1A1A1A`     | Body copy                          |
| Text Secondary   | Medium Gray       | `#6B6B6B`     | Dates, captions, meta text         |
| Border/Divider   | Subtle Gray       | `#E0E0E0`     | Card borders, section dividers     |

---

## 4. Typography

### Font Stack
- **Headings:** Sans-serif grotesque (e.g., `"DSM Sans"`, fallback: `"Helvetica Neue", Arial, sans-serif`)
- **Body:** Clean sans-serif, same family at lighter weight

### Scale

| Element             | Size (desktop) | Weight | Line Height | Transform     |
|---------------------|---------------|--------|-------------|---------------|
| Hero Headline       | 48-56px       | 700    | 1.1         | Uppercase     |
| Section Heading     | 32-36px       | 700    | 1.2         | None          |
| Card Title          | 20-24px       | 600    | 1.3         | None          |
| Body Copy           | 16px          | 400    | 1.6         | None          |
| Meta/Date           | 13-14px       | 400    | 1.4         | Uppercase     |
| Nav Links           | 14-16px       | 500    | 1.0         | Uppercase     |
| Button Text         | 14px          | 600    | 1.0         | Uppercase     |

---

## 5. Navigation

### Top Bar
- **Position:** Sticky top, full-width
- **Background:** White with subtle bottom border or shadow on scroll
- **Height:** ~64-72px
- **Layout:** Logo (left) | Nav links (center/right) | External link icon for "Shop"
- **Links:** `Team` | `Events` | `News` | `About` | `Shop`
- **Mobile:** Hamburger menu icon, slide-in drawer

### Behavior
- Logo has primary (dark) and secondary (light) variants for use on different backgrounds
- Active page link indicated with underline or weight change
- Hover state: color shift or underline animation

---

## 6. Hero Section

- **Layout:** Full-width, edge-to-edge image
- **Height:** ~70-80vh on desktop, ~50vh on mobile
- **Image:** High-contrast, cinematic athletic photography
- **Overlay:** Optional dark gradient from bottom for text readability
- **Text placement:** Bottom-left, large headline + subtitle
- **CTA button:** Optional, positioned below headline

---

## 7. Content Cards (News/Press)

### Card Anatomy
```
+----------------------------------+
|        [Image - 16:9]            |
+----------------------------------+
| PRESS RELEASE | 13 MAR           |  <- meta line (uppercase, gray, small)
| Card Headline Title Here         |  <- title (bold, 20-24px)
| Brief excerpt text if present... |  <- body (regular, 16px, gray)
+----------------------------------+
```

### Specs
- **Image aspect ratio:** 16:9
- **Border radius:** 0px (sharp edges) or subtle 4px
- **Shadow:** None or very subtle (`0 2px 8px rgba(0,0,0,0.06)`)
- **Hover state:** Slight image zoom (scale 1.02-1.05), transition 0.3s ease
- **Gap between cards:** 24-32px

---

## 8. Events Section

- **Style:** Minimal list layout, no cards
- **Each row:** Event name + date + location
- **Separator:** Thin horizontal line between entries
- **Typography:** Event name in bold, details in regular weight
- **Global locations:** Marathons across international venues
- **Hover:** Subtle background highlight on row

---

## 9. Featured Content Blocks

### Layout Pattern
Alternating left-right arrangement:
```
Block 1:  [Image]  |  [Text + CTA]
Block 2:  [Text + CTA]  |  [Image]
Block 3:  [Image]  |  [Text + CTA]
```

- **Image:** ~50% width, full section height
- **Text side:** Vertically centered heading + paragraph + button
- **Background:** Alternates between white and light gray

---

## 10. Buttons & CTAs

### Primary Button
- **Background:** Primary teal/blue (`#003D4C`)
- **Text:** White, uppercase, 14px, font-weight 600
- **Padding:** 12px 32px
- **Border radius:** 0px (sharp/geometric) or 4px
- **Hover:** Darken background 10%, or shift to accent green
- **Transition:** `background-color 0.2s ease`

### Secondary / Ghost Button
- **Background:** Transparent
- **Border:** 2px solid primary color
- **Text:** Primary color, uppercase
- **Hover:** Fill with primary color, text turns white

### Text Link / Arrow CTA
- **Style:** Inline text with right arrow (`->`)
- **Hover:** Underline or arrow nudges right

---

## 11. Newsletter Signup

- **Layout:** Centered block, full-width background (light gray or dark)
- **Heading:** "Stay up to date" or similar (h4)
- **Input:** Email field + submit button inline
- **Input style:** Clean border, large padding, no rounded corners
- **Button:** Primary style, attached to input or below on mobile

---

## 12. Sponsor Logo Grid

- **Layout:** Horizontal row or grid, 4-6 logos per row
- **Logo treatment:** Monochrome/grayscale for visual consistency
- **Hover:** Optional color reveal on hover
- **Spacing:** Even distribution with generous padding
- **Sponsors include:** Nike, Huawei, Maurten, and others
- **Alignment:** Vertically centered logos of varying aspect ratios

---

## 13. Footer

### Structure
```
+----------------------------------------------+
|  Sponsor Logos (grid)                        |
+----------------------------------------------+
|  Social Icons: IG | FB | X | YT             |
+----------------------------------------------+
|  Legal links  |  Privacy  |  Copyright       |
+----------------------------------------------+
```

- **Background:** Dark (navy/near-black `#001A2B`)
- **Text color:** White/light gray
- **Social icons:** Minimal line icons, ~24px, hover brightens or adds color
- **Legal text:** Small (12-13px), muted gray
- **Padding:** Generous vertical padding (~40-60px)

---

## 14. Imagery Guidelines

- **Style:** High-performance athletic photography — runners in motion, race environments, training
- **Mood:** Aspirational, focused, powerful
- **Color grading:** Slightly desaturated with high contrast
- **Composition:** Dynamic angles, motion blur acceptable
- **People:** Diverse, elite-level athletes
- **Aspect ratios:** 16:9 for cards, flexible for hero/featured blocks

---

## 15. Motion & Interaction

| Element          | Interaction         | Animation                              |
|------------------|--------------------|-----------------------------------------|
| Nav bar          | Scroll             | Background opacity shift on scroll down |
| Card images      | Hover              | Scale 1.0 -> 1.05, 0.3s ease           |
| Buttons          | Hover              | Background color shift, 0.2s ease       |
| Page transitions | Route change       | Fade in, 0.3s                           |
| Scroll reveal    | Viewport entry     | Fade up + translate Y 20px, 0.5s ease   |
| Arrow CTAs       | Hover              | Arrow translates right 4px              |

---

## 16. Responsive Breakpoints

| Breakpoint | Width     | Behavior                                      |
|------------|-----------|-----------------------------------------------|
| Mobile     | < 768px   | Single column, hamburger nav, stacked blocks   |
| Tablet     | 768-1024px| 2-column cards, condensed nav                  |
| Desktop    | > 1024px  | Full layout, sticky nav, side-by-side blocks   |
| Wide       | > 1440px  | Content max-width capped, centered             |

---

## 17. Technical Notes

- **Performance:** Lazy-loaded images with timestamp cache-busting
- **Tracking:** Google Tag Manager integration
- **Security:** Cloudflare layer
- **SEO:** Semantic HTML structure with proper heading hierarchy
- **Accessibility:** SVG logos with alt variants, semantic nav landmarks
