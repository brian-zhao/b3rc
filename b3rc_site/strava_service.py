"""
Strava API client for fetching club data and athlete activities.

Uses the authenticated user's access token for personal data,
and caches club-level data in Firestore to respect rate limits.
"""
import logging
import time
from datetime import datetime, timedelta, timezone

import requests
from django.conf import settings

from . import firestore_service

logger = logging.getLogger(__name__)

STRAVA_API = 'https://www.strava.com/api/v3'


def _get_headers(access_token):
    return {'Authorization': f'Bearer {access_token}'}


# ── Club Data ──

def get_club_info(access_token):
    """Fetch club details. Cached in Firestore for 1 hour."""
    db = firestore_service.get_client()
    cache_ref = db.collection('strava_cache').document('club_info')
    cached = cache_ref.get()

    if cached.exists:
        data = cached.to_dict()
        if data.get('cached_at') and (
            datetime.now(timezone.utc) - data['cached_at']
        ).total_seconds() < 3600:
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
        return club_data
    except Exception:
        logger.exception('Failed to fetch club info from Strava')
        if cached.exists:
            return cached.to_dict()
        return None


def get_club_activities(access_token, per_page=30):
    """Fetch recent club activities. Cached 15 min."""
    db = firestore_service.get_client()
    cache_ref = db.collection('strava_cache').document('club_activities')
    cached = cache_ref.get()

    if cached.exists:
        data = cached.to_dict()
        if data.get('cached_at') and (
            datetime.now(timezone.utc) - data['cached_at']
        ).total_seconds() < 900:
            return data.get('activities', [])

    try:
        resp = requests.get(
            f'{STRAVA_API}/clubs/{settings.STRAVA_CLUB_ID}/activities',
            headers=_get_headers(access_token),
            params={'per_page': per_page},
            timeout=10,
        )
        resp.raise_for_status()
        raw = resp.json()

        activities = []
        for a in raw:
            distance_km = a.get('distance', 0) / 1000
            moving_time = a.get('moving_time', 0)
            pace_min_km = (moving_time / 60) / distance_km if distance_km > 0 else 0
            activities.append({
                'firstname': a.get('athlete', {}).get('firstname', ''),
                'lastname_initial': (
                    a.get('athlete', {}).get('lastname', ' ')[0] + '.'
                    if a.get('athlete', {}).get('lastname')
                    else ''
                ),
                'name': a.get('name', 'Activity'),
                'type': a.get('type', 'Run'),
                'sport_type': a.get('sport_type', 'Run'),
                'distance_km': round(distance_km, 2),
                'moving_time_seconds': moving_time,
                'moving_time_display': _format_duration(moving_time),
                'pace_display': _format_pace(pace_min_km) if distance_km > 0 else '',
                'elevation': round(a.get('total_elevation_gain', 0)),
            })

        cache_ref.set({
            'activities': activities,
            'cached_at': datetime.now(timezone.utc),
        })
        return activities
    except Exception:
        logger.exception('Failed to fetch club activities from Strava')
        if cached.exists:
            return cached.to_dict().get('activities', [])
        return []


# ── Leaderboard (aggregated from club activities) ──

def build_leaderboard(access_token):
    """
    Build a leaderboard from club activities.

    Since the Strava club activities endpoint doesn't include dates,
    we aggregate by athlete across all returned activities (typically
    the most recent ~30). This gives a "recent activity" leaderboard.
    """
    activities = get_club_activities(access_token, per_page=200)

    athletes = {}
    for a in activities:
        if a.get('type') not in ('Run', 'TrailRun', 'VirtualRun'):
            continue

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
        athletes[key]['total_elevation'] += a['elevation']
        athletes[key]['total_time_seconds'] += a['moving_time_seconds']

    # Compute averages and format
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

    # Sort by total distance descending
    leaderboard.sort(key=lambda x: x['distance_km'], reverse=True)
    return leaderboard


# ── Helpers ──

def _format_duration(seconds):
    """Format seconds as Xh Ym or Ym Xs."""
    seconds = int(seconds)
    if seconds >= 3600:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f'{h}h {m:02d}m'
    m = seconds // 60
    s = seconds % 60
    return f'{m}m {s:02d}s'


def _format_pace(min_per_km):
    """Format pace as M:SS /km."""
    if min_per_km <= 0 or min_per_km > 30:
        return ''
    m = int(min_per_km)
    s = int((min_per_km - m) * 60)
    return f'{m}:{s:02d} /km'
