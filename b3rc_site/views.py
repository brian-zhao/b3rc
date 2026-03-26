from django.http import HttpResponse
from django.shortcuts import render


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


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        '',
        f'Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
