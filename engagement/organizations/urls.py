from django.urls import path
from . import views

urlpatterns = [
    path('', views.organization_list, name='organization_list'),
    path('create/', views.organization_create, name='organization_create'),
    path('<int:pk>/', views.organization_detail, name='organization_detail'),
    path('<int:pk>/edit/', views.organization_edit, name='organization_edit'),
    path('<int:pk>/org-chart/', views.organization_org_chart, name='organization_org_chart'),
]