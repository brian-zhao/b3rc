import json
import logging
from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Post, PostComment, PostLike, Product, ProductVariant, Order, OrderItem

logger = logging.getLogger(__name__)


def home(request):
    recent_posts = Post.objects.filter(status='PUBLISHED').order_by('-published_at')[:3]
    return render(request, 'home.html', {'recent_posts': recent_posts})


def about(request):
    return render(request, 'about.html')


def activities(request):
    return render(request, 'activities.html')


def find_us(request):
    return render(request, 'find_us.html')


def sponsors(request):
    return render(request, 'sponsors.html')


def leaderboard(request):
    """Club leaderboard — requires Strava login."""
    from . import strava_service
    from datetime import datetime, timezone

    context = {
        'club_info': None,
        'this_week': [],
        'last_week': [],
        'recent_activities': [],
        'strava_connected': False,
        'tracking_started_at': None,
        'tracking_days': 0,
    }

    if not request.user.is_authenticated:
        return render(request, 'leaderboard.html', context)

    access_token = _get_strava_token(request.user)
    if not access_token:
        return render(request, 'leaderboard.html', context)

    context['strava_connected'] = True
    context['club_info'] = strava_service.get_club_info(access_token)

    # Current user's display name in leaderboard (e.g. "Brian Z.")
    try:
        from allauth.socialaccount.models import SocialAccount
        strava_account = SocialAccount.objects.get(user=request.user, provider='strava')
        extra = strava_account.extra_data
        firstname = extra.get('firstname', '')
        lastname = extra.get('lastname', '')
        lastname_initial = (lastname[0] + '.') if lastname else ''
        context['current_user_name'] = f'{firstname} {lastname_initial}'.strip()
    except Exception:
        context['current_user_name'] = ''

    # Accumulate new activities into Firestore log
    strava_service.accumulate_club_activities(access_token)

    # Weekly leaderboards from Firestore log
    context['this_week'] = strava_service.build_weekly_leaderboard(week_offset=0)
    context['last_week'] = strava_service.build_weekly_leaderboard(week_offset=1)

    # How long we've been tracking (affects whether weekly data is meaningful)
    started = strava_service.get_tracking_started_at()
    if started:
        context['tracking_started_at'] = started
        context['tracking_days'] = (datetime.now(timezone.utc) - started).days

    return render(request, 'leaderboard.html', context)


def _get_strava_token(user):
    """Get valid Strava access token for the user, refreshing if needed.
    Falls back to any stored Strava token since club data is member-agnostic.
    """
    if not user.is_authenticated:
        return None

    try:
        from allauth.socialaccount.models import SocialToken, SocialAccount
        from django.utils import timezone as tz

        # Check if this user has a linked Strava account
        has_strava = SocialAccount.objects.filter(user=user, provider='strava').exists()
        if not has_strava:
            return None

        # Try user's own token first, fall back to any stored Strava token
        token = SocialToken.objects.filter(
            account__user=user,
            account__provider='strava',
        ).first() or SocialToken.objects.filter(
            account__provider='strava',
        ).first()

        if not token:
            return None

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


# ── Blog Views ───────────────────────────────────────────────────────────────

