from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import SearchRequest
from .forms import CadastroForm


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
        status__in=[SearchRequest.Status.PENDING, SearchRequest.Status.PROCESSING]
    )[:5]

    completed = all_searches.filter(
        status=SearchRequest.Status.COMPLETED
    )[:5]

    recent = all_searches[:10]

    # Estatísticas
    stats = {
        'total': all_searches.count(),
        'processing': all_searches.filter(
            status__in=[SearchRequest.Status.PENDING, SearchRequest.Status.PROCESSING]
        ).count(),
        'completed': all_searches.filter(status=SearchRequest.Status.COMPLETED).count(),
        'failed': all_searches.filter(status=SearchRequest.Status.FAILED).count(),
    }

    context = {
        'processing_searches': processing,
        'completed_searches': completed,
        'recent_searches': recent,
        'stats': stats,
    }

    return render(request, 'core/dashboard.html', context)


@login_required
def search_list(request):
    """Lista todas as pesquisas do usuário."""
    searches = SearchRequest.objects.filter(user=request.user)

    # Filtro por status (opcional via query param)
    status_filter = request.GET.get('status')
    if status_filter:
        searches = searches.filter(status=status_filter)

    context = {
        'searches': searches,
        'current_filter': status_filter,
    }

    return render(request, 'core/search_list.html', context)


@login_required
def new_search(request):
    """Página para criar nova pesquisa."""
    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        area = request.POST.get('area', '').strip() or None
        modality = request.POST.get('modality', '').strip() or None
        state = request.POST.get('state', '').strip() or None

        if query:
            SearchRequest.objects.create(
                user=request.user,
                query=query,
                area=area,
                modality=modality,
                state=state,
                status=SearchRequest.Status.PENDING
            )
            messages.success(request, f'Pesquisa "{query}" criada com sucesso!')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'O termo de busca é obrigatório.')

    return render(request, 'core/new_search.html')


def logout_view(request):
    """Logout do usuário."""
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login')


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    form = CadastroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
        return redirect('login')
    return render(request, 'registration/register.html', {'form': form})
