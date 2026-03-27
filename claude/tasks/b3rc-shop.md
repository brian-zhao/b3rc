# B3RC Shop — Design Document

**Date:** 2026-03-27
**Status:** Draft — awaiting review

---

## 1. Vision

A members-first shop for B3RC club apparel, race kits, and curated running gear — integrated directly into the existing site. The shop should feel like a natural extension of the editorial aesthetic: clean product cards, minimal checkout friction, and deep integration with the club identity (Strava login, member pricing, race-day kit bundles).

This is **not** a general-purpose e-commerce platform. It is a focused club shop that reinforces community belonging and funds the club's operations.

---

## 2. User Accounts & Social Login

### Authentication Providers

| Provider | Why | Scopes |
|----------|-----|--------|
| **Google** | Most universal, many members already use it | `email`, `profile` |
| **Apple** | Required for iOS users, privacy-friendly | `email`, `name` |
| **Strava** | Core to the running community — unlocks activity-based features | `read`, `profile:read_all`, `activity:read` |

### Account Model

```
UserProfile
├── user              → Django User (email as username)
├── display_name      → str (from social provider or manual)
├── avatar_url        → str (from social provider)
├── phone             → str (optional, for delivery updates)
├── strava_id         → str (nullable, linked Strava athlete ID)
├── membership_tier   → enum: FREE | MEMBER | FOUNDING
├── joined_at         → datetime
│
├── ShippingAddress[] (one-to-many)
│   ├── label         → str ("Home", "Work", etc.)
│   ├── full_name     → str
│   ├── line_1        → str
│   ├── line_2        → str (optional)
│   ├── city          → str
│   ├── state         → str
│   ├── postcode      → str
│   ├── country        → str (default: "AU")
│   └── is_default    → bool
│
└── stripe_customer_id → str (created on first purchase)
```

### Auth Flow

1. User clicks "Sign in" → modal with Google / Apple / Strava buttons
2. OAuth redirect → callback creates or links Django user
3. If Strava: store `strava_id` and athlete name, refresh token for activity sync
4. First login prompts for shipping address (skippable, required at checkout)
5. Session stored in signed cookies (existing setup)

### Library

Use **`django-allauth`** — mature, supports Google/Apple/Strava out of the box, handles account linking (one user, multiple social providers).

---

## 3. Product Catalog

### Product Model

```
Product
├── slug              → str (URL-safe, unique)
├── name              → str ("B3RC Racing Singlet")
├── short_description → str (one-liner for cards)
├── description       → text (markdown, for detail page)
├── category          → enum: APPAREL | ACCESSORIES | RACE_KIT | LIMITED_DROP
├── base_price        → decimal (AUD)
├── member_price      → decimal (nullable — member-only discount)
├── is_active         → bool
├── is_preorder       → bool (for upcoming drops)
├── preorder_eta      → str (nullable, e.g. "Ships late April 2026")
├── sort_order        → int
├── created_at        → datetime
│
├── ProductImage[] (one-to-many, ordered)
│   ├── image         → file (GCS)
│   ├── alt_text      → str
│   └── order         → int
│
├── ProductVariant[] (one-to-many)
│   ├── size          → str ("XS", "S", "M", "L", "XL", "XXL")
│   ├── color         → str (nullable, "Black", "White", "Teal")
│   ├── sku           → str (unique)
│   ├── stock         → int (0 = sold out)
│   └── price_override → decimal (nullable — overrides base if set)
│
└── ProductTag[] (many-to-many)
    └── tag           → str ("new", "bestseller", "race-day", "winter")
```

### Categories

| Category | Examples |
|----------|----------|
| **Apparel** | Racing singlets, tees, shorts, long sleeves, jackets, caps |
| **Accessories** | Socks, headbands, bottles, tote bags, stickers |
| **Race Kit** | Bundled singlet + shorts + socks at discounted bundle price |
| **Limited Drop** | Seasonal or collab items with countdown timer, limited stock |

### Size Guide

Dedicated size guide component per product category (different measurements for tops vs shorts vs caps). Displayed as a modal/drawer from the product detail page. Include a "How to measure" illustration.

---

## 4. Shopping Experience

### Pages

