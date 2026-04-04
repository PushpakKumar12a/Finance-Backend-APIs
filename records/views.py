"""
Views for financial record CRUD operations.

Access control:
  - GET (list/detail):        Viewer, Analyst, Admin
  - POST/PATCH/DELETE:        Admin only
"""

from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from accounts.permissions import IsAdmin, IsViewerOrAbove
from records.filters import RecFilter
from records.models import Record
from records.serializers import RecSerializer

@extend_schema(tags=['Records'])
class RecListCreateAPI(generics.ListCreateAPIView):
    """
    GET  /api/records/      — List records (all authenticated users)
    POST /api/records/      — Create a record (admin only)

    Supports:
      - Filtering: type, category, date_from, date_to, amount_min, amount_max
      - Search:    description, category
      - Ordering:  date, amount, created_at
      - Pagination: page number (20 per page)
    """
    serializer_class = RecSerializer
    filterset_class = RecFilter
    search_fields = ['desc', 'cat']
    ordering_fields = ['date', 'amt', 'created_at']

    def get_queryset(self):
        return Record.objects.select_related('user').all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsViewerOrAbove()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@extend_schema(tags=['Records'])
class RecDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/records/<id>/  — View a record (all authenticated users)
    PATCH  /api/records/<id>/  — Update a record (admin only)
    DELETE /api/records/<id>/  — Soft-delete a record (admin only)
    """
    serializer_class = RecSerializer

    def get_queryset(self):
        return Record.objects.select_related('user').all()

    def get_permissions(self):
        if self.request.method in ('PATCH', 'PUT', 'DELETE'):
            return [IsAdmin()]
        return [IsViewerOrAbove()]

    def destroy(self, request, *args, **kwargs):
        record = self.get_object()
        record.soft_delete()
        return Response(
            {'message': 'Record has been deleted.'},
            status=status.HTTP_200_OK,
        )