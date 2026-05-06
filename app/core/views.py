from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from search.models import SearchRequest
from search.choices import SearchStatus


@login_required
def dashboard(request):
    """
    Dashboard principal do usuário.
    Exibe pesquisas em andamento, concluídas e recentes.
    """
    user = request.user

    # Pesquisas do usuário
    all_searches = SearchRequest.objects.filter(user=user)

    # Separar por status
    processing = all_searches.filter(
        status__in=[SearchStatus.PENDING, SearchStatus.PROCESSING]
    )[:5]

    completed = all_searches.filter(
        status=SearchStatus.COMPLETED
    )[:5]

    recent = all_searches[:10]

    # Estatísticas
    stats = {
        'total': all_searches.count(),
        'processing': all_searches.filter(
            status__in=[SearchStatus.PENDING, SearchStatus.PROCESSING]
        ).count(),
        'completed': all_searches.filter(status=SearchStatus.COMPLETED).count(),
        'failed': all_searches.filter(status=SearchStatus.FAILED).count(),
    }

    context = {
        'processing_searches': processing,
        'completed_searches': completed,
        'recent_searches': recent,
        'stats': stats,
    }

    return render(request, 'core/dashboard.html', context)

def logout_view(request):
    """Logout do usuário."""
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login')
