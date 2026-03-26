# B3RC Admin Guide — Managing Site Images & Video

## Accessing the Admin

1. Go to `/en/admin/` (e.g. http://localhost:8111/en/admin/)
2. Log in with your admin credentials

## Adding Images / Video

1. In the admin dashboard, click **Site Media**
2. Click **Add Site Media** (top right)
3. Fill in:
   - **Slot** — Choose where the media appears on the site:
     - `Home — Hero Background` — The large background at the top of the homepage (supports images or video)
     - `Home — About Section Image` — The image next to the "About Us" text
     - `Home — Photo Strip 1 (left)` — Left photo in the 3-photo strip
     - `Home — Photo Strip 2 (center)` — Center photo in the 3-photo strip
     - `Home — Photo Strip 3 (right)` — Right photo in the 3-photo strip
   - **File** — Click "Choose File" and select an image (`.jpg`, `.png`, `.webp`) or video (`.mp4` for hero only)
   - **Alt text** — A short description of the image (for accessibility and SEO)
4. Click **Save**

The image/video will appear on the site immediately. If no media is uploaded for a slot, a gradient placeholder is shown instead.

## Editing / Replacing Media

### From the list view (quickest)
1. Go to **Site Media** — you'll see all uploaded slots in a table
2. You can change the **File** and **Alt text** directly in the list
3. Click **Save** at the bottom

### From the detail view
1. Click on a slot name to open it
2. Change the file or alt text
3. Click **Save**

## Deleting Media

1. Click on the slot name to open it
2. Click **Delete** at the bottom left
3. Confirm deletion

The slot will revert to showing a gradient placeholder on the site.

## Recommended Image Sizes

| Slot | Recommended Size | Format |
|------|-----------------|--------|
| Hero Background | 1920x1080 or wider | `.jpg`, `.webp`, or `.mp4` |
| About Section | 800x600 (4:3 ratio) | `.jpg`, `.webp` |
| Photo Strip (each) | 800x600 (4:3 ratio) | `.jpg`, `.webp` |

Tips:
- Keep images under 500KB for fast loading (compress with tools like TinyPNG)
- Hero video should be under 5MB, muted, and looping (it auto-plays)
- Use `.webp` format for best quality-to-size ratio
