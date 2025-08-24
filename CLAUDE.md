# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Plan and Review

Before starting work
Before you begin, write a detaield implementation plan in a file named claude/tasks/TASK_NAME.md.

This plan should include:

A clear, detailed breakdown of the implementation steps.

The reasoning behind your approach

A list of specific tasks.

Focus on a Minimum Viable Product (MVP) to avoid over-planning. Once the plan is ready, please ask me to review it. Do not proceed with the implementation until I have approved the plan.

## While Implementing

As you work, keep the plan updated. After you complete a task. apppend a detailed descripiton of the changes you've made to the plan. This ensures that the progress and next steps are clear and can be easily handed over to other engineers if needed.

## Project Overview

This is B3RC (B3 Running Club), a Django web application for a running club website. The project is configured for deployment on Google App Engine.

## Architecture

- **Django Project**: Standard Django structure with `b3rc_site` as the main project package
- **Templates**: HTML templates in `/templates/` directory (project-level templates)
- **Static Files**: CSS, images, and admin assets in `/static/` with collected files in `/staticfiles/`
- **Database**: SQLite for local development (`db.sqlite3`)
- **Deployment**: Google App Engine with `app.yaml` configuration

## Key Files

- `main.py`: App Engine entry point that imports the WSGI application
- `manage.py`: Standard Django management script
- `b3rc_site/settings.py`: Django settings with environment variable support
- `b3rc_site/views.py`: View functions (currently just a home view)
- `b3rc_site/urls.py`: URL routing configuration
- `app.yaml`: Google App Engine configuration
- `requirements.txt`: Python dependencies (Django>=4.2, gunicorn)

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python manage.py runserver

# Database operations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

### Google App Engine Deployment
```bash
# Deploy to App Engine
gcloud app deploy

# View logs
gcloud app logs tail -s default
```

## Project Structure

The codebase follows Django's standard project layout:
- Main project configuration in `b3rc_site/`
- Templates at project root level in `templates/`
- Static files organized in `static/` with admin assets
- App Engine configuration via `app.yaml`

## Environment Variables

- `DJANGO_SECRET_KEY`: Secret key for Django (falls back to insecure dev key)
- `DJANGO_SETTINGS_MODULE`: Set to `b3rc_site.settings`