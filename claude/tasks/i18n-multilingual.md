# i18n — English / Simplified Chinese / Traditional Chinese

## Goal
Add a language switcher to the navbar that lets users toggle between English (en), Simplified Chinese (zh-hans), and Traditional Chinese (zh-hant). All page content should be translated accordingly.

## Approach — Django i18n (server-side)

Use Django's built-in internationalization framework. This is the standard, SEO-friendly approach with URL prefixes (`/en/`, `/zh-hans/`, `/zh-hant/`).

### Why Django i18n over client-side JS:
- SEO: each language gets its own URL, crawlable by search engines
- No flash of untranslated content
- Standard Django pattern, easy to maintain
- Works without JavaScript

## Implementation Steps

### 1. Configure Django i18n in settings.py
- Add `django.middleware.locale.LocaleMiddleware` to MIDDLEWARE (between SessionMiddleware and CommonMiddleware)
- Define `LANGUAGES` list: en, zh-hans, zh-hant
- Set `LOCALE_PATHS` to `BASE_DIR / 'locale'`
- `USE_I18N = True` (already set)

### 2. Update urls.py with i18n URL patterns
- Wrap existing urlpatterns with `i18n_patterns()`
- Add `path('i18n/', include('django.conf.urls.i18n'))` for the `set_language` view

### 3. Mark all template strings for translation
- Wrap all user-facing text in `{% trans "..." %}` or `{% blocktrans %}...{% endblocktrans %}` tags
- Templates: base.html, home.html, about.html, activities.html, find_us.html, sponsors.html

### 4. Add language switcher to navbar (base.html)
- Add a dropdown/toggle in the navbar (right side, after nav links)
- Uses Django's `set_language` view to switch
- Shows current language, allows switching to the other two
- Style: minimal, matches existing navbar aesthetic

### 5. Create translation files
- Run `django-admin makemessages -l zh_Hans` and `-l zh_Hant`
- Fill in all translations in `locale/zh_Hans/LC_MESSAGES/django.po` and `locale/zh_Hant/LC_MESSAGES/django.po`
- Run `django-admin compilemessages`

### 6. Update CSS
- Style the language switcher dropdown
- Ensure it works on mobile (even though nav-links are hidden on mobile, the language switcher should remain visible)

## Tasks
- [x] Configure settings.py for i18n
- [x] Update urls.py with i18n_patterns
- [x] Mark template strings with {% trans %} tags
- [x] Add language switcher UI to navbar
- [x] Create and fill zh_Hans translations
- [x] Create and fill zh_Hant translations
- [x] Compile messages
- [x] Add CSS for language switcher
- [x] Test all three languages
