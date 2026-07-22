from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_admin, name='dashboard_admin'),
    path('suscripciones/', views.lista_suscripciones, name='suscripciones'),
    path('pagos/', views.lista_pagos, name='pagos'),
    path('pagos/<int:pago_id>/aprobar/', views.aprobar_pago, name='aprobar_pago'),
    path('pagos/<int:pago_id>/rechazar/', views.rechazar_pago, name='rechazar_pago'),
    path('cupones/', views.lista_cupones, name='cupones'),
]
