# Design Palette Migration (Navy)

**Status:** Not started
**Priority:** High — foundational visual change that all future work builds on
**Date created:** 2026-03-21

---

## Goal

Migrate the site from its current black-and-white + purple overlay palette to the navy-driven design system defined in `design.md`, inspired by [DSM-Firmenich Running Team](https://www.dsm-firmenichrunningteam.com/). The result should feel editorial, athletic, and premium — not generic corporate.

---

## Current State → Target State

| Element | Current | Target |
|---------|---------|--------|
| Navbar background | `#000000` (black) | `#001A2B` (dark navy) |
| Navbar shadow | `rgba(45,16,96,0.2)` (purple) | `rgba(0,26,43,0.15)` (navy) |
| Nav link hover | `#f5eaff` (lavender) | `#00A550` (accent green) or white at 0.8 opacity |
| Body text color | `#000000` | `#1A1A1A` (near black) |
| Section titles | `#000000` | `#003D4C` (deep teal) |
| Card borders | `rgba(0,0,0,0.12)` | `#E0E0E0` or `rgba(0,61,76,0.12)` |
| Video overlay | `rgba(45,16,96,0.3)` (purple) | `rgba(0,26,43,0.4)` (navy) |
| Buttons (sponsors CTA) | `black` bg | `#003D4C` (primary teal) bg |
| Button hover | `opacity: 0.85` | Darken 10% or shift to `#00A550` (green) |
| Secondary text | `rgba(0,0,0,0.5-0.8)` | `#6B6B6B` for meta, `#1A1A1A` for body |
| Feature card headings | `#000000` | `#003D4C` |
| Logo | Current PNG (on black bg) | Needs light variant for navy bg — see materials below |

---

## Implementation Steps

### 1. CSS Custom Properties (set up tokens)
Add CSS variables to `:root` in `style.css` so palette changes are centralized:
```css
:root {
  --color-primary: #003D4C;
  --color-secondary: #001A2B;
  --color-accent: #00A550;
  --color-bg: #FFFFFF;
  --color-surface: #F5F5F5;
  --color-text: #1A1A1A;
  --color-text-secondary: #6B6B6B;
  --color-border: #E0E0E0;
}
```

### 2. Navbar migration
- Background: `var(--color-secondary)`
- Box-shadow: `0 2px 12px rgba(0,26,43,0.15)`
- Link hover color: `var(--color-accent)` or white with opacity

### 3. Typography color pass
- Replace all `#000000` text colors with `var(--color-text)` or `var(--color-primary)` for headings
- Replace `rgba(0,0,0,0.x)` secondary text with `var(--color-text-secondary)`

### 4. Hero overlay
- Change `rgba(45,16,96,0.3)` → `rgba(0,26,43,0.4)` (navy tint)

### 5. Card and component borders
- Replace `rgba(0,0,0,0.12)` → `var(--color-border)`

### 6. Buttons
- `.sponsors-contact-btn` background: `var(--color-primary)`
- Hover: background shifts to `var(--color-accent)` with `transition: background-color 0.2s ease`

### 7. Surface backgrounds
- Add `var(--color-surface)` to alternating sections where design.md calls for it (about features, CTA blocks)

### 8. Logo swap
- Replace `logo.png` with updated version(s) — see materials needed below

### 9. Verify and test
- Check all 5 pages visually
- Verify contrast ratios meet WCAG AA (especially white text on navy, teal text on white)
- Test at 768px breakpoint

---

## Materials Needed from the Team

### Required

| Material | Format | Specs | Why |
|----------|--------|-------|-----|
| **Logo (light version)** | SVG preferred, PNG fallback | White or light-colored variant, transparent background, min 160px wide @2x | Current logo sits on a black navbar. Navy background needs a logo that reads clearly against `#001A2B`. SVG scales cleanly across devices. |
| **Logo (dark version)** | SVG preferred, PNG fallback | Dark variant (teal `#003D4C` or navy `#001A2B`), transparent background | For use on white/light backgrounds (future footer, print, open graph image). |
| **Brand color sign-off** | Slack message or doc | Confirm or adjust the 3 core colors: primary `#003D4C`, secondary `#001A2B`, accent `#00A550` | These are approximations from the DSM-Firmenich reference. B3RC may want its own specific shades — need final approval before hardcoding. |

### Strongly Recommended

| Material | Format | Specs | Why |
|----------|--------|-------|-----|
| **Hero photo (still)** | JPG/WebP | Min 1920x1080, landscape, cinematic athletic photography | design.md calls for a full-width hero image option alongside the video. A strong still image loads faster and works as a fallback when video can't autoplay (low-power mode, slow connections). Should feature B3RC runners, Sydney locations, or race-day moments. |
| **Hero video (updated)** | MP4 (H.264) | 1080p, 10-20 seconds, loop-friendly, no audio needed | Current `background.mp4` works but the purple overlay it was graded for won't match the new navy palette. If the source footage has a cooler/neutral grade, a re-export would look sharper under the navy overlay. |
| **Favicon / app icon** | SVG + PNG (32x32, 180x180) | Simple mark from the B3RC logo, works at small sizes | Not currently in the project. Needed for browser tabs and mobile bookmarks. Should use the new brand palette. |

### Nice to Have (for upcoming features)

| Material | Format | Specs | Why |
|----------|--------|-------|-----|
| **Team member photos** | JPG/WebP | 4:5 portrait or 1:1 square, min 600px wide, consistent lighting/background | Needed when we build the Team page (listed in design.md nav: Team, Events, News, About). Athletic/training shots preferred over headshots — matches the editorial aesthetic. |
| **Event/race photos** | JPG/WebP | 16:9 landscape, min 800px wide | For the news/press cards and events section from design.md. Race-day photography from Sydney marathons, training at Concord/Rhodes, group runs. |
| **Sponsor logos** | SVG (vector) | Monochrome/single-color versions, transparent background | design.md specifies a grayscale sponsor grid. SVG ensures crisp rendering. Need monochrome variants — full-color logos won't match the editorial aesthetic. |
| **Social media handles** | Text list | Instagram, Facebook, Strava, YouTube URLs | For the dark footer with social links (design.md section 13). Need the actual profile URLs to link out. |
| **Newsletter platform** | Account/API details | Mailchimp, Buttondown, or similar | design.md includes a newsletter signup section. Need to know which platform (if any) the team uses or wants to use, so we can wire up the form. |
| **About page copy (expanded)** | Google Doc or plain text | Club history, coach bios, training philosophy, membership details | Current about page is solid but brief. Richer copy lets us build out the alternating featured content blocks from design.md (image + text, image + text). |
| **Open Graph image** | PNG/JPG | 1200x630, B3RC branding with navy background | For link previews when the site is shared on social media or messaging apps. Should use the new palette. |

---

## Delivery Notes

- **Drop files** into a shared Google Drive folder or send via Slack — whatever works for the team.
- **SVG is king.** Vector logos and icons scale perfectly and keep the site fast. If only raster (PNG/JPG) versions exist, provide the highest resolution available and we'll work with it.
- **Photography style:** Slightly desaturated with high contrast. Dynamic angles. Motion blur is fine. Think editorial sports magazine, not corporate stock photography.
- **Name files clearly:** `logo-light.svg`, `logo-dark.svg`, `hero-fallback.jpg`, `sponsor-nike-mono.svg`, etc.

---

## Definition of Done

- [ ] All `#000000` replaced with navy/teal design tokens
- [ ] Purple overlay eliminated — navy overlay in place
- [ ] CSS custom properties used throughout (no raw hex in component styles)
- [ ] Logo updated for navy navbar
- [ ] All 5 pages visually consistent under new palette
- [ ] WCAG AA contrast ratios pass on all text/background combos
- [ ] `collectstatic` run, no broken references
- [ ] Reviewed on desktop and mobile (768px breakpoint)
