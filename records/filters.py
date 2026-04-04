"""
Django-filter FilterSet for FinancialRecord.
Enables filtering by type, category, date range, and amount range.
"""

import django_filters

from records.models import Record

class RecFilter(django_filters.FilterSet):
    """
    Query parameters:
      - type:       exact match (income / expense)
      - category:   case-insensitive contains
      - date_from:  records on or after this date
      - date_to:    records on or before this date
      - amount_min: minimum amount
      - amount_max: maximum amount
    """
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    amt_min = django_filters.NumberFilter(field_name='amt', lookup_expr='gte')
    amt_max = django_filters.NumberFilter(field_name='amt', lookup_expr='lte')
    cat = django_filters.CharFilter(field_name='cat', lookup_expr='icontains')

    class Meta:
        model = Record
        fields = ['type', 'cat', 'date_from', 'date_to', 'amt_min', 'amt_max']
