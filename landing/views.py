from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from core.models import Consultorio, Plan, Suscripcion
from cuentas.models import Usuario


def home(request):
    return render(request, 'landing/home.html')


def precios(request):
    planes = Plan.objects.filter(activo=True)
    return render(request, 'landing/precios.html', {'planes': planes})


def registro(request):
    """
    Registro publico de un nuevo consultorio.
    Crea: el Consultorio (tenant, con su propio schema aislado),
    la Suscripcion en periodo de prueba, y el primer Usuario
    (admin_consultorio), vinculado a ese consultorio.
    """
    planes = Plan.objects.filter(activo=True)

    if request.method == 'POST':
        nombre_practica = request.POST.get('nombre_practica', '').strip()
        subdominio = request.POST.get('subdominio', '').strip().lower()
        nombre_admin = request.POST.get('nombre_admin', '').strip()
        correo = request.POST.get('correo', '').strip()
        password = request.POST.get('password', '')
        plan_id = request.POST.get('plan_id')

        if not all([nombre_practica, subdominio, nombre_admin, correo, password, plan_id]):
            messages.error(request, 'Por favor completa todos los campos.')
            return render(request, 'landing/registro.html', {'planes': planes})

        if Consultorio.objects.filter(schema_name=subdominio).exists():
            messages.error(request, 'Ese identificador ya esta en uso, elige otro.')
            return render(request, 'landing/registro.html', {'planes': planes})

        if Usuario.objects.filter(username=correo).exists():
            messages.error(request, 'Ya existe una cuenta con ese correo.')
            return render(request, 'landing/registro.html', {'planes': planes})

        try:
            with transaction.atomic():
                plan = Plan.objects.get(id=plan_id)

                consultorio = Consultorio(
                    schema_name=subdominio,
                    nombre_practica=nombre_practica,
                )
                consultorio.save()

                Suscripcion.objects.create(
                    consultorio=consultorio,
                    plan=plan,
                    estado='trial',
                    fecha_vencimiento=timezone.now().date() + timedelta(days=14),
                )

                Usuario.objects.create_user(
                    username=correo,
                    email=correo,
                    password=password,
                    first_name=nombre_admin,
                    rol='admin_consultorio',
                    consultorio=consultorio,
                )

            messages.success(
                request,
                f'¡Listo! Tu consultorio "{nombre_practica}" fue creado con 14 dias de prueba gratis. '
                f'Ya puedes iniciar sesion.'
            )
            return redirect('cuentas:login')

        except Exception as e:
            messages.error(request, f'Ocurrio un error al crear tu cuenta: {e}')

    return render(request, 'landing/registro.html', {'planes': planes})
