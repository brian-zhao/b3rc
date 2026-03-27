# Strava SSO + Club Leaderboard

## Goal
Add Strava login via django-allauth and a `/leaderboard/` page showing B3RC club rankings (distance, runs, elevation) pulled from the Strava API.

## Key Constraints
- Strava club activities endpoint does NOT include dates → can't build time-based leaderboards from it alone
- For weekly/monthly leaderboards, we pull each logged-in member's activities (which DO have dates) and aggregate
- Club activities endpoint used for "Recent Activity Feed" (no date needed)
- Rate limits: 200 req/15min, 2000/day → cache aggressively
- Club ID: 1331912

## Approach

### Data Strategy
- **Club info + member count:** GET /clubs/1331912 (public, cached 1hr)
- **Recent activity feed:** GET /clubs/1331912/activities (shows recent runs, no dates, cached 15min)
- **Leaderboard (weekly/monthly):** Aggregate from individual member activities fetched via each user's token. Stored in Firestore, updated periodically.
- **Fallback for logged-out users:** Show the recent activity feed + club stats, prompt to "Sign in with Strava to see full leaderboard"

### Leaderboard Data Model (Firestore)
```
leaderboard_entries/{athlete_id}
├── athlete_id      → int
├── firstname       → str
├── lastname        → str (first initial only for privacy)
├── avatar_url      → str
├── week_distance   → float (meters, current week Mon-Sun)
├── week_runs       → int
├── week_elevation  → float (meters)
├── month_distance  → float
├── month_runs      → int
├── month_elevation → float
├── last_synced     → datetime
```

Updated when a user logs in or visits the leaderboard (if stale > 1hr).

## Implementation Steps

- [ ] 1. Install django-allauth + configure Strava provider
- [ ] 2. Create Strava API app at strava.com/settings/api, get credentials
- [ ] 3. Add login/callback URLs and templates (login page with Strava button)
- [ ] 4. Create UserProfile model (Firestore-backed) with strava tokens
- [ ] 5. Create Strava API service (fetch club info, club activities, athlete activities)
- [ ] 6. Create leaderboard view + template at /leaderboard/
- [ ] 7. Build leaderboard aggregation logic (weekly/monthly from individual activities)
- [ ] 8. Add caching layer (Firestore + in-memory) to respect rate limits
- [ ] 9. Add leaderboard link to navbar
- [ ] 10. Test locally with Strava sandbox
- [ ] 11. Deploy and verify

## Pages

| Route | Auth Required | Content |
|-------|--------------|---------|
| `/leaderboard/` | No (degraded) | Club stats, recent feed, full leaderboard if logged in |
| `/auth/login/` | No | "Sign in with Strava" button |
| `/auth/logout/` | Yes | Logout and redirect home |
