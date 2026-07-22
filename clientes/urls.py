from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Pacientes
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/nuevo/', views.crear_paciente, name='crear_paciente'),
    path('pacientes/<int:paciente_id>/', views.detalle_paciente, name='detalle_paciente'),
    path('pacientes/<int:paciente_id>/editar/', views.editar_paciente, name='editar_paciente'),

    # Historias clinicas
    path('pacientes/<int:paciente_id>/historias/nueva/', views.crear_historia, name='crear_historia'),

    # Fotos
    path('pacientes/<int:paciente_id>/fotos/subir/', views.subir_foto, name='subir_foto'),

    # Odontograma
    path('pacientes/<int:paciente_id>/odontograma/', views.odontograma, name='odontograma'),
    path('pacientes/<int:paciente_id>/odontograma/registrar/', views.registrar_odontograma, name='registrar_odontograma'),

    # Citas y calendario
    path('calendario/', views.calendario, name='calendario'),
    path('calendario/eventos/', views.eventos_calendario_json, name='eventos_calendario_json'),
    path('citas/nueva/', views.crear_cita, name='crear_cita'),
    path('citas/<int:cita_id>/mover/', views.mover_cita, name='mover_cita'),
    path('citas/<int:cita_id>/editar/', views.editar_cita, name='editar_cita'),

    # Cotizaciones
    path('cotizaciones/', views.lista_cotizaciones, name='lista_cotizaciones'),
    path('cotizaciones/nueva/<int:paciente_id>/', views.crear_cotizacion, name='crear_cotizacion'),
    path('cotizaciones/<int:cotizacion_id>/', views.detalle_cotizacion, name='detalle_cotizacion'),
    path('cotizaciones/<int:cotizacion_id>/aprobar/', views.aprobar_cotizacion, name='aprobar_cotizacion'),
    path('cotizaciones/<int:cotizacion_id>/pdf/', views.cotizacion_pdf, name='cotizacion_pdf'),

    # Pagos
    path('pagos/', views.lista_pagos_pacientes, name='lista_pagos'),
    path('pagos/nuevo/<int:paciente_id>/', views.registrar_pago, name='registrar_pago'),

    # Procedimientos (catalogo)
    path('procedimientos/', views.lista_procedimientos, name='lista_procedimientos'),
    path('procedimientos/nuevo/', views.crear_procedimiento, name='crear_procedimiento'),
    path('procedimientos/<int:procedimiento_id>/editar/', views.editar_procedimiento, name='editar_procedimiento'),

    # Usuarios/doctores del consultorio
    path('equipo/', views.lista_equipo, name='lista_equipo'),
    path('equipo/nuevo/', views.crear_doctor, name='crear_doctor'),
]
