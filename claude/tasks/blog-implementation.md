# Blog & Events — Implementation Plan

## Goal

A public blog/events section where admins post about club events, parkruns, race recaps, and training highlights. Posts support rich text, YouTube/Vimeo video embeds, and featured images. The list page shows posts alongside a month calendar that highlights event dates.

---

## What Gets Built

### 1. `Post` Django Model

```
title            CharField(200)
slug             SlugField(unique=True)        — auto-generated from title
category         CharField(choices)
status           CharField(DRAFT | PUBLISHED)
body             TextField                     — Markdown
featured_image   ImageField(blank)             — stored in GCS / local media
video_url        URLField(blank)               — YouTube or Vimeo link
event_date       DateField(null, blank)        — the day the event happened
location         CharField(200, blank)         — e.g. "Rhodes Amphitheatre"
strava_url       URLField(blank)               — optional link to Strava activity/event
is_featured      BooleanField(default=False)   — pin to top of list
author           ForeignKey(User, null)
created_at       DateTimeField(auto_now_add)
updated_at       DateTimeField(auto_now)
published_at     DateTimeField(null, blank)    — auto-set when first published
```

**Category choices:**
| Value | Label |
|-------|-------|
| `EVENT` | Club Event |
| `PARKRUN` | Parkrun |
| `RACE` | Race Recap |
| `TRAINING` | Training Report |
| `NEWS` | Club News |

### 2. Django Admin

- Auto-generate slug from title on create (editable after)
- Auto-set `published_at` when status changes DRAFT → PUBLISHED
- Markdown preview panel (use `django-markdownx` or render inline with JS)
- Inline `featured_image` upload preview
- Filter by status, category, event_date
- Search by title, body
- List display: title, category, status, event_date, is_featured

### 3. Firestore Persistence (follow existing sync pattern)

Since SQLite is ephemeral on GAE, blog posts must be persisted in Firestore and synced back on startup — exactly the same as Products and Orders.

- Add `save_post(post)` / `list_posts()` to `firestore_service.py`
- Add `_sync_posts()` to `sync_from_firestore` management command
- Add `_export_posts()` to `export_to_firestore` management command
- Add post-save signal in `signals.py` to auto-export to Firestore on admin save
- Featured images are already stored in GCS (via `django-storages`) so only the path is synced

### 4. URL Routes

```
/blog/                  → post list + calendar sidebar
/blog/<slug>/           → post detail
/blog/category/<cat>/   → filtered list by category  (optional, nice to have)
```

### 5. Blog List Page (`templates/blog/list.html`)

**Layout:** two-column (posts left, sidebar right)

**Left — Post Cards:**
- Featured post (if any) shown full-width at top with large image/video thumbnail
- Remaining posts as cards: featured image thumbnail, category pill, title, excerpt (first 160 chars of body), event_date, location
- Pagination (10 per page)
- Category filter tabs above the list

**Right — Sidebar:**
- Mini calendar (current month)
  - Highlight dates that have a published post with `event_date`
  - Click a highlighted date → filters list to that day
  - Prev/next month navigation
- Recent posts list (latest 5 titles)
- Category counts

**Calendar implementation:** pure HTML + vanilla JS (no external library). Server renders a JSON blob of `event_date` values into a `<script>` tag; JS builds the calendar and marks those dates.

### 6. Blog Detail Page (`templates/blog/detail.html`)

- Hero: featured image (full-width) or video embed (YouTube/Vimeo iframe)
- Title, category pill, event_date, location, Strava link (if set)
- Body rendered from Markdown to HTML (using `markdown` package, already in `requirements.txt`)
- Author + published date in footer of post
- Next / Previous post navigation (by published_at)
- Back to Blog link

### 7. Video Embed Helper

Parse `video_url` to detect YouTube vs Vimeo and output the correct `<iframe>` embed code. Store as a template tag or model property.

