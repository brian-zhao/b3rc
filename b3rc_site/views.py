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
