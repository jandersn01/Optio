from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext
from django.views.decorators.http import require_POST
from search.models import SearchRequest, SavedAlert
from search.choices import SearchArea, SearchModality, SearchStatus
from .forms import CadastroForm, NotificationPreferenceForm, UserIdentityForm
from .models import NotificationPreference, NotificationSent
from . import services as metrics_services


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

    week_ago = timezone.now() - timedelta(days=7)
    new_programs = (
        NotificationSent.objects
        .filter(user=user, sent_at__gte=week_ago)
        .order_by('-sent_at')[:6]
    )

    alerts = list(SavedAlert.objects.filter(user=user, active=True)[:3])

    return render(request, 'core/dashboard.html', {
        'recent_searches': all_searches[:5],
        'stats': stats,
        'total_searches': stats['total'],
        'new_programs': new_programs,
        'alerts': alerts,
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

@login_required
@permission_required('core.view_metrics', login_url='core:dashboard')
def metrics_dashboard(request):
    # Captura o período da URL (default: 30)
    try:
        days = int(request.GET.get('period', 30))
    except ValueError:
        days = 30
        
    # Garante que só valores permitidos sejam lidos
    if days not in [7, 30, 365]:
        days = 30

    context = {
        'current_period': days, # Mandamos para o HTML para pintar o botão ativo
        'kpis': metrics_services.get_kpi_metrics(days=days),
        'status_distribution': metrics_services.get_search_status_distribuition(days=days),
        'daily_volume': metrics_services.get_daily_search_volume(days=days),
        'unmet_demand': metrics_services.get_unmet_demand_keywords(days=days, limit=5),
        'top_areas': metrics_services.get_top_monitored_areas(limit=5),
        'top_modalities': metrics_services.get_top_modalities(days=days, limit=5),
        'top_states': metrics_services.get_top_states(days=days, limit=5),
        'peak_hours': metrics_services.get_peak_hours(days=days),
    }
    return render(request, 'core/metrics_dashboard.html', context)