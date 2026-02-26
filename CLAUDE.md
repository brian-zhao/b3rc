# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Workflow

Before starting work, write a detailed implementation plan in `claude/tasks/TASK_NAME.md`. The plan should include a clear breakdown of implementation steps, the reasoning behind your approach, and a list of specific tasks. Focus on an MVP. Ask for review before proceeding — do not implement until the plan is approved.

As you work, keep the plan updated. After completing each task, append a description of the changes made. This ensures progress is clear and can be handed off if needed.

## Project Overview

B3RC (B3 Running Club) is a Django web application deployed on Google App Engine. It uses a minimal project structure with no separate Django apps — all views and URL routing live at the project level in `b3rc_site/`.

## Development Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run development server
python manage.py runserver

# Database migrations
python manage.py makemigrations && python manage.py migrate

# Collect static files
python manage.py collectstatic
```

## Deployment

```bash
gcloud app deploy
gcloud app logs tail -s default
```

## Environment Variables

- `DJANGO_SECRET_KEY`: Falls back to an insecure dev key if not set
- `DJANGO_SETTINGS_MODULE`: Set to `b3rc_site.settings`
