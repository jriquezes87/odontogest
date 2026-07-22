import json
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import (
    Paciente, HistoriaClinica, FotoPaciente, Procedimiento,
    Cotizacion, CotizacionItem, CuentaCobro, PagoPaciente,
    Cita, OdontogramaRegistro,
)
from cuentas.models import Usuario


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@login_required
def dashboard(request):
    hoy = timezone.now().date()

    citas_hoy_qs = Cita.objects.filter(fecha_hora__date=hoy).exclude(estado='cancelada')
    if request.user.es_doctor:
        citas_hoy_qs = citas_hoy_qs.filter(doctor=request.user)

    cotizaciones_pendientes = Cotizacion.objects.filter(estado='enviada')
    citas_por_crear = Cotizacion.objects.filter(estado='aprobada', cita_generada=False)

    ingresos_mes = PagoPaciente.objects.filter(
        fecha__month=hoy.month, fecha__year=hoy.year
    ).aggregate(total=Sum('monto'))['total'] or 0

    total_pacientes = Paciente.objects.filter(activo=True).count()

    contexto = {
        'citas_hoy': citas_hoy_qs.order_by('fecha_hora'),
        'cotizaciones_pendientes': cotizaciones_pendientes,
        'citas_por_crear': citas_por_crear,
        'ingresos_mes': ingresos_mes,
        'total_pacientes': total_pacientes,
    }
    return render(request, 'clientes/dashboard.html', contexto)


# ---------------------------------------------------------------------------
# Pacientes
# ---------------------------------------------------------------------------
@login_required
def lista_pacientes(request):
    query = request.GET.get('q', '').strip()
    pacientes = Paciente.objects.filter(activo=True)
    if query:
        pacientes = pacientes.filter(
            Q(cedula__icontains=query) |
            Q(nombres__icontains=query) |
            Q(apellidos__icontains=query)
        )
    return render(request, 'clientes/pacientes_lista.html', {'pacientes': pacientes, 'query': query})


