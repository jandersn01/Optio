from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from search.models import SearchRequest
from search.choices import SearchStatus
from .forms import CadastroForm


@login_required
def dashboard(request):
    user = request.user

    all_searches = SearchRequest.objects.filter(user=user)

    processing = all_searches.filter(
        status__in=[SearchStatus.PENDING, SearchStatus.PROCESSING]
    )[:5]

    completed = all_searches.filter(
        status=SearchStatus.COMPLETED
    )[:5]

    recent = all_searches[:10]

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
