from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from . import views
from .sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('allauth.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    # Stripe webhook — outside i18n, no CSRF
    path('shop/stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('activities/', views.activities, name='activities'),
    path('find-us/', views.find_us, name='find_us'),
    path('sponsors/', views.sponsors, name='sponsors'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    # Account
    path('account/', views.account, name='account'),
    # Shop
    path('shop/', views.shop_landing, name='shop'),
    path('shop/cart/', views.cart, name='cart'),
    path('shop/cart/add/', views.cart_add, name='cart_add'),
    path('shop/checkout/', views.checkout, name='checkout'),
    path('shop/checkout/success/', views.checkout_success, name='checkout_success'),
    path('shop/checkout/cancel/', views.checkout_cancel, name='checkout_cancel'),
    path('shop/orders/', views.order_list, name='order_list'),
    path('shop/orders/<str:order_number>/', views.order_detail, name='order_detail'),
    path('shop/<slug:slug>/', views.product_detail, name='product_detail'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
