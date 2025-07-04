from django.urls import path
from . import views

urlpatterns = [
    path('<int:org_pk>/', views.survey_detail, name='survey_detail'),
    path('<int:org_pk>/create/', views.survey_create, name='survey_create'),
    path('<int:org_pk>/edit/', views.survey_edit, name='survey_edit'),
    path('<int:org_pk>/themes/create/', views.theme_create, name='theme_create'),
    path('<int:org_pk>/themes/<int:theme_pk>/questions/create/', views.question_create, name='question_create'),
]