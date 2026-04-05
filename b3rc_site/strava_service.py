"""
Strava API client for fetching club data and athlete activities.

Uses the authenticated user's access token for club data.
Activities are accumulated in Firestore with timestamps so we can
build genuine this-week / last-week leaderboards (the Strava API
returns club activities without dates, so we track first-seen time).
"""
import logging
from datetime import datetime, timedelta, timezone

import requests
from django.conf import settings

from . import firestore_service

logger = logging.getLogger(__name__)

STRAVA_API = 'https://www.strava.com/api/v3'
CACHE_TTL_SECONDS = 2 * 3600  # 2 hours

# Module-level memory cache — instant reads within the same server process.
# Firestore is the persistent fallback across restarts / GAE instances.
_mem: dict = {}


def _mem_get(key):
    entry = _mem.get(key)
    if entry and (datetime.now(timezone.utc) - entry['ts']).total_seconds() < CACHE_TTL_SECONDS:
        return entry['data']
    return None


def _mem_set(key, data):
    _mem[key] = {'data': data, 'ts': datetime.now(timezone.utc)}


def _get_headers(access_token):
    return {'Authorization': f'Bearer {access_token}'}


def _week_bounds(week_offset=0):
    """Return (start, end) UTC datetimes for a given week (0=this, 1=last).
    Strava weeks run Monday–Sunday.
    """
    now = datetime.now(timezone.utc)
    # Monday of the current week
    monday = now - timedelta(days=now.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    start = monday - timedelta(weeks=week_offset)
    end = start + timedelta(weeks=1)
    return start, end


# ── Service Token ─────────────────────────────────────────────────────────

def get_service_token():
    """
    Return a valid access token using the stored service refresh token.
    Auto-refreshes when expired and persists the new tokens to Firestore
    so the latest refresh token survives across restarts.
    """
    cached = _mem_get('service_token')
    if cached:
        return cached

    db = firestore_service.get_client()
    ref = db.collection('strava_cache').document('service_token')
    doc = ref.get()
    if doc.exists:
        data = doc.to_dict()
        expires_at = data.get('expires_at')
        if expires_at and expires_at > datetime.now(timezone.utc):
            _mem_set('service_token', data['access_token'])
            return data['access_token']
        # Prefer the refresh token stored in Firestore (may be newer than env var)
        refresh_token = data.get('refresh_token') or settings.STRAVA_REFRESH_TOKEN
    else:
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
        expires_at = datetime.fromtimestamp(data['expires_at'], tz=timezone.utc)

        ref.set({
            'access_token': access_token,
            'refresh_token': data['refresh_token'],
            'expires_at': expires_at,
        })
        _mem_set('service_token', access_token)
        return access_token
    except Exception:
        logger.exception('Failed to refresh Strava service token')
        return None


# ── Club Info ──────────────────────────────────────────────────────────────

def get_club_info(access_token):
    """Fetch club details. Memory-cached for 2 hours, persisted in Firestore."""
    cached = _mem_get('club_info')
    if cached:
        return cached

    db = firestore_service.get_client()
    cache_ref = db.collection('strava_cache').document('club_info')
    cached = cache_ref.get()

    if cached.exists:
        data = cached.to_dict()
        if data.get('cached_at') and (
            datetime.now(timezone.utc) - data['cached_at']
        ).total_seconds() < CACHE_TTL_SECONDS:
            _mem_set('club_info', data)
            return data

    try:
        resp = requests.get(
            f'{STRAVA_API}/clubs/{settings.STRAVA_CLUB_ID}',
            headers=_get_headers(access_token),
            timeout=10,
        )
        resp.raise_for_status()
        info = resp.json()
        club_data = {
            'name': info.get('name', ''),
            'member_count': info.get('member_count', 0),
            'description': info.get('description', ''),
            'city': info.get('city', ''),
            'state': info.get('state', ''),
            'country': info.get('country', ''),
            'profile': info.get('profile', ''),
            'cover_photo': info.get('cover_photo', ''),
            'url': info.get('url', ''),
            'cached_at': datetime.now(timezone.utc),
        }
        cache_ref.set(club_data)
        _mem_set('club_info', club_data)
        return club_data
    except Exception:
        logger.exception('Failed to fetch club info from Strava')
        if cached.exists:
            data = cached.to_dict()
            _mem_set('club_info', data)
            return data
        return None


# ── Activity Accumulation ─────────────────────────────────────────────────


def accumulate_club_activities(access_token):
    """
    Fetch recent club activities and store any NEW ones in Firestore with
    a first_seen_at timestamp.  Skipped if last fetch was within 2 hours
    (shared cache — same data for all users).

    Returns (new_count, total_count).
    """
    # Fast path: memory says we fetched recently — skip Firestore entirely
    if _mem_get('last_fetched'):
        return 0, 0

    db = firestore_service.get_client()
    now = datetime.now(timezone.utc)

    # Record when we first started tracking (used to warn the UI)
    meta_ref = db.collection('strava_cache').document('tracking_meta')
    meta = meta_ref.get()
    meta_data = meta.to_dict() if meta.exists else {}

    if not meta.exists:
        meta_ref.set({'tracking_started_at': now, 'last_fetched_at': None})
        meta_data = {'tracking_started_at': now, 'last_fetched_at': None}

    # Skip if fetched within the last 2 hours
    last_fetched = meta_data.get('last_fetched_at')
    if last_fetched and (now - last_fetched).total_seconds() < CACHE_TTL_SECONDS:
        logger.debug('Strava fetch skipped — cache valid for another %ds',
                     CACHE_TTL_SECONDS - (now - last_fetched).total_seconds())
        return 0, 0

    try:
        resp = requests.get(
            f'{STRAVA_API}/clubs/{settings.STRAVA_CLUB_ID}/activities',
            headers=_get_headers(access_token),
            params={'per_page': 200},
            timeout=15,
        )
        resp.raise_for_status()
        raw = resp.json()
    except Exception:
        logger.exception('Failed to fetch club activities from Strava')
        return 0, 0

    log_col = db.collection('strava_activities_log')
    new_count = 0

    for a in raw:
        activity_type = a.get('sport_type') or a.get('type', '')
        if activity_type not in ('Run', 'TrailRun', 'VirtualRun'):
            continue

        firstname = a.get('athlete', {}).get('firstname', '')
        lastname = a.get('athlete', {}).get('lastname', '')
        lastname_initial = (lastname[0] + '.') if lastname else ''
        name = a.get('name', 'Activity')
        distance_m = int(a.get('distance', 0))
        moving_time = int(a.get('moving_time', 0))

        # Fingerprint: enough to uniquely identify the activity
        fp = f"{firstname}_{lastname}_{distance_m}_{moving_time}"
        fp = fp.replace(' ', '_').lower()

        doc_ref = log_col.document(fp)
        if not doc_ref.get().exists:
            distance_km = distance_m / 1000
            pace = (moving_time / 60) / distance_km if distance_km > 0 else 0
            doc_ref.set({
                'firstname': firstname,
                'lastname_initial': lastname_initial,
                'name': name,
                'type': activity_type,
                'distance_km': round(distance_km, 2),
                'moving_time_seconds': moving_time,
                'moving_time_display': _format_duration(moving_time),
                'pace_display': _format_pace(pace) if distance_km > 0 else '',
                'elevation': round(a.get('total_elevation_gain', 0)),
                'first_seen_at': now,
            })
            new_count += 1

    # Update last fetched timestamp in Firestore and memory
    meta_ref.set({'last_fetched_at': now}, merge=True)
    _mem_set('last_fetched', True)

    total = log_col.count().get()[0][0].value
    return new_count, total


def get_tracking_started_at():
    """Return when activity tracking began, or None."""
    cached = _mem_get('tracking_started_at')
    if cached:
        return cached
    db = firestore_service.get_client()
    meta = db.collection('strava_cache').document('tracking_meta').get()
    if meta.exists:
        val = meta.to_dict().get('tracking_started_at')
        if val:
            _mem_set('tracking_started_at', val)
        return val
    return None


# ── Weekly Leaderboards ────────────────────────────────────────────────────

def build_weekly_leaderboard(week_offset=0):
    """
    Build a leaderboard for a given week from the Firestore activity log.
    week_offset=0 → this week (Mon–now), week_offset=1 → last week.
    Results memory-cached for 2 hours, persisted in Firestore.
    """
    mem_key = f'leaderboard_w{week_offset}'
    cached_mem = _mem_get(mem_key)
    if cached_mem is not None:
        return cached_mem

    db = firestore_service.get_client()
    now = datetime.now(timezone.utc)
    cache_key = f'leaderboard_w{week_offset}'
    cache_ref = db.collection('strava_cache').document(cache_key)
    cached = cache_ref.get()

    if cached.exists:
        data = cached.to_dict()
        if data.get('cached_at') and (now - data['cached_at']).total_seconds() < CACHE_TTL_SECONDS:
            entries = data.get('entries', [])
            _mem_set(mem_key, entries)
            return entries

    start, end = _week_bounds(week_offset)
    docs = (
        db.collection('strava_activities_log')
        .where('first_seen_at', '>=', start)
        .where('first_seen_at', '<', end)
        .stream()
    )

    athletes = {}
    for doc in docs:
        a = doc.to_dict()
        key = a['firstname'] + ' ' + a['lastname_initial']
        if key not in athletes:
            athletes[key] = {
                'name': key,
                'total_distance_km': 0,
                'total_runs': 0,
                'total_elevation': 0,
                'total_time_seconds': 0,
            }
        athletes[key]['total_distance_km'] += a['distance_km']
        athletes[key]['total_runs'] += 1
        athletes[key]['total_elevation'] += a.get('elevation', 0)
        athletes[key]['total_time_seconds'] += a['moving_time_seconds']

    leaderboard = []
    for athlete in athletes.values():
        dist = athlete['total_distance_km']
        time_s = athlete['total_time_seconds']
        avg_pace = (time_s / 60) / dist if dist > 0 else 0
        leaderboard.append({
            'name': athlete['name'],
            'distance_km': round(dist, 1),
            'runs': athlete['total_runs'],
            'elevation': athlete['total_elevation'],
            'time_display': _format_duration(time_s),
            'avg_pace': _format_pace(avg_pace) if dist > 0 else '',
        })

    leaderboard.sort(key=lambda x: x['distance_km'], reverse=True)
    cache_ref.set({'entries': leaderboard, 'cached_at': now})
    _mem_set(mem_key, leaderboard)
    return leaderboard


# ── Recent Activity Feed ───────────────────────────────────────────────────

def get_recent_activities(limit=30):
    """Return the most recently seen activities from Firestore log."""
    db = firestore_service.get_client()
    docs = (
        db.collection('strava_activities_log')
        .order_by('first_seen_at', direction='DESCENDING')
        .limit(limit)
        .stream()
    )
    return [doc.to_dict() for doc in docs]


# ── Helpers ───────────────────────────────────────────────────────────────

def _format_duration(seconds):
    seconds = int(seconds)
    if seconds >= 3600:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f'{h}h {m:02d}m'
    m = seconds // 60
    s = seconds % 60
    return f'{m}m {s:02d}s'


def _format_pace(min_per_km):
    if min_per_km <= 0 or min_per_km > 30:
        return ''
    m = int(min_per_km)
    s = int((min_per_km - m) * 60)
    return f'{m}:{s:02d} /km'
