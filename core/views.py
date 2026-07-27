from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, ProtectedError

from .models import Consultorio, Suscripcion, Pago, Cupon, Plan


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


# ---------------------------------------------------------------------------
# Planes
# ---------------------------------------------------------------------------
@login_required
@user_passes_test(es_super_admin)
def lista_planes(request):
    planes = Plan.objects.all()
    return render(request, 'core/planes.html', {'planes': planes})


@login_required
@user_passes_test(es_super_admin)
def crear_plan(request):
    if request.method == 'POST':
        Plan.objects.create(
            nombre=request.POST.get('nombre', '').strip(),
            precio_mensual=request.POST.get('precio_mensual'),
            limite_pacientes=request.POST.get('limite_pacientes') or 100,
            limite_doctores=request.POST.get('limite_doctores') or 1,
            limite_storage_gb=request.POST.get('limite_storage_gb') or 1,
            activo=request.POST.get('activo') == 'on',
            orden=request.POST.get('orden') or 0,
        )
        messages.success(request, 'Plan creado.')
        return redirect('core:planes')
    return render(request, 'core/plan_form.html')


@login_required
@user_passes_test(es_super_admin)
def editar_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    if request.method == 'POST':
        plan.nombre = request.POST.get('nombre', plan.nombre).strip()
        plan.precio_mensual = request.POST.get('precio_mensual', plan.precio_mensual)
        plan.limite_pacientes = request.POST.get('limite_pacientes', plan.limite_pacientes)
        plan.limite_doctores = request.POST.get('limite_doctores', plan.limite_doctores)
        plan.limite_storage_gb = request.POST.get('limite_storage_gb', plan.limite_storage_gb)
        plan.activo = request.POST.get('activo') == 'on'
        plan.orden = request.POST.get('orden', plan.orden)
        plan.save()
        messages.success(request, 'Plan actualizado.')
        return redirect('core:planes')
    return render(request, 'core/plan_form.html', {'plan': plan})


@login_required
@user_passes_test(es_super_admin)
def eliminar_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    if request.method == 'POST':
        nombre = plan.nombre
        try:
            plan.delete()
            messages.success(request, f'Plan "{nombre}" eliminado.')
        except ProtectedError:
            messages.error(
                request,
                f'No se puede eliminar "{nombre}": hay consultorios con suscripciones a este plan. '
                f'Marcalo como inactivo en su lugar.'
            )
        return redirect('core:planes')
    return render(request, 'core/plan_confirmar_eliminar.html', {'plan': plan})
