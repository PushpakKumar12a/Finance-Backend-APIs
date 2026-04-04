from django.urls import path
from records import views

urlpatterns = [
    path('records/', views.RecListCreateAPI.as_view(), name='record-list'),
    path('records/<int:pk>/', views.RecDetailAPI.as_view(), name='record-detail'),
]