@login_required
def crear_paciente(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula', '').strip()
        if Paciente.objects.filter(cedula=cedula).exists():
            messages.error(request, 'Ya existe un paciente registrado con esa cedula.')
            return render(request, 'clientes/paciente_form.html')

        paciente = Paciente.objects.create(
            cedula=cedula,
            nombres=request.POST.get('nombres', '').strip(),
            apellidos=request.POST.get('apellidos', '').strip(),
            fecha_nacimiento=request.POST.get('fecha_nacimiento') or None,
            telefono=request.POST.get('telefono', ''),
            telefono_whatsapp=request.POST.get('telefono_whatsapp', ''),
            correo=request.POST.get('correo', ''),
            direccion=request.POST.get('direccion', ''),
            doctor_responsable=request.user if request.user.es_doctor else None,
            alergias=request.POST.get('alergias', ''),
            antecedentes_medicos=request.POST.get('antecedentes_medicos', ''),
        )
        messages.success(request, f'Paciente {paciente.nombre_completo} registrado.')
        return redirect('clientes:detalle_paciente', paciente_id=paciente.id)

    return render(request, 'clientes/paciente_form.html')


@login_required
def detalle_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    contexto = {
        'paciente': paciente,
        'historias': paciente.historias.all()[:10],
        'fotos': paciente.fotos.all(),
        'cotizaciones': paciente.cotizaciones.all()[:10],
        'pagos': paciente.pagos.all()[:10],
        'total_pagado': paciente.pagos.aggregate(total=Sum('monto'))['total'] or 0,
    }
    return render(request, 'clientes/paciente_detalle.html', contexto)


@login_required
def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        paciente.nombres = request.POST.get('nombres', paciente.nombres)
        paciente.apellidos = request.POST.get('apellidos', paciente.apellidos)
        paciente.telefono = request.POST.get('telefono', paciente.telefono)
        paciente.telefono_whatsapp = request.POST.get('telefono_whatsapp', paciente.telefono_whatsapp)
        paciente.correo = request.POST.get('correo', paciente.correo)
        paciente.direccion = request.POST.get('direccion', paciente.direccion)
        paciente.alergias = request.POST.get('alergias', paciente.alergias)
        paciente.antecedentes_medicos = request.POST.get('antecedentes_medicos', paciente.antecedentes_medicos)
        paciente.save()
        messages.success(request, 'Datos del paciente actualizados.')
        return redirect('clientes:detalle_paciente', paciente_id=paciente.id)
    return render(request, 'clientes/paciente_form.html', {'paciente': paciente})


# ---------------------------------------------------------------------------
# Historias clinicas
# ---------------------------------------------------------------------------
@login_required
def crear_historia(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        HistoriaClinica.objects.create(
            paciente=paciente,
            doctor=request.user,
            motivo_consulta=request.POST.get('motivo_consulta', ''),
            diagnostico=request.POST.get('diagnostico', ''),
            tratamiento_realizado=request.POST.get('tratamiento_realizado', ''),
            observaciones=request.POST.get('observaciones', ''),
        )
        messages.success(request, 'Historia clinica agregada.')
        return redirect('clientes:detalle_paciente', paciente_id=paciente.id)
    return render(request, 'clientes/historia_form.html', {'paciente': paciente})


# ---------------------------------------------------------------------------
# Fotos
# ---------------------------------------------------------------------------
@login_required
def subir_foto(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST' and request.FILES.get('imagen'):
        FotoPaciente.objects.create(
            paciente=paciente,
            imagen=request.FILES['imagen'],
            momento=request.POST.get('momento', 'antes'),
            descripcion=request.POST.get('descripcion', ''),
            subida_por=request.user,
        )
        messages.success(request, 'Foto subida correctamente.')
    return redirect('clientes:detalle_paciente', paciente_id=paciente.id)


# ---------------------------------------------------------------------------
# Odontograma
# ---------------------------------------------------------------------------
# Notacion FDI: cuadrantes 1-4 (superior derecho, superior izquierdo,
# inferior izquierdo, inferior derecho), dientes 1-8 por cuadrante.
DIENTES_FDI = [
    [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28],
    [48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38],
]


@login_required
def odontograma(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    registros = paciente.odontograma.all()

    # Ultimo hallazgo por diente, para pintar el grafico
    estado_por_diente = {}
    for registro in registros:
        if registro.diente_numero not in estado_por_diente:
            estado_por_diente[registro.diente_numero] = registro

    contexto = {
        'paciente': paciente,
        'dientes_arriba': DIENTES_FDI[0],
        'dientes_abajo': DIENTES_FDI[1],
        'estado_por_diente': estado_por_diente,
        'historial': registros,
        'procedimientos': Procedimiento.objects.filter(activo=True),
        'hallazgos': OdontogramaRegistro.HALLAZGOS,
    }
    return render(request, 'clientes/odontograma.html', contexto)


@login_required
@require_POST
def registrar_odontograma(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    procedimiento_id = request.POST.get('procedimiento_relacionado') or None

    OdontogramaRegistro.objects.create(
        paciente=paciente,
        diente_numero=request.POST.get('diente_numero'),
        hallazgo=request.POST.get('hallazgo'),
        doctor=request.user,
        procedimiento_relacionado_id=procedimiento_id,
        notas=request.POST.get('notas', ''),
    )
    messages.success(request, f"Diente {request.POST.get('diente_numero')} actualizado.")
    return redirect('clientes:odontograma', paciente_id=paciente.id)


# ---------------------------------------------------------------------------
# Calendario y citas
# ---------------------------------------------------------------------------
@login_required
def calendario(request):
    doctores = Usuario.objects.filter(rol='doctor', activo_en_consultorio=True)
    return render(request, 'clientes/calendario.html', {'doctores': doctores})


@login_required
def eventos_calendario_json(request):
    """Devuelve las citas en formato JSON para pintar el calendario."""
    citas = Cita.objects.select_related('paciente', 'doctor').exclude(estado='cancelada')

    doctor_id = request.GET.get('doctor_id')
    if doctor_id:
        citas = citas.filter(doctor_id=doctor_id)
    elif request.user.es_doctor:
        citas = citas.filter(doctor=request.user)

    eventos = [{
        'id': cita.id,
        'title': f"{cita.paciente.nombre_completo} - {cita.doctor.get_full_name()}",
        'start': cita.fecha_hora.isoformat(),
        'end': (cita.fecha_hora + timedelta(minutes=cita.duracion_minutos)).isoformat(),
        'estado': cita.estado,
        'paciente_id': cita.paciente.id,
    } for cita in citas]

    return JsonResponse(eventos, safe=False)


@login_required
def crear_cita(request):
    if request.method == 'POST':
        paciente_id = request.POST.get('paciente_id')
        paciente = get_object_or_404(Paciente, id=paciente_id)

        Cita.objects.create(
            paciente=paciente,
            doctor_id=request.POST.get('doctor_id'),
            fecha_hora=request.POST.get('fecha_hora'),
            duracion_minutos=request.POST.get('duracion_minutos', 30),
            motivo=request.POST.get('motivo', ''),
            recordatorio_whatsapp_horas_antes=request.POST.get('recordatorio_horas_antes', 24),
        )
        messages.success(request, 'Cita creada correctamente.')
        return redirect('clientes:calendario')

    pacientes = Paciente.objects.filter(activo=True)
    doctores = Usuario.objects.filter(rol='doctor', activo_en_consultorio=True)
    paciente_preseleccionado = request.GET.get('paciente_id')
    cotizacion_id = request.GET.get('cotizacion_id')
    return render(request, 'clientes/cita_form.html', {
        'pacientes': pacientes,
        'doctores': doctores,
        'paciente_preseleccionado': paciente_preseleccionado,
        'cotizacion_id': cotizacion_id,
    })


@login_required
@require_POST
def mover_cita(request, cita_id):
    """Usado por el drag & drop del calendario (llamada AJAX)."""
    cita = get_object_or_404(Cita, id=cita_id)
    try:
        data = json.loads(request.body)
        cita.fecha_hora = data['nueva_fecha_hora']
        cita.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    if request.method == 'POST':
        cita.fecha_hora = request.POST.get('fecha_hora', cita.fecha_hora)
        cita.estado = request.POST.get('estado', cita.estado)
        cita.motivo = request.POST.get('motivo', cita.motivo)
        cita.notas = request.POST.get('notas', cita.notas)
        cita.save()
        messages.success(request, 'Cita actualizada.')
        return redirect('clientes:calendario')
    return render(request, 'clientes/cita_form.html', {'cita': cita})


# ---------------------------------------------------------------------------
# Cotizaciones
# ---------------------------------------------------------------------------
@login_required
def lista_cotizaciones(request):
    cotizaciones = Cotizacion.objects.select_related('paciente', 'doctor').all()
    estado = request.GET.get('estado')
    if estado:
        cotizaciones = cotizaciones.filter(estado=estado)
    return render(request, 'clientes/cotizaciones_lista.html', {
        'cotizaciones': cotizaciones,
        'estado_filtro': estado,
    })


@login_required
def crear_cotizacion(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    procedimientos = Procedimiento.objects.filter(activo=True)

    if request.method == 'POST':
        cotizacion = Cotizacion.objects.create(
            paciente=paciente,
            doctor=request.user,
            notas=request.POST.get('notas', ''),
        )

        procedimiento_ids = request.POST.getlist('procedimiento_id')
        cantidades = request.POST.getlist('cantidad')
        dientes = request.POST.getlist('diente_numero')

        for i, proc_id in enumerate(procedimiento_ids):
            if not proc_id:
                continue
            procedimiento = Procedimiento.objects.get(id=proc_id)
            CotizacionItem.objects.create(
                cotizacion=cotizacion,
                procedimiento=procedimiento,
                diente_numero=dientes[i] if i < len(dientes) else '',
                cantidad=int(cantidades[i]) if i < len(cantidades) and cantidades[i] else 1,
                precio_unitario=procedimiento.precio,
            )

        cotizacion.estado = 'enviada'
        cotizacion.save()
        messages.success(request, f'Cotizacion {cotizacion.numero} creada.')
        return redirect('clientes:detalle_cotizacion', cotizacion_id=cotizacion.id)

    return render(request, 'clientes/cotizacion_form.html', {
        'paciente': paciente,
        'procedimientos': procedimientos,
    })


@login_required
def detalle_cotizacion(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    return render(request, 'clientes/cotizacion_detalle.html', {'cotizacion': cotizacion})


@login_required
def aprobar_cotizacion(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    cotizacion.estado = 'aprobada'
    cotizacion.fecha_aprobacion = timezone.now()
    cotizacion.save()
    messages.success(request, f'Cotizacion {cotizacion.numero} aprobada. Ahora puedes crear la cita.')
    return redirect(
        f"/app/citas/nueva/?paciente_id={cotizacion.paciente.id}&cotizacion_id={cotizacion.id}"
    )


@login_required
def cotizacion_pdf(request, cotizacion_id):
    """
    Genera el PDF de la cotizacion. La generacion real usa una libreria
    de PDF (ver skill de pdf del proyecto / weasyprint) tomando el
    template cotizacion_pdf.html como base.
    """
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    return render(request, 'clientes/cotizacion_pdf.html', {'cotizacion': cotizacion})


# ---------------------------------------------------------------------------
# Pagos
# ---------------------------------------------------------------------------
@login_required
def lista_pagos_pacientes(request):
    pagos = PagoPaciente.objects.select_related('paciente', 'cuenta').all()
    total = pagos.aggregate(total=Sum('monto'))['total'] or 0
    return render(request, 'clientes/pagos_lista.html', {'pagos': pagos, 'total': total})


@login_required
def registrar_pago(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        PagoPaciente.objects.create(
            paciente=paciente,
            cotizacion_id=request.POST.get('cotizacion_id') or None,
            cuenta_id=request.POST.get('cuenta_id') or None,
            monto=request.POST.get('monto'),
            metodo=request.POST.get('metodo', ''),
            referencia=request.POST.get('referencia', ''),
            registrado_por=request.user,
        )
        messages.success(request, 'Pago registrado.')
        return redirect('clientes:detalle_paciente', paciente_id=paciente.id)

    cuentas = CuentaCobro.objects.filter(activa=True)
    cotizaciones = paciente.cotizaciones.filter(estado='aprobada')
    return render(request, 'clientes/pago_form.html', {
        'paciente': paciente, 'cuentas': cuentas, 'cotizaciones': cotizaciones,
    })


# ---------------------------------------------------------------------------
# Procedimientos (catalogo)
# ---------------------------------------------------------------------------
@login_required
def lista_procedimientos(request):
    procedimientos = Procedimiento.objects.all()
    return render(request, 'clientes/procedimientos_lista.html', {'procedimientos': procedimientos})


@login_required
def crear_procedimiento(request):
    if request.method == 'POST':
        Procedimiento.objects.create(
            nombre=request.POST.get('nombre'),
            descripcion=request.POST.get('descripcion', ''),
            precio=request.POST.get('precio'),
            duracion_minutos=request.POST.get('duracion_minutos', 30),
        )
        messages.success(request, 'Procedimiento agregado al catalogo.')
        return redirect('clientes:lista_procedimientos')
    return render(request, 'clientes/procedimiento_form.html')


@login_required
def editar_procedimiento(request, procedimiento_id):
    procedimiento = get_object_or_404(Procedimiento, id=procedimiento_id)
    if request.method == 'POST':
        procedimiento.nombre = request.POST.get('nombre', procedimiento.nombre)
        procedimiento.descripcion = request.POST.get('descripcion', procedimiento.descripcion)
        procedimiento.precio = request.POST.get('precio', procedimiento.precio)
        procedimiento.duracion_minutos = request.POST.get('duracion_minutos', procedimiento.duracion_minutos)
        procedimiento.activo = request.POST.get('activo') == 'on'
        procedimiento.save()
        messages.success(request, 'Procedimiento actualizado.')
        return redirect('clientes:lista_procedimientos')
    return render(request, 'clientes/procedimiento_form.html', {'procedimiento': procedimiento})


# ---------------------------------------------------------------------------
# Equipo (doctores del consultorio)
# ---------------------------------------------------------------------------
@login_required
def lista_equipo(request):
    equipo = Usuario.objects.filter(rol__in=['doctor', 'admin_consultorio'])
    return render(request, 'clientes/equipo_lista.html', {'equipo': equipo})


@login_required
def crear_doctor(request):
    if not request.user.es_admin_consultorio:
        messages.error(request, 'Solo el administrador del consultorio puede agregar doctores.')
        return redirect('clientes:lista_equipo')

    if request.method == 'POST':
        Usuario.objects.create_user(
            username=request.POST.get('correo'),
            email=request.POST.get('correo'),
            password=request.POST.get('password'),
            first_name=request.POST.get('nombres'),
            last_name=request.POST.get('apellidos'),
            rol='doctor',
            especialidad=request.POST.get('especialidad', ''),
            numero_colegiatura=request.POST.get('numero_colegiatura', ''),
        )
        messages.success(request, 'Doctor agregado al consultorio.')
        return redirect('clientes:lista_equipo')

    return render(request, 'clientes/doctor_form.html')