```python
# Supports:
# https://www.youtube.com/watch?v=VIDEO_ID
# https://youtu.be/VIDEO_ID
# https://vimeo.com/VIDEO_ID
```

### 8. Navbar + Footer

- Add **Blog** link to desktop nav, mobile nav, footer
- Show post count badge or "New" indicator if there's a post from the last 7 days (optional)

---

## Implementation Steps

### Phase 1 — Model & Admin (do first, get admin working)
- [x] Add `Post` model to `models.py` with all fields above
- [x] Write and run migration
- [x] Register `Post` in `admin.py` with full config (filters, search, list_display, auto-slug, auto-published_at)
- [x] Add post-save signal to `signals.py` to export to Firestore
- [x] Add `save_post` / `list_posts` / `delete_post` to `firestore_service.py`
- [x] Add `_sync_posts` to `sync_from_firestore`
- [x] Add `_export_posts` to `export_to_firestore`
- [x] Test: create a post in local admin, verify it syncs to Firestore

### Phase 2 — Views & URLs
- [x] Add `blog_list` view (paginated, category filter, event_date filter)
- [x] Add `blog_detail` view
- [x] Add URL routes to `urls.py`
- [x] Add `Blog` to navbar and footer links in `base.html`

### Phase 3 — Templates
- [x] `templates/blog/list.html` — two-column layout, post cards, category tabs, vanilla JS calendar
- [x] `templates/blog/detail.html` — full post with markdown render, video embed, prev/next nav
- [x] Add blog-specific CSS to `static/css/style.css`

### Phase 4 — Video embed
- [x] Add `video_embed_url` property on `Post` model (parses YouTube/Vimeo URL to embed URL)
- [x] Use in detail template with `<iframe>`

### Phase 5 — Polish
- [x] SEO: `<meta>` tags on detail page (og:title, og:description, structured data BlogPosting)
- [x] Add **Blog** to sitemap (`StaticViewSitemap` + new `BlogPostSitemap`)
- [ ] Update `CLAUDE.md` with new routes and model

---

## Reasonable Additions (not originally asked for)

| Addition | Why it makes sense |
|----------|--------------------|
| **Draft / Published status** | Admin can write posts ahead of time without going live |
| **`event_date` separate from `published_at`** | A race recap posted Tuesday should show the Saturday event date on the calendar |
| **Category filter tabs** | Club has distinct activity types (parkrun, Sunday long run, race) — filtering makes content scannable |
| **Strava activity URL field** | Natural integration — link the blog post back to the Strava club event or segment effort |
| **`is_featured` flag** | Pin one post as a hero/banner (e.g. the most recent race result) |
| **Video embed parser** | Members record GoPro/phone clips of parkruns — YouTube embed is the easiest way to share |
| **Firestore sync** | Without this, posts vanish on every GAE cold start (same problem already solved for Shop) |
| **Excerpt in list view** | First 160 chars of body, auto-truncated — avoids needing a separate summary field |
| **Next/Prev post nav on detail** | Keeps users engaged, easy to browse event history |
| **Calendar date highlights** | The calendar only lights up dates with actual events, so it's informative rather than decorative |

---

## Files Changed

```
b3rc_site/
  models.py              — add Post model
  admin.py               — register Post with full config
  signals.py             — add Post save/delete signal
  firestore_service.py   — add post CRUD functions
  views.py               — add blog_list, blog_detail
  urls.py                — add /blog/ routes
  management/commands/
    sync_from_firestore.py   — add _sync_posts
    export_to_firestore.py   — add _export_posts
templates/
  blog/
    list.html
    detail.html
    _calendar.html
  base.html              — add Blog nav link
static/css/style.css     — blog section styles
```

---

## Out of Scope (for now)

- Comments / reactions
- Newsletter subscribe on blog
- RSS feed
- Tag system (category is enough for now)
- Admin WYSIWYG editor (Markdown is simpler and already works)
- Multi-author bylines (single admin club)
