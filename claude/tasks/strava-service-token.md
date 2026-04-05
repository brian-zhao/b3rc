# Strava Service Token — Fix Leaderboard 403

## Problem

Strava restricts unreviewed apps to **1 connected athlete** (the developer).
The current code requires every leaderboard visitor to OAuth with Strava, so
the 2nd user to authorize hits:

> Error 403: Limit of connected athletes exceeded

The leaderboard only calls two club endpoints:
- `GET /clubs/{id}` — club info
- `GET /clubs/{id}/activities` — recent member activity

Neither endpoint requires the *current user's* token. Any valid token from a
club member works. There is no reason to gate the leaderboard behind per-user
Strava login.

---

## Fix: Single Service Token

Store the developer's own Strava refresh token as an env variable. On startup /
on demand, auto-refresh it and use it for all club API calls. Users no longer
need to connect Strava just to see the leaderboard.

### What Changes

| Layer | Change |
|-------|--------|
| `settings.py` | Add `STRAVA_REFRESH_TOKEN` setting |
| `app.yaml` | Add `STRAVA_REFRESH_TOKEN` env variable |
| `strava_service.py` | Add `get_service_token()` that auto-refreshes; cache in Firestore |
| `views.py` | `leaderboard()` — remove Strava auth gate; use service token |
| `leaderboard.html` | Remove "connect Strava" prompt (audit only — may need minor copy change) |

### What Does NOT Change

- Users can still optionally connect Strava for their own profile/account features
- `_get_strava_token()` and the per-user token refresh code stay (used by account page)
- No migration needed — Firestore activity log stays intact

---

## Implementation

### 1. `strava_service.py` — `get_service_token()`

```python
def get_service_token():
    """
    Return a valid access token using the stored service refresh token.
    Auto-refreshes when expired; persists new token to Firestore.
    """
    # Check memory cache first
    cached = _mem_get('service_token')
    if cached:
        return cached

    # Check Firestore for a still-valid access token
    db = firestore_service.get_client()
    ref = db.collection('strava_cache').document('service_token')
    doc = ref.get()
    if doc.exists:
        data = doc.to_dict()
        expires_at = data.get('expires_at')
        if expires_at and expires_at > datetime.now(timezone.utc):
            _mem_set('service_token', data['access_token'])
            return data['access_token']

    # Refresh using stored refresh token
    refresh_token = settings.STRAVA_REFRESH_TOKEN
    if not refresh_token:
        logger.error('STRAVA_REFRESH_TOKEN not configured')
        return None

    try:
        resp = requests.post('https://www.strava.com/oauth/token', data={
            'client_id': settings.STRAVA_CLIENT_ID,
            'client_secret': settings.STRAVA_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        access_token = data['access_token']
        new_refresh = data['refresh_token']
        expires_at = datetime.fromtimestamp(data['expires_at'], tz=timezone.utc)

        # Persist to Firestore
        ref.set({
            'access_token': access_token,
            'refresh_token': new_refresh,
            'expires_at': expires_at,
        })
        # Update settings in-process so next startup picks up latest refresh token
        # (Firestore is source of truth between deploys)

        _mem_set('service_token', access_token)
        return access_token
    except Exception:
        logger.exception('Failed to refresh Strava service token')
        return None
```

### 2. `views.py` — `leaderboard()`

Remove the `if not access_token: return render(...)` early-return that blocks
unauthenticated users. Replace with service token:

```python
def leaderboard(request):
    from . import strava_service

    access_token = strava_service.get_service_token()

    context = {
        'club_info': strava_service.get_club_info(access_token) if access_token else None,
        'this_week': [],
        'last_week': [],
        'strava_connected': False,
        'tracking_started_at': None,
        'tracking_days': 0,
    }

    if access_token:
        strava_service.accumulate_club_activities(access_token)
        context['this_week'] = strava_service.build_weekly_leaderboard(week_offset=0)
        context['last_week'] = strava_service.build_weekly_leaderboard(week_offset=1)
        ...

    # Per-user Strava connection only needed for current_user_name highlight
    if request.user.is_authenticated:
        # resolve current_user_name for row highlight (optional, no OAuth needed)
        ...

    return render(request, 'leaderboard.html', context)
```

### 3. `settings.py`

```python
STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN', '')
```

### 4. `app.yaml`

```yaml
STRAVA_REFRESH_TOKEN: "<developer refresh token from strava.com/settings/api>"
```

---

## How to Get the Initial Refresh Token

1. Go to https://www.strava.com/settings/api
2. Under the app, click "Authorize" with scope `activity:read`
3. Or use the OAuth flow manually with your own account:
   ```
   https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID
     &redirect_uri=http://localhost&response_type=code&scope=read,activity:read
   ```
4. Exchange the code for tokens:
   ```bash
   curl -X POST https://www.strava.com/oauth/token \
     -d client_id=YOUR_ID \
     -d client_secret=YOUR_SECRET \
     -d code=AUTH_CODE \
     -d grant_type=authorization_code
   ```
5. Copy the `refresh_token` from the response → put in `app.yaml`

The refresh token is long-lived. The service auto-refreshes the access token
(6hr expiry) and stores the latest refresh token in Firestore.

---

## Long-Term: Strava Developer Program

Separately, submit the app for review at developers@strava.com to lift the
1-athlete cap — needed if users ever want to connect their own Strava for
personal features (e.g. personal activity tracking, Strava login).

This fix is independent — it removes the immediate 403 blocker for all users.

---

## Files Changed

| File | Change |
|------|--------|
| `b3rc_site/strava_service.py` | Add `get_service_token()` |
| `b3rc_site/views.py` | Leaderboard uses service token, removes Strava auth gate |
| `b3rc_site/settings.py` | Add `STRAVA_REFRESH_TOKEN` |
| `app.yaml` | Add `STRAVA_REFRESH_TOKEN` env var |

---

## Tasks

- [x] Add `get_service_token()` to `strava_service.py`
- [x] Refactor `leaderboard()` in `views.py` to use service token
- [x] Add `STRAVA_REFRESH_TOKEN` to `settings.py` and `app.yaml`
- [x] Get initial refresh token from Strava and add to `app.yaml`
