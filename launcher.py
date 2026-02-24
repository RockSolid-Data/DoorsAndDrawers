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
  - Monitors browser heartbeat and shuts down when the tab is closed
"""

import os
import sys
import time
import signal
import webbrowser
import threading


def _fix_frozen_stdio():
    """
    When frozen as a GUI exe (base='gui'), sys.stdout and sys.stderr are None
    because there is no console. Redirect them to a log file so Django's
    management commands (migrate, etc.) and print() don't crash.
    """
    if getattr(sys, 'frozen', False) and (sys.stdout is None or sys.stderr is None):
        log_dir = _app_data_dir()
        log_path = os.path.join(log_dir, 'launcher.log')
        log_file = open(log_path, 'a', encoding='utf-8')
        if sys.stdout is None:
            sys.stdout = log_file
        if sys.stderr is None:
            sys.stderr = log_file


def _base_dir():
    """Return the directory that contains bundled resources (templates, staticfiles, etc.)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _get_version():
    """Read version from the VERSION file."""
    version_file = os.path.join(_base_dir(), 'VERSION')
    try:
        with open(version_file) as f:
            return f.read().strip()
    except FileNotFoundError:
        return 'unknown'


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


def _heartbeat_monitor(timeout=10):
    """
    Watch for browser heartbeat pings. If no heartbeat is received within
    `timeout` seconds, the browser tab was likely closed — shut down the server.
    """
    from core.views.lifecycle import get_last_heartbeat

    grace_period = 15
    time.sleep(grace_period)

    while True:
        last = get_last_heartbeat()
        if last is not None:
            elapsed = time.monotonic() - last
            if elapsed > timeout:
                print(f'[launcher] No heartbeat for {elapsed:.0f}s — browser tab closed. Shutting down.')
                os.kill(os.getpid(), signal.SIGTERM)
                return
        time.sleep(2)


def main():
    _fix_frozen_stdio()
    _configure_environment()

    import django
    django.setup()

    _run_migrations()
    _seed_defaults()

    from waitress import serve
    from DoorsAndDrawers.wsgi import application

    version = _get_version()
    host = '127.0.0.1'
    port = 8000
    url = f'http://{host}:{port}'

    print(f'[launcher] Doors and Drawers v{version}')
    print(f'[launcher] Starting server at {url}')
    print('[launcher] Server will shut down automatically when the browser tab is closed.')

    threading.Thread(target=_heartbeat_monitor, daemon=True).start()
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
