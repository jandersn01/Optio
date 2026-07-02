from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate, ExtractHour

from core.models import CustomUser
from search.models import SearchRequest, SavedAlert
from search.choices import SearchStatus, SearchArea, SearchModality, SearchStates_Br

def get_kpi_metrics(days=30) -> dict:
    now = timezone.now()
    current_start = now - timedelta(days=days)
    prev_start = current_start - timedelta(days=days)

    current_qs = SearchRequest.objects.filter(created_at__gte=current_start)
    prev_qs = SearchRequest.objects.filter(created_at__gte=prev_start, created_at__lt=current_start)

    current_total = current_qs.count()
    prev_total = prev_qs.count()

    growth = 0
    if prev_total > 0:
        growth = round(((current_total - prev_total) / prev_total) * 100, 1)
    elif current_total > 0:
        growth = 100.0

    failed = current_qs.filter(status=SearchStatus.FAILED).count()
    success_rate = 0
    if current_total > 0:
        success_rate = round(((current_total - failed) / current_total) * 100, 1)

    return {
        'period_days': days,
        'total_searches': current_total,
        'daily_average': round(current_total / days) if days > 0 else 0,
        'growth_pct': growth,
        'is_positive_growth': growth >= 0,
        'success_rate': success_rate,
        'active_alerts': SavedAlert.objects.filter(active=True).count(), # Snapshot Global
        'total_users': CustomUser.objects.count(), # Snapshot Global
    }

def get_search_status_distribuition(days=30) -> list[dict]:
    start_date = timezone.now() - timedelta(days=days)
    qs = SearchRequest.objects.filter(created_at__gte=start_date).values('status').annotate(total=Count('id')).order_by('-total')
    status_dict = dict(SearchStatus.choices)
    return [{'label': status_dict.get(item['status'], item['status']), 'total': item['total']} for item in qs]

def get_daily_search_volume(days=30) -> list[dict]:
    start_date = timezone.now() - timedelta(days=days)
    qs = (SearchRequest.objects.filter(created_at__gte=start_date)
          .annotate(date=TruncDate('created_at'))
          .values('date')
          .annotate(total=Count('id'))
          .order_by('date'))
    return [{'date': item['date'].strftime('%d/%m'), 'total': item['total']} for item in qs if item['date']]

def get_unmet_demand_keywords(days=30, limit=5) -> list[dict]:
    start_date = timezone.now() - timedelta(days=days)
    return list(SearchRequest.objects.filter(created_at__gte=start_date, status=SearchStatus.NO_RESULTS).values('keywords').annotate(total=Count('id')).order_by('-total')[:limit])

def get_top_monitored_areas(limit=5) -> list[dict]:
    qs = SavedAlert.objects.filter(active=True).values('area').annotate(total=Count('id')).order_by('-total')[:limit]
    area_dict = dict(SearchArea.choices)
    return [{'label': area_dict.get(item['area']) if item['area'] else 'Todas as áreas', 'total': item['total']} for item in qs]

def get_top_modalities(days=30, limit=5) -> list[dict]:
    start_date = timezone.now() - timedelta(days=days)
    qs = SearchRequest.objects.filter(created_at__gte=start_date).values('modality').annotate(total=Count('id')).order_by('-total')[:limit]
    mod_dict = dict(SearchModality.choices)
    return [{'label': mod_dict.get(item['modality']) if item['modality'] else 'Todas as Modalidades', 'total': item['total']} for item in qs]

def get_top_states(days=30, limit=5) -> list[dict]:
    start_date = timezone.now() - timedelta(days=days)
    qs = SearchRequest.objects.filter(created_at__gte=start_date).values('state').annotate(total=Count('id')).order_by('-total')[:limit]
    state_dict = dict(SearchStates_Br.choices)
    return [{'label': state_dict.get(item['state']) if item['state'] else 'Todo o Brasil', 'total': item['total']} for item in qs]

def get_peak_hours(days=30) -> list[dict]:
    start_date = timezone.now() - timedelta(days=days)
    qs = SearchRequest.objects.filter(created_at__gte=start_date).annotate(hour=ExtractHour('created_at')).values('hour').annotate(total=Count('id'))
    hours_map = {h: 0 for h in range(24)}
    for item in qs:
        if item['hour'] is not None:
            hours_map[int(item['hour'])] = item['total']
            
    result = []
    for h in range(24):
        result.append({'hour': f"{h:02d}h", 'total': hours_map[h]})
    return result