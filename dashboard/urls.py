from django.urls import path
from dashboard import views

urlpatterns = [
    path('dashboard/summary/', views.SummaryAPI.as_view(), name='dashboard-summary'),
    path('dashboard/category-breakdown/', views.CatBreakdownAPI.as_view(), name='dashboard-category-breakdown'),
    path('dashboard/trends/', views.TrendsAPI.as_view(), name='dashboard-trends'),
    path('dashboard/recent-activity/', views.RecentActivityAPI.as_view(), name='dashboard-recent-activity'),
]