| Route | Page | Description |
|-------|------|-------------|
| `/shop/` | Shop landing | Hero banner + category filter + product grid |
| `/shop/<slug>/` | Product detail | Image gallery, size/color picker, add to cart, description |
| `/shop/cart/` | Cart | Line items, quantity adjust, promo code input, subtotal |
| `/shop/checkout/` | Checkout | Address form, shipping method, Stripe payment |
| `/shop/checkout/success/` | Confirmation | Order summary, estimated delivery, "Track order" link |
| `/shop/orders/` | Order history | List of past orders with status badges |
| `/shop/orders/<id>/` | Order detail | Line items, tracking, delivery status |
| `/account/` | Profile | Edit name, email, addresses, linked social accounts |
| `/account/addresses/` | Address book | Manage saved shipping addresses |

### Shop Landing (`/shop/`)

```
+--------------------------------------------------+
|  [Hero Banner — seasonal campaign image]         |
|  "GEAR UP. BREAK 3."                            |
+--------------------------------------------------+
|  Filter bar: ALL | APPAREL | ACCESSORIES | KITS  |
+--------------------------------------------------+
|  [Product]  [Product]  [Product]                 |
|  [Product]  [Product]  [Product]                 |
|  ...                                             |
+--------------------------------------------------+
```

- 3-column grid on desktop, 2 on tablet, 1 on mobile
- Each product card: image, name, price (crossed-out if member discount), "MEMBER PRICE" badge
- Hover: subtle image zoom (consistent with existing card hover style)
- Filter is sticky below navbar on scroll
- "SOLD OUT" overlay on out-of-stock items
- "PRE-ORDER" badge on upcoming items

### Product Detail (`/shop/<slug>/`)

```
+------------------------+---------------------------+
|                        |  B3RC RACING SINGLET      |
|   [Image Gallery]      |  $65.00  ($55.00 members) |
|   • main image         |                           |
|   • thumbnails below   |  Size: [XS] S M L XL XXL |
|                        |  Color: ● Black  ○ White  |
|                        |                           |
|                        |  [ADD TO CART]            |
|                        |                           |
|                        |  ✓ Free pickup at training|
|                        |  🚚 $10 flat rate shipping |
|                        |                           |
+------------------------+---------------------------+
|  Description (markdown rendered)                   |
|  Size Guide (expandable)                          |
+---------------------------------------------------+
```

### Cart (`/shop/cart/`)

- Slide-out drawer on desktop (triggered by cart icon in navbar), full page on mobile
- Line items with thumbnail, name, size/color, quantity +/-, unit price, line total
- Promo code input field
- Subtotal, shipping estimate, total
- "CHECKOUT" primary CTA
- "Continue shopping" secondary link
- Empty state: "Your cart is empty" with link back to shop

---

## 5. Payments — Stripe Integration

### Approach

Use **Stripe Checkout (hosted)** for MVP — redirects to Stripe's hosted payment page. This avoids PCI compliance complexity and gives us Apple Pay, Google Pay, and card payments for free.

### Flow

1. User clicks "Checkout" in cart
2. Backend creates a `stripe.checkout.Session` with:
   - Line items (products, quantities, prices)
   - Shipping address collection (if not saved)
   - Customer email
   - Success/cancel redirect URLs
   - Metadata: `order_id`, `user_id`
3. User is redirected to Stripe Checkout
4. On success: Stripe redirects to `/shop/checkout/success/?session_id=...`
5. Webhook `checkout.session.completed` confirms payment and creates the order

### Stripe Objects

| Stripe Object | Usage |
|---------------|-------|
| `Customer` | Created per user, stored as `stripe_customer_id` |
| `Checkout Session` | One per checkout attempt |
| `Payment Intent` | Created automatically by Checkout |
| `Webhook` | `checkout.session.completed`, `payment_intent.payment_failed` |

### Webhook Events to Handle

| Event | Action |
|-------|--------|
| `checkout.session.completed` | Create Order, mark as PAID, send confirmation email |
| `payment_intent.payment_failed` | Mark order as FAILED, notify user |
| `charge.refunded` | Mark order as REFUNDED |

### Env Variables

