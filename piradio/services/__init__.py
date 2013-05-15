import base
import clock

from base import deliver_pending_notifications

def stop_all():
    # Fixme hack, should have a service registry
    if clock._instance:
        clock._instance.stop()
