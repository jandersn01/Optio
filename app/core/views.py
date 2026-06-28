from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext
from django.views.decorators.http import require_POST
from search.models import SearchRequest
from search.choices import SearchArea, SearchModality, SearchStatus
from .forms import CadastroForm, NotificationPreferenceForm, UserIdentityForm
from .models import NotificationPreference


@login_required
def dashboard(request):
    user = request.user
    all_searches = SearchRequest.objects.for_user(user)

    stats = {
        'total': all_searches.count(),
        'processing': all_searches.filter(
            status__in=[SearchStatus.PENDING, SearchStatus.PROCESSING]
        ).count(),
        'completed': all_searches.filter(status=SearchStatus.COMPLETED).count(),
        'failed': all_searches.filter(status=SearchStatus.FAILED).count(),
        'total_results': all_searches.aggregate(s=Sum('results_count'))['s'] or 0,
    }

    return render(request, 'core/dashboard.html', {
        'recent_searches': all_searches[:5],
        'stats': stats,
        'total_searches': stats['total'],
    })


def logout_view(request):
    logout(request)
    messages.info(request, gettext('Você saiu da sua conta.'))
    return redirect('login')


@login_required
def preferences(request):
    preference, _created = NotificationPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        identity_form = UserIdentityForm(request.POST, instance=request.user)
        pref_form = NotificationPreferenceForm(request.POST, instance=preference)
        if identity_form.is_valid() and pref_form.is_valid():
            identity_form.save()
            pref_form.save()
            messages.success(request, gettext('Preferências salvas com sucesso.'))
            return redirect('core:preferences')
    else:
        identity_form = UserIdentityForm(instance=request.user)
        pref_form = NotificationPreferenceForm(instance=preference)

    return render(request, 'core/preferences.html', {
        'identity_form': identity_form,
        'pref_form': pref_form,
        'preference': preference,
        'area_choices': SearchArea.choices,
        'modality_choices': SearchModality.choices,
    })


@login_required
@require_POST
def delete_search_history(request):
    SearchRequest.objects.for_user(request.user).update(
        is_deleted=True,
        deleted_at=timezone.now(),
    )
    messages.success(request, gettext('Histórico de buscas apagado.'))
    return redirect('core:preferences')


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    form = CadastroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, gettext('Conta criada com sucesso! Faça login para continuar.'))
        return redirect('login')
    return render(request, 'registration/register.html', {'form': form})
