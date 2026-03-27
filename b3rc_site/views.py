import logging

from django.http import HttpResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def activities(request):
    return render(request, 'activities.html')


def find_us(request):
    return render(request, 'find_us.html')


def sponsors(request):
    return render(request, 'sponsors.html')


def leaderboard(request):
    """Club leaderboard — full data for Strava-authenticated users."""
    from . import strava_service

    context = {
        'club_info': None,
        'activities': [],
        'leaderboard': [],
        'strava_connected': False,
        'strava_linked': False,
    }

    if request.user.is_authenticated:
        # User is logged in (via any provider)
        access_token = _get_strava_token(request.user)
        if access_token:
            # Strava is linked — show full leaderboard
            context['strava_connected'] = True
            context['strava_linked'] = True
            context['club_info'] = strava_service.get_club_info(access_token)
            context['activities'] = strava_service.get_club_activities(
                access_token
            )
            context['leaderboard'] = strava_service.build_leaderboard(
                access_token
            )
        else:
            # Logged in via Google/Facebook/Apple but no Strava
            context['strava_connected'] = True  # show logged-in UI
            context['strava_linked'] = False     # prompt to link Strava

    return render(request, 'leaderboard.html', context)


def _get_strava_token(user):
    """Get valid Strava access token for the user, refreshing if needed."""
    if not user.is_authenticated:
        return None

    try:
        from allauth.socialaccount.models import SocialToken, SocialApp
        token = SocialToken.objects.filter(
            account__user=user,
            account__provider='strava',
        ).first()
        if not token:
            return None

        # Refresh if expired
        from django.utils import timezone as tz
        if token.expires_at and token.expires_at <= tz.now():
            return _refresh_strava_token(token)

        return token.token
    except Exception:
        logger.exception('Failed to get Strava token')
        return None


def _refresh_strava_token(token):
    """Refresh an expired Strava OAuth token."""
    import requests
    from django.conf import settings
    from django.utils import timezone as tz
    from datetime import timedelta

    try:
        from allauth.socialaccount.models import SocialApp
        app = SocialApp.objects.get(provider='strava')

        resp = requests.post('https://www.strava.com/oauth/token', data={
            'client_id': app.client_id,
            'client_secret': app.secret,
            'grant_type': 'refresh_token',
            'refresh_token': token.token_secret,
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        token.token = data['access_token']
        token.token_secret = data['refresh_token']
        token.expires_at = tz.now() + timedelta(seconds=data.get('expires_in', 21600))
        token.save()
        return token.token
    except Exception:
        logger.exception('Failed to refresh Strava token')
        return None


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        '',
        f'Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
