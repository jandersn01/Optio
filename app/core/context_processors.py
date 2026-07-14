from search.models import Favorite, SearchRequest


def sidebar_context(request):
    if not request.user.is_authenticated:
        return {}
    
    return {
        "total_searches": SearchRequest.objects.for_user(request.user).count(),
        "total_favorites": Favorite.objects.filter(user=request.user).count(),
        "is_analyst": request.user.has_perm('core.view_metrics'),
    }

