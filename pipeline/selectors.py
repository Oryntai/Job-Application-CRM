from .models import ApplicationEvent


def events_for_application(application):
    return ApplicationEvent.objects.filter(application=application).select_related("event_type")
