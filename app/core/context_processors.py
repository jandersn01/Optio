from search.models import Favorite, SearchRequest


def sidebar_context(request):
    if not request.user.is_authenticated:
        return {}
    
    is_analyst = request.user.groups.filter(name='Analista').exists()
    return {
        "total_searches": SearchRequest.objects.for_user(request.user).count(),
        "total_favorites": Favorite.objects.filter(user=request.user).count(),
        "is_analyst": is_analyst,
    }

