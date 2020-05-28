from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .utilities import get_default_filter_by_group

@receiver(user_logged_in)
def set_default_filter_by_group(sender, request, user, **kwargs):
    """
    Set layer/map/document to be filtered by user's group by default
    """

    request.session['filter_by_group'] = get_default_filter_by_group(request.user)
