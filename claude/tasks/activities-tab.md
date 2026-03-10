# Task: Add Activities Tab Content

## Goal
Add "Wednesday Quality" and "Sunday Long Run" information to the Activities section of the site.

## Approach
The simplest MVP is to add tab-based navigation within `home.html` so clicking "Activities" in the navbar shows an activities section with two run types. No backend/database is needed — this is static content.

## Implementation Steps

1. **Update `home.html`**
   - Change the "Activities" nav link to anchor to `#activities`
   - Add an `#activities` section inside `<main>` with two cards:
     - **Wednesday Quality** — description of the midweek speed/quality workout
     - **Sunday Long Run** — description of the weekend long run

2. **Update `static/css/style.css`**
   - Style the activities section and cards to match the existing dark/overlay aesthetic

## What I Need From You
- What details should be shown for each run?
  - **Wednesday Quality**: time, location, description, pace group info?
  - **Sunday Long Run**: same — time, location, description?
- Or should I use placeholder text for now?

## Out of Scope (for now)
- Backend model for activities
- Admin UI to manage activities
- Other nav tabs (About, Sponsors, Find Us)