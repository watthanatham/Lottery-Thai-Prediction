from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Lottery Draws
    path('draws/', views.draw_list, name='draw_list'),
    path('draws/add/', views.draw_add, name='draw_add'),
    path('draws/<int:pk>/edit/', views.draw_edit, name='draw_edit'),
    path('draws/<int:pk>/delete/', views.draw_delete, name='draw_delete'),

    # Analysis
    path('analysis/run/', views.analysis_run, name='analysis_run'),
    path('analysis/<int:pk>/', views.analysis_detail, name='analysis_detail'),
    path('analysis/<int:pk>/generate/<str:number>/<str:option>/', views.generate_six_digits, name='generate_six_digits'),
    path('analysis/', views.analysis_history, name='analysis_history'),

    # Checklist
    path('checklist/', views.checklist, name='checklist'),
    path('checklist/verify/<int:session_pk>/', views.verify_session, name='verify_session'),

    # Formula Settings
    path('formulas/', views.formula_settings, name='formula_settings'),

    # HTMX Partials
    path('partials/formula-table/<int:session_pk>/', views.partial_formula_table, name='partial_formula_table'),
]
