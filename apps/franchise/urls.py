"""
Franchise application URLs
"""
from django.urls import path
from apps.franchise.views import (
    FranchiseApplicationCreateView,
    FranchiseApplicationListView,
    FranchiseApplicationDetailView,
    FranchiseApplicationUpdateView,
    FranchiseApplicationDeleteView,
)

app_name = 'franchise'

urlpatterns = [
    # Public endpoint for creating applications
    path('applications/', FranchiseApplicationCreateView.as_view(), name='application_create'),
    
    # Admin-only endpoints
    path('applications/list/', FranchiseApplicationListView.as_view(), name='application_list'),
    path('applications/<int:id>/', FranchiseApplicationDetailView.as_view(), name='application_detail'),
    path('applications/<int:id>/update/', FranchiseApplicationUpdateView.as_view(), name='application_update'),
    path('applications/<int:id>/delete/', FranchiseApplicationDeleteView.as_view(), name='application_delete'),
]
