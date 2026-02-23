#!/usr/bin/env python3
"""
Doors and Drawers - Desktop Application Launcher

Entry point for the frozen (cx_Freeze) application that:
  - Sets up the Django environment
  - Detects frozen mode (cx_Freeze .exe) vs development
  - Stores the SQLite database in %LOCALAPPDATA%\\DoorsAndDrawers
  - Runs database migrations on every startup
  - Seeds default application settings when the DB is fresh
  - Opens the default browser to the app
  - Starts the Waitress WSGI server on 127.0.0.1:8000
"""

import os
import sys
import time
import webbrowser
import threading


def _base_dir():
    """Return the directory that contains bundled resources (templates, staticfiles, etc.)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _app_data_dir():
    """Return (and create) the per-user data directory for DB and logs."""
    root = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
    data_dir = os.path.join(root, 'DoorsAndDrawers')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def _configure_environment():
    """Set environment variables and sys.path *before* Django is imported."""
    base = _base_dir()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DoorsAndDrawers.settings')
    if base not in sys.path:
        sys.path.insert(0, base)


def _run_migrations():
    """Apply any pending database migrations."""
    from django.core.management import call_command
    print('[launcher] Running database migrations ...')
    call_command('migrate', '--run-syncdb', verbosity=1)
    print('[launcher] Migrations complete.')


def _seed_defaults():
    """Create default application settings if the tables are empty."""
    try:
        from scripts.create_default_settings import main as create_defaults
        print('[launcher] Checking / creating default settings ...')
        create_defaults()
    except Exception as exc:
        print(f'[launcher] Warning: could not seed defaults: {exc}')


def _open_browser(url, delay=2.0):
    """Open the user's default browser after a short delay."""
    def _open():
        time.sleep(delay)
        webbrowser.open(url)
    threading.Thread(target=_open, daemon=True).start()


def main():
    _configure_environment()

    import django
    django.setup()

    _run_migrations()
    _seed_defaults()

    from waitress import serve
    from DoorsAndDrawers.wsgi import application

    host = '127.0.0.1'
    port = 8000
    url = f'http://{host}:{port}'

    print(f'[launcher] Starting Doors and Drawers at {url}')
    print('[launcher] Press Ctrl+C to stop the server.')

    _open_browser(url)

    serve(
        application,
        host=host,
        port=port,
        threads=4,
        connection_limit=100,
        channel_timeout=120,
        url_scheme='http',
    )


if __name__ == '__main__':
    main()
