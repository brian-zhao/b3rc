from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('activities/', views.activities, name='activities'),
    path('find-us/', views.find_us, name='find_us'),
    path('sponsors/', views.sponsors, name='sponsors'),
]
