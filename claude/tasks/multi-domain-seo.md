# Multi-Domain SEO: b3rc.com.au + b3rc.store

## Goal

Make the Django app serve correctly and rank cleanly from both custom domains without duplicate-content penalties and without broken form submissions.

---

## Current State

| Item | Status |
|------|--------|
| `ALLOWED_HOSTS` | `['*']` — works but permissive |
| `CSRF_TRUSTED_ORIGINS` | Not set — **forms will 403 on custom domains** |
| Canonical URL | `request.build_absolute_uri()` — self-referencing per domain ✓ |
| `og:url` | Missing |
| `robots.txt` | Dynamic per host ✓, but `/admin/` not blocked |
| Sitemap | Dynamic via `request.get_host()` ✓ |
| JSON-LD `url` | `{{ request.scheme }}://{{ request.get_host }}` ✓ |
| `SITE_DOMAIN` in app.yaml | Only set to appspot default, not used in code |

---

## Domain Strategy

| Domain | Purpose | Canonical |
|--------|---------|-----------|
| `b3rc.com.au` | Primary — running club (all pages) | self |
| `b3rc.store` | Shop-focused entry point (all pages, shop emphasis) | self |

Both domains serve the same Django instance. Each is treated as its own canonical — search engines will index each independently. This is acceptable because:
- The two domains target different audiences/search intent (club vs shop)
- Canonical tags self-reference so Google understands which is authoritative per domain
- No cross-domain duplicate-content penalty if canonicals are properly set

---

## Implementation Plan

### 1. `settings.py` — CSRF_TRUSTED_ORIGINS (critical)

Without this, every POST (language switcher, blog comments, checkout) returns **403 Forbidden** on both custom domains.

```python
CSRF_TRUSTED_ORIGINS = [
    'https://b3rc.com.au',
    'https://www.b3rc.com.au',
    'https://b3rc.store',
    'https://www.b3rc.store',
]
```

Also tighten `ALLOWED_HOSTS` from `['*']` to the explicit list (with appspot fallback for GAE):

```python
ALLOWED_HOSTS = [
    'b3rc.com.au',
    'www.b3rc.com.au',
    'b3rc.store',
    'www.b3rc.store',
    'b3rc-467810.ts.r.appspot.com',
    'localhost',
    '127.0.0.1',
]
```

### 2. `base.html` — Add `og:url`

`og:url` should match the canonical. Currently missing. Add:

```html
<meta property="og:url" content="{{ request.build_absolute_uri }}">
```

Placed after `og:locale`.

### 3. `views.py` — robots.txt: block admin + private paths

```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /accounts/
Disallow: /account/
Disallow: /shop/cart/
Disallow: /shop/checkout/

Sitemap: https://<host>/sitemap.xml
```

### 4. `app.yaml` — Update SITE_DOMAIN

Remove the single `SITE_DOMAIN` value (it's not used in code). No change needed here — the app is already domain-agnostic via `request.get_host()`.

---

## What We're NOT Doing

- **No www redirect middleware** — GAE handles custom domain www/apex at the load-balancer level
- **No cross-domain redirect** (b3rc.store → b3rc.com.au) — both domains are intentional
- **No Django Sites framework changes** — `SITE_ID=1` is only used for allauth, not for URL generation

---

## Files Changed

| File | Change |
|------|--------|
| `b3rc_site/settings.py` | Add `CSRF_TRUSTED_ORIGINS`, tighten `ALLOWED_HOSTS` |
| `templates/base.html` | Add `og:url` meta tag |
| `b3rc_site/views.py` | Expand `robots_txt` disallow rules |

---

## Tasks

- [x] Add `CSRF_TRUSTED_ORIGINS` and update `ALLOWED_HOSTS` in `settings.py`
- [x] Add `og:url` to `base.html`
- [x] Update `robots_txt` view to block private paths
