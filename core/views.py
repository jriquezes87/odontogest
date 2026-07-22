from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum

from .models import Consultorio, Suscripcion, Pago, Cupon


def es_super_admin(user):
    return user.is_authenticated and getattr(user, 'rol', None) == 'super_admin'


@login_required
@user_passes_test(es_super_admin)
def dashboard_admin(request):
    total_consultorios = Consultorio.objects.exclude(schema_name='public').count()
    suscripciones_activas = Suscripcion.objects.filter(estado='activa').count()
    suscripciones_trial = Suscripcion.objects.filter(estado='trial').count()
    pagos_pendientes = Pago.objects.filter(estado='pendiente').count()

    ingresos_mes = Pago.objects.filter(
        estado='aprobado',
        fecha_aprobacion__month=timezone.now().month,
        fecha_aprobacion__year=timezone.now().year,
    ).aggregate(total=Sum('monto'))['total'] or 0

    contexto = {
        'total_consultorios': total_consultorios,
        'suscripciones_activas': suscripciones_activas,
        'suscripciones_trial': suscripciones_trial,
        'pagos_pendientes': pagos_pendientes,
        'ingresos_mes': ingresos_mes,
    }
    return render(request, 'core/dashboard_admin.html', contexto)


@login_required
@user_passes_test(es_super_admin)
def lista_suscripciones(request):
    suscripciones = Suscripcion.objects.select_related('consultorio', 'plan').all()
    return render(request, 'core/suscripciones.html', {'suscripciones': suscripciones})


@login_required
@user_passes_test(es_super_admin)
def lista_pagos(request):
    pagos = Pago.objects.select_related('suscripcion__consultorio').order_by('-fecha_pago')
    return render(request, 'core/pagos.html', {'pagos': pagos})


@login_required
@user_passes_test(es_super_admin)
def aprobar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    pago.estado = 'aprobado'
    pago.fecha_aprobacion = timezone.now()
    pago.save()

    suscripcion = pago.suscripcion
    suscripcion.estado = 'activa'
    suscripcion.save()

    messages.success(request, f'Pago de {suscripcion.consultorio.nombre_practica} aprobado.')
    return redirect('core:pagos')


@login_required
@user_passes_test(es_super_admin)
def rechazar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    pago.estado = 'rechazado'
    pago.save()
    messages.info(request, 'Pago rechazado.')
    return redirect('core:pagos')


@login_required
@user_passes_test(es_super_admin)
def lista_cupones(request):
    cupones = Cupon.objects.all()
    return render(request, 'core/cupones.html', {'cupones': cupones})
