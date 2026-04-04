"""
Dashboard analytics views.

All endpoints require Analyst or Admin role.
All accept optional ?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD query params.
"""

from datetime import date

from django.db.models import Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce, TruncMonth
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAnalystOrAbove
from records.models import Record

def _get_date_filtered_qs(request):
    """
    Return a base queryset filtered by optional date_from / date_to
    query parameters.
    """
    qs = Record.objects.all()
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return qs


@extend_schema(tags=['Dashboard'])
class SummaryAPI(APIView):
    """
    GET /api/dashboard/summary/
    Returns: total_income, total_expenses, net_balance, total_records.
    """
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        qs = _get_date_filtered_qs(request)

        zero = Value(0, output_field=DecimalField())
        agg = qs.aggregate(
            inc=Coalesce(
                Sum('amt', filter=Q(type=Record.TxType.INCOME)),
                zero,
            ),
            exp=Coalesce(
                Sum('amt', filter=Q(type=Record.TxType.EXPENSE)),
                zero,
            ),
            recs=Count('id'),
        )
        agg['net'] = agg['inc'] - agg['exp']
        return Response(agg)

@extend_schema(tags=['Dashboard'])
class CatBreakdownAPI(APIView):
    """
    GET /api/dashboard/category-breakdown/
    Returns per-category totals grouped by type, e.g.:
    [
        {"category": "salary", "type": "income", "total": 5000, "count": 2},
        {"category": "rent",   "type": "expense", "total": 1200, "count": 1},
    ]
    """
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        qs = _get_date_filtered_qs(request)
        breakdown = (
            qs.values('cat', 'type')
            .annotate(
                total=Coalesce(Sum('amt'), Value(0, output_field=DecimalField())),
                count=Count('id'),
            )
            .order_by('cat', 'type')
        )
        return Response(list(breakdown))

@extend_schema(tags=['Dashboard'])
class TrendsAPI(APIView):
    """
    GET /api/dashboard/trends/
    Returns monthly income/expense totals:
    [
        {"month": "2026-01", "type": "income",  "total": 8000, "count": 3},
        {"month": "2026-01", "type": "expense", "total": 3500, "count": 5},
        ...
    ]
    """
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        qs = _get_date_filtered_qs(request)
        trends = (
            qs.annotate(month=TruncMonth('date'))
            .values('month', 'type')
            .annotate(
                total=Coalesce(Sum('amt'), Value(0, output_field=DecimalField())),
                count=Count('id'),
            )
            .order_by('month', 'type')
        )
        result = []
        for entry in trends:
            result.append({
                'month': entry['month'].strftime('%Y-%m') if entry['month'] else None,
                'type': entry['type'],
                'total': entry['total'],
                'count': entry['count'],
            })
        return Response(result)

@extend_schema(tags=['Dashboard'])
class RecentActivityAPI(APIView):
    """
    GET /api/dashboard/recent-activity/
    Returns the 10 most recent financial records.
    """
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        records = Record.objects.select_related('user').all()[:10]
        data = [
            {
                'id': r.id,
                'user': str(r.user),
                'amt': str(r.amt),
                'type': r.type,
                'cat': r.cat,
                'date': r.date.isoformat(),
                'desc': r.desc,
                'created_at': r.created_at.isoformat(),
            }
            for r in records
        ]
        return Response(data)