```
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## 6. Order Model

```
Order
├── order_number       → str (auto-generated, e.g. "B3RC-20260327-0042")
├── user               → FK UserProfile
├── status             → enum: PENDING | PAID | PROCESSING | SHIPPED | DELIVERED | CANCELLED | REFUNDED
├── stripe_session_id  → str
├── stripe_payment_intent → str
│
├── shipping_name      → str (snapshot at order time)
├── shipping_address   → text (snapshot — full formatted address)
├── shipping_method    → enum: PICKUP | STANDARD
├── tracking_number    → str (nullable)
├── tracking_url       → str (nullable)
│
├── subtotal           → decimal
├── shipping_cost      → decimal
├── discount           → decimal
├── promo_code         → str (nullable)
├── total              → decimal
├── currency           → str (default: "AUD")
│
├── created_at         → datetime
├── paid_at            → datetime (nullable)
├── shipped_at         → datetime (nullable)
├── delivered_at       → datetime (nullable)
│
├── OrderItem[] (one-to-many)
│   ├── product        → FK Product (nullable, preserved even if product deleted)
│   ├── product_name   → str (snapshot)
│   ├── variant_sku    → str (snapshot)
│   ├── size           → str (snapshot)
│   ├── color          → str (snapshot)
│   ├── quantity       → int
│   ├── unit_price     → decimal (snapshot)
│   └── line_total     → decimal
│
└── OrderEvent[] (one-to-many, audit trail)
    ├── status         → str
    ├── note           → str
    └── created_at     → datetime
