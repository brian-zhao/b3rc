# Firestore Migration — Replace Cloud SQL with Google Firestore

## Goal
Eliminate Cloud SQL (PostgreSQL) dependency entirely. Use Firestore as the persistent data store for SiteMedia and CarouselImage. Keep Django admin working unchanged.

## Approach: "Firestore as source of truth, SQLite as ephemeral cache"

Since Django admin is tightly coupled to the ORM, the simplest migration path is:
- **Firestore** stores all SiteMedia and CarouselImage data persistently
- **SQLite** is used everywhere (dev + prod) for Django internals (auth, sessions, contenttypes, migrations) and as an ephemeral cache for our models
- On GAE startup: migrate SQLite → load data from Firestore → create superuser → start gunicorn
- On admin save/delete: Django writes to SQLite normally, then a `post_save`/`post_delete` signal syncs to Firestore

### Why this works on GAE
- GAE filesystem is ephemeral, but the entrypoint runs on every instance start
- `migrate --noinput` creates fresh tables each time
- `sync_from_firestore` populates them from Firestore
- Cookie-based sessions eliminate the need for persistent session storage
- Admin user is auto-created from env vars

### What stays unchanged
- `models.py` — no changes needed
- `admin.py` — no changes needed
- `context_processors.py` — no changes needed
- `views.py` — no changes needed
- All templates — no changes needed

## Implementation Steps

- [ ] 1. Create `b3rc_site/firestore_service.py` — Firestore client + CRUD helpers
- [ ] 2. Create `b3rc_site/signals.py` — post_save/post_delete sync to Firestore
- [ ] 3. Create `b3rc_site/apps.py` — connect signals on ready()
- [ ] 4. Create `b3rc_site/management/commands/sync_from_firestore.py` — load Firestore data into SQLite
- [ ] 5. Create `b3rc_site/management/commands/ensure_superuser.py` — auto-create admin user
- [ ] 6. Update `b3rc_site/settings.py` — SQLite everywhere, cookie sessions, add FIRESTORE_PROJECT_ID
- [ ] 7. Update `requirements.txt` — remove psycopg2-binary, add google-cloud-firestore
- [ ] 8. Update `app.yaml` — remove DB_PASSWORD, update entrypoint
- [ ] 9. Create `firebase.json` + `firestore.rules` for local emulator
- [ ] 10. Test locally with Firestore emulator

## Testing Plan
1. Start Firestore emulator: `gcloud emulators firestore start`
2. Set `FIRESTORE_EMULATOR_HOST=localhost:8080`
3. Run `python manage.py migrate && python manage.py sync_from_firestore && python manage.py runserver`
4. Add/edit/delete SiteMedia and CarouselImage via admin
5. Restart server — verify data persists (loaded from Firestore)
6. Kill emulator — verify site still loads from SQLite cache
