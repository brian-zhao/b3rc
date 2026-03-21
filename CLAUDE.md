# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project Identity

**B3RC — Breaking 3 Running Club.** A Sydney-based running community built around the pursuit of the sub-3-hour marathon. The site channels a performance-driven, editorial aesthetic inspired by [DSM-Firmenich Running Team](https://www.dsm-firmenichrunningteam.com/) — clean, minimal, athletic. Every design and code decision should reinforce ambition, dedication, and elite-level professionalism.

## Workflow

Before starting work, write a detailed implementation plan in `claude/tasks/TASK_NAME.md`. The plan should include a clear breakdown of implementation steps, the reasoning behind your approach, and a list of specific tasks. Focus on an MVP. Ask for review before proceeding — do not implement until the plan is approved.

As you work, keep the plan updated. After completing each task, append a description of the changes made.

## Architecture

| Layer | Detail |
|-------|--------|
| Framework | Django 5.2+ (Python 3.12) |
| Structure | Single-project, no separate Django apps — all views and URL routing live in `b3rc_site/` |
| Database | SQLite3 (`db.sqlite3`) — no custom models yet |
| Templates | `templates/` — extends `base.html` |
| Static | `static/` (source) → `staticfiles/` (collected for deploy) |
| Deployment | Google App Engine (F1 instances, `app.yaml`) via `gunicorn` |
| Entry point | `main.py` → `b3rc_site.wsgi` |

### File Map

```
b3rc_site/
  settings.py    # Django config (DEBUG=True, ALLOWED_HOSTS=['*'])
  urls.py        # 5 routes: /, /about/, /activities/, /find-us/, /sponsors/
  views.py       # Simple render functions, one per page
  wsgi.py        # WSGI entry point
templates/
  base.html      # Master layout — fixed black navbar, logo, nav links
  home.html      # Video background hero (background.mp4, purple overlay)
  about.html     # Mission statement, 4-feature grid, CTA
  activities.html # 2-column cards (Wednesday quality, Sunday long run)
  find_us.html   # Location info + embedded Google Maps
  sponsors.html  # Partnership CTA with contact button
static/
  css/style.css  # All custom styles (332 lines)
  images/logo.png
  videos/background.mp4
```

### Current Routes

| URL | View | Template |
|-----|------|----------|
| `/` | `home` | `home.html` |
| `/about/` | `about` | `about.html` |
| `/activities/` | `activities` | `activities.html` |
| `/find-us/` | `find_us` | `find_us.html` |
| `/sponsors/` | `sponsors` | `sponsors.html` |

## Design System

Full design spec lives in `design.md`. Here are the rules to follow when writing frontend code:

### Visual Language
- **Aesthetic:** Performance-driven editorial — generous whitespace, bold typography, high-impact imagery
- **Layout:** Max content width ~1200px centered. CSS Grid/Flexbox. Mobile-first.
- **Spacing rhythm:** 60-80px between sections (desktop), 40px (mobile)

### Color Palette

| Token | Hex | Current Usage |
|-------|-----|---------------|
| Primary | `#003D4C` (deep teal) | Headings, primary buttons — *design.md target* |
| Secondary | `#001A2B` (dark navy) | Footer background, overlays — *design.md target* |
| Accent | `#00A550` (vibrant green) | CTAs, highlights — *design.md target* |
| Background | `#FFFFFF` | Main background |
| Surface | `#F5F5F5` | Alternating sections |
| Text Primary | `#1A1A1A` | Body copy |
| Text Secondary | `#6B6B6B` | Meta text, dates |
| **Currently in CSS** | `#000000` | Navbar, headings, body text (black-heavy) |
| **Currently in CSS** | `rgba(45,16,96,0.3)` | Video overlay (purple tint) |

> **Note:** The current CSS uses a black-and-white palette with a purple video overlay. The design.md specifies a teal/navy/green palette inspired by DSM-Firmenich. New work should migrate toward the design.md palette.

### Typography
- Headings: sans-serif grotesque, 700 weight, uppercase for hero/nav/feature labels
- Body: 16px, 400 weight, line-height 1.6-1.8
- Meta/dates: 13-14px, uppercase
- Buttons: 14px, 600 weight, uppercase
- Letter-spacing: 0.04-0.08em on headings and labels

### Components
- **Navbar:** Fixed top, full-width. Logo left, links right. Collapses on mobile (links hidden, no hamburger yet).
- **Hero:** Video background with overlay. Centered, max-width 800px, border-radius 10px.
- **Cards:** White background, 1px border `rgba(0,0,0,0.12)`, border-radius 12px, padding 24-32px.
- **Buttons:** Black fill, white text, border-radius 8px, 12px 32px padding, opacity hover.
- **Grids:** 2-column on desktop, single column below 768px.

### Responsive
- Single breakpoint at `768px` (mobile vs desktop)
- design.md specifies additional breakpoints at 1024px (tablet) and 1440px (wide) — not yet implemented

### Motion (from design.md, not yet implemented)
- Card hover: scale 1.0 → 1.05, 0.3s ease
- Scroll reveal: fade up + translateY 20px, 0.5s ease
- Nav background: opacity shift on scroll

## Development Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run development server
python manage.py runserver

# Database migrations
python manage.py makemigrations && python manage.py migrate

# Collect static files (required before deploy)
python manage.py collectstatic --noinput

# Deploy to Google App Engine
gcloud app deploy
gcloud app logs tail -s default
```

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `DJANGO_SETTINGS_MODULE` | Settings module path | `b3rc_site.settings` |
| `DJANGO_SECRET_KEY` | Secret key | Falls back to insecure dev key |

## Conventions

- **No separate Django apps.** Keep views, URLs, and logic in `b3rc_site/`.
- **Single CSS file.** All styles in `static/css/style.css`, organized by section with comment headers (`/* ── Section ── */`).
- **Django template tags.** Use `{% static %}` for all asset references. Use `{% url %}` for internal links where possible.
- **Semantic HTML.** Proper heading hierarchy, landmark elements, alt text on images.
- **Keep it static.** The site is currently content-only with no models or dynamic data. When adding dynamic features, keep the MVP minimal.
- **Sydney context.** All locations, times, and references are Sydney-based (AEST/AEDT). Training locations: St Lukes Oval (Concord) and Rhodes Amphitheatre.
- **Contact:** info@b3rc.com.au

## What's Built vs What's in design.md

| Feature | Status |
|---------|--------|
| Fixed navbar with logo + links | Done |
| Video hero with overlay | Done |
| About page (mission, features, CTA) | Done |
| Activities page (2 session cards) | Done |
| Find Us page (maps) | Done |
| Sponsors page (CTA) | Done |
| Design palette migration (teal/navy/green) | Not started |
| News/press release cards | Not started |
| Events list section | Not started |
| Alternating featured content blocks | Not started |
| Newsletter signup | Not started |
| Sponsor logo grid | Not started |
| Dark footer with social links | Not started |
| Scroll animations / hover effects | Not started |
| Mobile hamburger menu | Not started |
| Additional responsive breakpoints (1024, 1440) | Not started |