```

---

## 7. Shipping & Fulfillment

| Method | Cost | Details |
|--------|------|---------|
| **Free pickup at training** | $0 | Collected at Wednesday or Sunday session. Default for Sydney members. |
| **Standard shipping** | $10 flat | Australia Post, 3-5 business days. Tracking number provided. |
| **Express shipping** | $15 flat | Australia Post Express, 1-2 business days. |

- Pickup orders show a QR code on the confirmation page and in the order detail — scanned by a committee member at training to mark as collected.
- Admin marks orders as SHIPPED with tracking number → user gets email notification.
- International shipping: Phase 2 (not MVP). Show "Australia only" message for now.

---

## 8. Membership & Pricing Tiers

| Tier | Who | Discount | How to Get |
|------|-----|----------|------------|
| **Free** | Anyone who creates an account | No discount | Sign up |
| **Member** | Active club members | 15% off all apparel | Committee adds via admin, or verified via Strava club membership |
| **Founding** | Original B3RC members | 20% off + early access to drops | Manual assignment by admin |

### Strava-Verified Membership (Phase 2)

If the user has linked their Strava account and is a member of the "Breaking 3 Running Club" Strava club, automatically upgrade them to MEMBER tier. Check on login and periodically via a background sync.

---

## 9. Promo Codes & Discounts

```
PromoCode
├── code              → str (uppercase, unique, e.g. "LAUNCH20")
├── discount_type     → enum: PERCENTAGE | FIXED_AMOUNT
├── discount_value    → decimal (e.g. 20 for 20%, or 10 for $10 off)
├── min_order_amount  → decimal (nullable)
├── max_uses          → int (nullable, unlimited if null)
├── times_used        → int
├── valid_from        → datetime
├── valid_until       → datetime (nullable)
├── is_active         → bool
└── applies_to        → enum: ALL | APPAREL | ACCESSORIES | SPECIFIC_PRODUCTS
```

- Applied at cart level before checkout
- Validation: check expiry, usage limit, minimum order, category match
- Only one promo code per order (MVP)

---

## 10. Notifications & Emails

| Trigger | Channel | Content |
|---------|---------|---------|
| Account created | Email | Welcome + "Complete your profile" CTA |
| Order confirmed | Email | Order summary, items, estimated delivery |
| Order shipped | Email | Tracking number + link |
| Order ready for pickup | Email | QR code + next training session details |
| Limited drop launching | Email (opt-in) | Product preview, launch time, "Set reminder" |
| Back in stock | Email (opt-in) | "Your size is back in stock" for wishlisted items |

Use **Django's built-in email** with a transactional provider (SendGrid or AWS SES via SMTP). HTML email templates matching the B3RC editorial style.

---

## 11. Additional Features

### 11.1 Wishlist

- Heart icon on product cards and detail page
- Saved per user in Firestore
- "Back in stock" notification trigger
- Wishlist page under `/account/wishlist/`

### 11.2 Race-Day Kit Builder

A guided flow where members assembling a race kit get a bundle discount:

1. Pick a singlet → pick shorts → pick socks (optional accessories)
2. See the bundle price vs individual total
3. Add entire bundle to cart as a single line item

Great for new members gearing up for their first race.

### 11.3 Limited Drops with Countdown

- Admin sets a `launch_at` datetime on a product
- Product appears on shop with "DROPPING [date]" badge and countdown timer
- At launch time, product becomes purchasable
- Low stock: show "Only X left" urgency indicator
- Founding members get 24-hour early access

### 11.4 Training Pickup Slot

When a user selects "Free pickup at training":
- Show a dropdown: "Next Wednesday (Apr 2)" / "Next Sunday (Apr 6)"
- This helps the committee know which session to bring the order to
- After the selected session passes without collection, auto-remind via email

### 11.5 Strava Milestone Rewards (Phase 2)

Reward members who hit milestones with shop discounts:

| Milestone | Reward |
|-----------|--------|
| First run logged with B3RC Strava club | 10% off first order |
| 50 runs logged | Free B3RC socks (add to cart, auto-applied) |
| Sub-3 marathon logged | Exclusive "SUB3" tee unlocked in shop |
| 100km month | 15% off next order |

Requires Strava activity sync via refresh token + webhook.

### 11.6 Group Orders

For teams entering a relay or race together:
- A "captain" creates a group order and shares a link
- Each member picks their size/color and adds their address
- Captain reviews and submits a single payment (or split payment)
- Useful for team kits, matching race gear

### 11.7 Gift Cards

```
GiftCard
├── code        → str (auto-generated)
├── balance     → decimal (AUD)
├── original    → decimal
├── purchaser   → FK User
├── recipient_email → str
├── redeemed_by → FK User (nullable)
├── created_at  → datetime
├── expires_at  → datetime (12 months)
```

- Sold as a product in the shop ($25, $50, $100)
- Delivered via email with a branded card design
- Redeemed at checkout like a promo code
- Partial redemption supported (remaining balance shown)

### 11.8 Product Reviews

- Star rating (1-5) + optional text review
- Only users who purchased the item can review
- Displayed on product detail page
- Average rating shown on product card
- Helps future buyers pick the right size ("runs small", "true to size")

### 11.9 Referral Program (Phase 2)

- Each member gets a unique referral code
- New user signs up via referral → both get $10 shop credit
- Credited as a gift card balance
- Tracked in admin dashboard

### 11.10 Admin Dashboard Enhancements

Beyond Django admin, add a lightweight dashboard at `/admin/shop/`:

- **Orders overview:** Today's orders, pending shipments, revenue this week/month
- **Low stock alerts:** Variants with stock < 5
- **Popular products:** Best sellers this month
- **Pickup queue:** Orders pending pickup at next training session
- **Export:** CSV export of orders for accounting

---

## 12. Data Storage

### Firestore Collections

All shop data persists in Firestore (consistent with the existing architecture). SQLite remains as an ephemeral cache.

| Collection | Document Key | Synced to SQLite? |
|------------|-------------|-------------------|
| `products` | slug | Yes (for admin + reads) |
| `product_images` | auto-id | Yes |
| `product_variants` | sku | Yes |
| `orders` | order_number | Yes |
| `order_items` | auto-id | Yes |
| `user_profiles` | user_id | Yes |
| `promo_codes` | code | Yes |
| `gift_cards` | code | Yes |
| `wishlists` | user_id | Firestore-only (no ORM needed) |
| `reviews` | auto-id | Yes |

The existing signal-based sync pattern (`post_save` → Firestore, `sync_from_firestore` on startup) extends to all new models.

---

## 13. Security Considerations

- **Stripe Checkout (hosted):** No card data touches our server. PCI-DSS SAQ A.
- **Webhook verification:** All Stripe webhooks verified via `stripe.Webhook.construct_event()` with the signing secret.
- **CSRF:** Django's built-in CSRF protection on all forms.
- **Auth:** `django-allauth` handles OAuth state, PKCE, and token storage.
- **Address data:** Stored in Firestore with Firestore Security Rules restricting access to the owning user.
- **Admin access:** All shop admin views require `is_staff` permission.
- **Price integrity:** Prices are calculated server-side from the product catalog, never from the client. Cart total is recomputed at checkout.
- **Rate limiting:** Add rate limiting on checkout endpoint to prevent abuse.

---

## 14. Tech Stack Additions

| Component | Library / Service |
|-----------|-------------------|
| Social auth | `django-allauth` (Google, Apple, Strava providers) |
| Payments | Stripe Checkout (hosted) + `stripe` Python SDK |
| Email | Django email backend + SendGrid SMTP |
| Image handling | Pillow (existing) + GCS (existing) |
| Markdown rendering | `markdown` (for product descriptions) |
| QR codes | `qrcode` (for pickup order confirmation) |

### New Environment Variables

```yaml
# app.yaml env_variables additions
STRIPE_SECRET_KEY: "sk_live_..."
STRIPE_PUBLISHABLE_KEY: "pk_live_..."
STRIPE_WEBHOOK_SECRET: "whsec_..."
GOOGLE_OAUTH_CLIENT_ID: "...apps.googleusercontent.com"
GOOGLE_OAUTH_CLIENT_SECRET: "..."
APPLE_CLIENT_ID: "..."
APPLE_CLIENT_SECRET: "..."
STRAVA_CLIENT_ID: "..."
STRAVA_CLIENT_SECRET: "..."
SENDGRID_API_KEY: "SG...."
```

---

## 15. URL Structure

```
/shop/                          → Shop landing (product grid)
/shop/<slug>/                   → Product detail
/shop/cart/                     → Cart (full page on mobile)
/shop/checkout/                 → Redirect to Stripe Checkout
/shop/checkout/success/         → Order confirmation
/shop/checkout/cancel/          → Checkout cancelled, return to cart
/shop/orders/                   → Order history (auth required)
/shop/orders/<order_number>/    → Order detail (auth required)
/shop/kit-builder/              → Race-day kit builder

