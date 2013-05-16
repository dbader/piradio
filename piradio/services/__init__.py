import base
import clock
import weather

from base import deliver_pending_notifications

def stop_all():
    # Fixme hack, should have a service registry
    if clock._instance:
        clock._instance.stop()
    if weather._instance:
        weather._instance.stop()
