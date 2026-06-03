from search.models import SearchRequest


def sidebar_context(request):
    if not request.user.is_authenticated:
        return {}
    return {
        "total_searches": SearchRequest.objects.for_user(request.user).count(),
    }
