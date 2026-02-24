"""
Server lifecycle views: heartbeat and shutdown.

The browser sends a heartbeat ping every few seconds. When the tab is closed
the pings stop, and the monitor thread in launcher.py shuts down the process.
"""

import os
import signal
import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

_last_heartbeat_lock = threading.Lock()
_last_heartbeat = None  # float – time.monotonic()


def get_last_heartbeat():
    with _last_heartbeat_lock:
        return _last_heartbeat


@require_GET
def heartbeat(request):
    import time
    with _last_heartbeat_lock:
        global _last_heartbeat
        _last_heartbeat = time.monotonic()
    return JsonResponse({'status': 'ok'})


@csrf_exempt
@require_POST
def shutdown(request):
    """Immediate shutdown requested by the browser (beforeunload fallback)."""
    def _kill():
        os.kill(os.getpid(), signal.SIGTERM)
    threading.Timer(0.5, _kill).start()
    return JsonResponse({'status': 'shutting_down'})