/account/                       → Profile settings (auth required)
/account/addresses/             → Address book (auth required)
/account/wishlist/              → Saved items (auth required)

/auth/login/                    → Login page (social buttons)
/auth/signup/                   → Redirects to login (social-only signup)
/auth/callback/<provider>/      → OAuth callback (handled by allauth)
/auth/logout/                   → Logout

/api/stripe/webhook/            → Stripe webhook endpoint (POST only)
/api/cart/add/                  → Add to cart (AJAX)
/api/cart/update/               → Update quantity (AJAX)
/api/cart/remove/               → Remove item (AJAX)
```

---

## 16. Phased Rollout

### Phase 1 — MVP (Target: 4-6 weeks)

- [x] User accounts with Google login (`django-allauth`) — Apple not configured (needs Apple dev credentials)
- [x] Product catalog (CRUD via Django admin)
- [x] Product listing page with category filter
- [x] Product detail page with image gallery + size picker
- [x] Cart (session-based for guests, persistent for logged-in users)
- [x] Stripe Checkout integration — keys loaded from `app.secrets.yaml` via env vars
- [x] Order model + webhook handler
- [x] Order confirmation page + email — console backend in dev; set `EMAIL_BACKEND` + `SENDGRID_API_KEY` env vars for prod
- [x] Shipping: pickup at training + flat-rate standard
- [x] Basic order history page
- [x] Admin: manage products, view orders, update status

### Phase 2 — Member Features (2-3 weeks after MVP)

- [ ] Strava login + account linking
- [ ] Membership tiers + member pricing
- [ ] Promo codes
- [ ] Wishlist + back-in-stock notifications
- [ ] Limited drops with countdown + early access
- [ ] Gift cards
- [ ] Product reviews

### Phase 3 — Community & Growth (ongoing)

- [ ] Strava milestone rewards
- [ ] Race-day kit builder
- [ ] Group orders
- [ ] Referral program
- [ ] Admin dashboard with analytics
- [ ] International shipping
- [ ] Inventory management alerts

---

## 17. Design — Visual Direction

The shop inherits the existing B3RC editorial aesthetic. Key principles:

- **Product photography:** Shot on clean backgrounds, consistent lighting, lifestyle shots on runners in training. Same cinematic feel as the hero imagery.
- **Cards:** Match existing card style — white bg, subtle border, 12px radius, hover zoom on image.
- **Typography:** Product names in 600 weight, prices in 400, "MEMBER PRICE" labels in uppercase 13px accent green.
- **Color usage:** Accent green (`#00A550`) for sale/member price badges, CTAs. Deep teal (`#003D4C`) for primary buttons.
- **Cart drawer:** Slides in from right on desktop, half-width, dark overlay on rest of page.
- **Checkout:** Clean, single-column form. Stripe handles the payment UI.
- **Mobile:** Full-bleed product images, sticky "Add to Cart" bar at bottom of product detail page.
- **Empty states:** Illustrated with brand-consistent line art ("Your cart is empty — gear up for race day").

---

## 18. Open Questions

1. **Inventory management:** Who handles stock counts — admin manually, or integrate with a supplier/fulfillment API?
2. **Product sourcing:** Custom-printed apparel (e.g. via Printful) or pre-ordered bulk from a supplier?
3. **Tax:** Do we need to charge GST? (Yes if annual revenue > $75K AUD — likely not initially, but should be configurable.)
4. **Returns policy:** What's the return/exchange window? Needed for checkout legal text.
5. **Email provider:** SendGrid (free tier: 100 emails/day) vs AWS SES vs Mailgun?
6. **Domain:** Shop at `b3rc.com.au/shop/` or separate `shop.b3rc.com.au`?
