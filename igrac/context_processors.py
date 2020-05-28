from .utilities import get_default_filter_by_group

def resource_urls(request):
    """Global values to pass to templates"""

    defaults = dict(
        DEFAULT_GROUP_FILTER=get_default_filter_by_group(request.user)
    )

    return defaults