def blog_list(request):
    import json as _json
    from datetime import date

    category   = request.GET.get('category', '').upper()
    date_str   = request.GET.get('date', '')
    page_num   = int(request.GET.get('page', 1))

    posts = Post.objects.filter(status='PUBLISHED').order_by('-is_featured', '-published_at')

    if category and category in dict(Post.CATEGORY_CHOICES):
        posts = posts.filter(category=category)

    if date_str:
        try:
            filter_date = date.fromisoformat(date_str)
            posts = posts.filter(event_date=filter_date)
        except ValueError:
            pass

    # Pagination
    per_page   = 10
    total      = posts.count()
    total_pages = max(1, (total + per_page - 1) // per_page)
    page_num   = max(1, min(page_num, total_pages))
    offset     = (page_num - 1) * per_page
    page_posts = posts[offset: offset + per_page]

    # Calendar: all published event_dates for JS highlighting
    all_event_dates = list(
        Post.objects.filter(status='PUBLISHED')
        .exclude(event_date=None)
        .values_list('event_date', flat=True)
    )
    event_dates_json = _json.dumps([d.isoformat() for d in all_event_dates])

    # Sidebar: recent posts & category counts as (val, label, count) tuples
    recent_posts = Post.objects.filter(status='PUBLISHED').order_by('-published_at')[:5]
    categories_with_counts = [
        (val, label, Post.objects.filter(status='PUBLISHED', category=val).count())
        for val, label in Post.CATEGORY_CHOICES
    ]

    return render(request, 'blog/list.html', {
        'posts':                  page_posts,
        'category_choices':       Post.CATEGORY_CHOICES,
        'categories_with_counts': categories_with_counts,
        'current_category':       category,
        'current_date':           date_str,
        'page':                   page_num,
        'total_pages':            total_pages,
        'has_prev':               page_num > 1,
        'has_next':               page_num < total_pages,
        'event_dates_json':       event_dates_json,
        'recent_posts':           recent_posts,
    })


def blog_detail(request, slug):
    import markdown as md
    post = get_object_or_404(Post, slug=slug, status='PUBLISHED')
    body_html = md.markdown(post.body, extensions=['extra', 'nl2br'])

    prev_post = Post.objects.filter(
        status='PUBLISHED', published_at__lt=post.published_at
    ).order_by('-published_at').first()
    next_post = Post.objects.filter(
        status='PUBLISHED', published_at__gt=post.published_at
    ).order_by('published_at').first()

    comments = post.comments.select_related('user').all()
    like_count = post.likes.count()
    user_liked = (
        request.user.is_authenticated and
        post.likes.filter(user=request.user).exists()
    )

    return render(request, 'blog/detail.html', {
        'post':       post,
        'body_html':  body_html,
        'prev_post':  prev_post,
        'next_post':  next_post,
        'comments':   comments,
        'like_count': like_count,
        'user_liked': user_liked,
    })


@login_required
@require_POST
def blog_comment_add(request, slug):
    post = get_object_or_404(Post, slug=slug, status='PUBLISHED')
    body = request.POST.get('body', '').strip()
    if body:
        PostComment.objects.create(post=post, user=request.user, body=body[:1000])
    return redirect('blog_detail', slug=slug)


@login_required
@require_POST
def blog_like_toggle(request, slug):
    post = get_object_or_404(Post, slug=slug, status='PUBLISHED')
    like = PostLike.objects.filter(post=post, user=request.user).first()
    if like:
        like.delete()
    else:
        PostLike.objects.create(post=post, user=request.user)
    return redirect('blog_detail', slug=slug)


# ── Shop Views ───────────────────────────────────────────────────────────────

def shop_landing(request):
    """Product listing with optional category filter."""
    category = request.GET.get('category', '')
    products = Product.objects.filter(is_active=True)
    if category:
        products = products.filter(category=category.upper())

    categories = Product.CATEGORY_CHOICES
    context = {
        'products': products,
        'categories': categories,
        'current_category': category.upper() if category else '',
    }
    return render(request, 'shop/landing.html', context)


def product_detail(request, slug):
    """Single product page with image gallery and variant picker."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    variants = product.variants.all()
    images = product.images.all()

    # Build available sizes and colors for the picker
    sizes = list(dict.fromkeys(v.size for v in variants))
    colors = list(dict.fromkeys(v.color for v in variants if v.color))

    # Variant data as JSON for frontend
    variant_data = json.dumps([
        {
            'sku': v.sku,
            'size': v.size,
            'color': v.color,
            'stock': v.stock,
            'price': str(v.effective_price),
        }
        for v in variants
    ])

    context = {
        'product': product,
        'images': images,
        'sizes': sizes,
        'colors': colors,
        'variant_data': variant_data,
    }
    return render(request, 'shop/product_detail.html', context)


def _get_cart(request):
    """Return the session cart as {sku: quantity}."""
    return request.session.get('cart', {})


def _get_cart_items(request):
    """Resolve cart SKUs to variant objects with quantities."""
    cart = _get_cart(request)
    if not cart:
        return [], Decimal('0.00')

    items = []
    subtotal = Decimal('0.00')
    for sku, qty in cart.items():
        try:
            variant = ProductVariant.objects.select_related('product').get(sku=sku)
        except ProductVariant.DoesNotExist:
            continue
        price = variant.effective_price
        line_total = price * qty
        items.append({
            'variant': variant,
            'quantity': qty,
            'unit_price': price,
            'line_total': line_total,
        })
        subtotal += line_total
    return items, subtotal


def cart(request):
    """Cart page — view and update items."""
    if request.method == 'POST':
        action = request.POST.get('action')
        sku = request.POST.get('sku')
        cart_data = _get_cart(request)

        if action == 'update' and sku:
            try:
                qty = int(request.POST.get('quantity', 0))
            except ValueError:
                qty = 0
            if qty > 0:
                cart_data[sku] = qty
            else:
                cart_data.pop(sku, None)

        elif action == 'remove' and sku:
            cart_data.pop(sku, None)

        request.session['cart'] = cart_data
        return redirect('cart')

    items, subtotal = _get_cart_items(request)
    shipping_method = request.session.get('shipping_method', 'PICKUP')
    shipping_cost = Decimal('10.00') if shipping_method == 'STANDARD' else Decimal('0.00')
    total = subtotal + shipping_cost

    context = {
        'cart_items': items,
        'subtotal': subtotal,
        'shipping_method': shipping_method,
        'shipping_cost': shipping_cost,
        'total': total,
        'cart_count': sum(item['quantity'] for item in items),
    }
    return render(request, 'shop/cart.html', context)


@require_POST
def cart_add(request):
    """Add a variant to the session cart."""
    sku = request.POST.get('sku')
    try:
        qty = int(request.POST.get('quantity', 1))
    except ValueError:
        qty = 1

    if not sku or qty < 1:
        return redirect('shop')

    # Validate variant exists and has stock
    try:
        variant = ProductVariant.objects.get(sku=sku)
    except ProductVariant.DoesNotExist:
        return redirect('shop')

    cart_data = _get_cart(request)
    current = cart_data.get(sku, 0)
    new_qty = min(current + qty, variant.stock)  # cap at available stock
    if new_qty > 0:
        cart_data[sku] = new_qty
    request.session['cart'] = cart_data

    # If AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'cart_count': sum(cart_data.values())})

    return redirect('cart')


@require_POST
def checkout(request):
    """Create a Stripe Checkout Session and redirect."""
    items, subtotal = _get_cart_items(request)
    if not items:
        return redirect('cart')

    # Save shipping method choice
    shipping_method = request.POST.get('shipping_method', 'PICKUP')
    request.session['shipping_method'] = shipping_method
    shipping_cost = Decimal('10.00') if shipping_method == 'STANDARD' else Decimal('0.00')

    stripe.api_key = settings.STRIPE_SECRET_KEY

    line_items = []
    for item in items:
        v = item['variant']
        name = v.product.name
        if v.size:
            name += f' — {v.size}'
        if v.color:
            name += f' / {v.color}'
        line_items.append({
            'price_data': {
                'currency': 'aud',
                'unit_amount': int(item['unit_price'] * 100),
                'product_data': {'name': name},
            },
            'quantity': item['quantity'],
        })

    # Add shipping as a line item if applicable
    if shipping_cost > 0:
        line_items.append({
            'price_data': {
                'currency': 'aud',
                'unit_amount': int(shipping_cost * 100),
                'product_data': {'name': 'Standard Shipping'},
            },
            'quantity': 1,
        })

    # Build metadata
    metadata = {
        'shipping_method': shipping_method,
    }
    if request.user.is_authenticated:
        metadata['user_id'] = str(request.user.pk)

    checkout_params = {
        'mode': 'payment',
        'line_items': line_items,
        'success_url': request.build_absolute_uri('/shop/checkout/success/') + '?session_id={CHECKOUT_SESSION_ID}',
        'cancel_url': request.build_absolute_uri('/shop/checkout/cancel/'),
        'metadata': metadata,
    }

    # Collect shipping address for standard shipping
    if shipping_method == 'STANDARD':
        checkout_params['shipping_address_collection'] = {
            'allowed_countries': ['AU'],
        }

    if request.user.is_authenticated and request.user.email:
        checkout_params['customer_email'] = request.user.email

    try:
        session = stripe.checkout.Session.create(**checkout_params)
        return redirect(session.url)
    except stripe.error.StripeError:
        logger.exception('Stripe checkout session creation failed')
        return redirect('cart')


def checkout_success(request):
    """Order confirmation page after successful Stripe payment."""
    session_id = request.GET.get('session_id', '')
    order = None
    if session_id:
        order = Order.objects.filter(stripe_session_id=session_id).first()
        if not order:
            # Webhook hasn't fired yet (common in local dev) — fetch from Stripe and create now
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                stripe_session = stripe.checkout.Session.retrieve(session_id)
                if stripe_session.payment_status == 'paid':
                    # Serialize to plain dict so _handle_checkout_completed works uniformly
                    session_dict = json.loads(str(stripe_session))
                    _handle_checkout_completed(session_dict)
                    order = Order.objects.filter(stripe_session_id=session_id).first()
            except Exception:
                logger.exception('Failed to retrieve Stripe session %s on success page', session_id)

    # Clear cart on success
    if 'cart' in request.session:
        del request.session['cart']
    request.session.pop('shipping_method', None)

    context = {'order': order}
    return render(request, 'shop/checkout_success.html', context)


def checkout_cancel(request):
    """Checkout was cancelled — return to cart."""
    return render(request, 'shop/checkout_cancel.html')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        logger.warning('Stripe webhook signature verification failed')
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        _handle_checkout_completed(session)

    return HttpResponse(status=200)


def _handle_checkout_completed(session):
    """Create Order + OrderItems from a completed Stripe checkout session."""
    # Avoid duplicate orders
    if Order.objects.filter(stripe_session_id=session['id']).exists():
        return

    metadata = session.get('metadata', {})
    shipping_method = metadata.get('shipping_method', 'PICKUP')
    user_id = metadata.get('user_id')

    # Get shipping details
    shipping_name = ''
    shipping_address = ''
    shipping_details = session.get('shipping_details')
    if shipping_details:
        shipping_name = shipping_details.get('name', '')
        addr = shipping_details.get('address', {})
        parts = [addr.get('line1', ''), addr.get('line2', ''),
                 addr.get('city', ''), addr.get('state', ''),
                 addr.get('postal_code', ''), addr.get('country', '')]
        shipping_address = ', '.join(p for p in parts if p)

    shipping_cost = Decimal('10.00') if shipping_method == 'STANDARD' else Decimal('0.00')
    total_amount = Decimal(session['amount_total']) / 100
    subtotal = total_amount - shipping_cost

    from django.contrib.auth.models import User
    user = None
    if user_id:
        user = User.objects.filter(pk=user_id).first()

    order = Order.objects.create(
        order_number=Order.generate_order_number(),
        user=user,
        email=session.get('customer_details', {}).get('email', ''),
        status='PAID',
        stripe_session_id=session['id'],
        stripe_payment_intent=session.get('payment_intent', ''),
        shipping_name=shipping_name,
        shipping_address=shipping_address,
        shipping_method=shipping_method,
        shipping_cost=shipping_cost,
        subtotal=subtotal,
        total=total_amount,
        paid_at=timezone.now(),
    )

    # Retrieve line items from Stripe to create OrderItems
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        line_items = stripe.checkout.Session.list_line_items(session['id'])
        for item in line_items.get('data', []):
            description = item.get('description', '')
            quantity = item.get('quantity', 1)
            unit_amount = Decimal(item['amount_total']) / 100 / quantity if quantity else Decimal('0')
            line_total = Decimal(item['amount_total']) / 100

            # Skip the shipping line item
            if description == 'Standard Shipping':
                continue

            # Try to match variant
            size = ''
            color = ''
            sku = ''
            product = None
            # Parse "Product Name — Size / Color" format
            parts = description.split(' — ')
            product_name = parts[0] if parts else description
            if len(parts) > 1:
                variant_parts = parts[1].split(' / ')
                size = variant_parts[0] if variant_parts else ''
                color = variant_parts[1] if len(variant_parts) > 1 else ''

            # Try to find the variant
            variant_qs = ProductVariant.objects.select_related('product').filter(
                product__name=product_name, size=size
            )
            if color:
                variant_qs = variant_qs.filter(color=color)
            variant = variant_qs.first()

            if variant:
                sku = variant.sku
                product = variant.product
                # Decrement stock
                variant.stock = max(0, variant.stock - quantity)
                variant.save()

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product_name,
                variant_sku=sku,
                size=size,
                color=color,
                quantity=quantity,
                unit_price=unit_amount,
                line_total=line_total,
            )
    except Exception:
        logger.exception('Failed to create order items from Stripe session')

    _send_order_confirmation(order)


def _send_order_confirmation(order):
    """Send an order confirmation email to the customer."""
    recipient = order.email or (order.user.email if order.user else None)
    if not recipient:
        return
    context = {'order': order}
    subject = render_to_string('shop/email/order_confirmation_subject.txt', context).strip()
    body_txt = render_to_string('shop/email/order_confirmation.txt', context)
    body_html = render_to_string('shop/email/order_confirmation.html', context)
    msg = EmailMultiAlternatives(subject, body_txt, settings.DEFAULT_FROM_EMAIL, [recipient])
    msg.attach_alternative(body_html, 'text/html')
    try:
        msg.send()
    except Exception:
        logger.exception('Failed to send order confirmation email for %s', order.order_number)


@login_required
def account(request):
    """User account / profile page."""
    from django.db.models import Q
    from allauth.socialaccount.models import SocialAccount

    recent_orders = Order.objects.filter(
        Q(user=request.user) | Q(email=request.user.email)
    ).exclude(status='PENDING').distinct().order_by('-created_at')[:5]

    social = {a.provider: a for a in SocialAccount.objects.filter(user=request.user)}
    google = social.get('google')
    strava = social.get('strava')

    # Best available avatar
    avatar_url = ''
    if google:
        avatar_url = google.get_avatar_url() or ''
    if not avatar_url and strava:
        avatar_url = strava.extra_data.get('profile_medium', '')

    # Best available display name
    display_name = request.user.get_full_name()
    if not display_name and strava:
        ed = strava.extra_data
        display_name = f"{ed.get('firstname', '')} {ed.get('lastname', '')}".strip()
    if not display_name:
        display_name = request.user.username

    # Best available email label
    email = request.user.email
    if not email and strava:
        email = strava.extra_data.get('username', '')

    return render(request, 'account/account.html', {
        'recent_orders': recent_orders,
        'google_account': google,
        'strava_account': strava,
        'avatar_url': avatar_url,
        'display_name': display_name,
        'email': email,
    })


@login_required
def order_list(request):
    """User's order history — matches by user FK or email."""
    from django.db.models import Q
    orders = Order.objects.filter(
        Q(user=request.user) | Q(email=request.user.email)
    ).exclude(status='PENDING').distinct().order_by('-created_at')
    return render(request, 'shop/orders.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    """Single order detail — accessible by owner user or matching email."""
    from django.db.models import Q
    order = get_object_or_404(
        Order, order_number=order_number
    )
    if order.user != request.user and order.email != request.user.email:
        from django.http import Http404
        raise Http404
    return render(request, 'shop/order_detail.html', {'order': order})


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        '',
        f'Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
