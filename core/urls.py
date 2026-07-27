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
    path('planes/', views.lista_planes, name='planes'),
    path('planes/nuevo/', views.crear_plan, name='crear_plan'),
    path('planes/<int:plan_id>/editar/', views.editar_plan, name='editar_plan'),
    path('planes/<int:plan_id>/eliminar/', views.eliminar_plan, name='eliminar_plan'),
]
