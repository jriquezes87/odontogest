from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django_tenants.utils import schema_context

from core.models import Consultorio, Plan, Suscripcion
from cuentas.models import Usuario

DEMO_SCHEMA = 'demo'
DEMO_ADMIN_EMAIL = 'demo@odontogest.com'
DEMO_ADMIN_PASSWORD = 'Demo1234!'
DEMO_DOCTOR_EMAIL = 'doctora.rivas@odontogest.com'
DEMO_DOCTOR_PASSWORD = 'Demo1234!'


class Command(BaseCommand):
    help = (
        "Crea (si no existe) un consultorio de demostracion con pacientes, "
        "citas, cotizaciones, pagos y odontogramas de ejemplo, para poder "
        "explorar la app con datos reales sin tener que cargarlos a mano."
    )

    def handle(self, *args, **options):
        plan, _ = Plan.objects.get_or_create(
            nombre='Demo',
            defaults={
                'precio_mensual': 15,
                'limite_pacientes': 500,
                'limite_doctores': 5,
                'limite_storage_gb': 5,
                'activo': False,
                'orden': 99,
            },
        )

        consultorio, tenant_creado = Consultorio.objects.get_or_create(
            schema_name=DEMO_SCHEMA,
            defaults={'nombre_practica': 'Clinica Demo', 'color_acento': '#16181D'},
        )

        Suscripcion.objects.get_or_create(
            consultorio=consultorio,
            defaults={
                'plan': plan,
                'estado': 'activa',
                'fecha_vencimiento': timezone.now().date() + timedelta(days=365),
            },
        )

        admin_demo, admin_creado = Usuario.objects.get_or_create(
            username=DEMO_ADMIN_EMAIL,
            defaults={
                'email': DEMO_ADMIN_EMAIL,
                'first_name': 'Andrea',
                'last_name': 'Suarez',
                'rol': 'admin_consultorio',
                'consultorio': consultorio,
            },
        )
        if admin_creado:
            admin_demo.set_password(DEMO_ADMIN_PASSWORD)
            admin_demo.save()

        doctora, doctora_creada = Usuario.objects.get_or_create(
            username=DEMO_DOCTOR_EMAIL,
            defaults={
                'email': DEMO_DOCTOR_EMAIL,
                'first_name': 'Maria',
                'last_name': 'Rivas',
                'rol': 'doctor',
                'consultorio': consultorio,
                'especialidad': 'Ortodoncia',
                'numero_colegiatura': 'OD-4821',
            },
        )
        if doctora_creada:
            doctora.set_password(DEMO_DOCTOR_PASSWORD)
            doctora.save()

        with schema_context(DEMO_SCHEMA):
            self._sembrar_datos_clinicos(admin_demo, doctora)

        self.stdout.write(self.style.SUCCESS(
            f"Demo lista. Entra con {DEMO_ADMIN_EMAIL} / {DEMO_ADMIN_PASSWORD}"
        ))

    def _sembrar_datos_clinicos(self, admin_demo, doctora):
        from clientes.models import (
            Paciente, HistoriaClinica, Procedimiento, Cotizacion, CotizacionItem,
            CuentaCobro, PagoPaciente, Cita, OdontogramaRegistro,
        )

        if Paciente.objects.exists():
            return  # ya sembrado antes, no duplicar

        procedimientos_datos = [
            ('Limpieza dental', 'Profilaxis y remocion de placa', 35, 30),
            ('Resina compuesta', 'Obturacion por caries, una superficie', 60, 45),
            ('Endodoncia', 'Tratamiento de conducto', 220, 90),
            ('Corona de porcelana', 'Corona ceramica sobre diente tratado', 350, 60),
            ('Extraccion simple', 'Extraccion de pieza dental', 45, 30),
            ('Blanqueamiento dental', 'Blanqueamiento en consultorio', 150, 60),
        ]
        procedimientos = [
            Procedimiento.objects.create(nombre=n, descripcion=d, precio=p, duracion_minutos=m)
            for n, d, p, m in procedimientos_datos
        ]

        cuenta = CuentaCobro.objects.create(
            nombre='Banco Principal USD', tipo='transferencia', detalles='Cuenta corriente 0102-****-1234'
        )

        pacientes_datos = [
            ('V-14882301', 'Carol', 'May', '0414-1112233', 'carol.may@example.com'),
            ('V-19233410', 'Beatriz', 'Delgado', '0424-2223344', 'beatriz.delgado@example.com'),
            ('V-12094455', 'Angelica', 'Angarita', '0412-3334455', ''),
            ('V-20871122', 'Josue', 'Escobar', '0414-4445566', 'josue.escobar@example.com'),
            ('V-15662398', 'Yrimar', 'Meza', '0424-5556677', ''),
            ('V-18332290', 'Eumary', 'Suarez', '0412-6667788', 'eumary.suarez@example.com'),
            ('V-21099887', 'Mauricio', 'Rosillo', '0414-7778899', ''),
            ('V-16554423', 'Paola', 'Riascos', '0424-8889900', 'paola.riascos@example.com'),
        ]
        hoy = timezone.now().date()
        pacientes = []
        for i, (cedula, nombres, apellidos, telefono, correo) in enumerate(pacientes_datos):
            pacientes.append(Paciente.objects.create(
                cedula=cedula, nombres=nombres, apellidos=apellidos,
                fecha_nacimiento=hoy.replace(year=hoy.year - 20 - i * 3),
                telefono=telefono, telefono_whatsapp=telefono, correo=correo,
                direccion='Caracas, Venezuela',
                doctor_responsable=doctora,
                alergias='Ninguna conocida' if i % 3 else 'Penicilina',
                antecedentes_medicos='' if i % 2 else 'Hipertension controlada',
            ))

        for paciente in pacientes[:5]:
            HistoriaClinica.objects.create(
                paciente=paciente, doctor=doctora,
                motivo_consulta='Control de rutina y evaluacion general',
                diagnostico='Buena salud bucal general, gingivitis leve',
                tratamiento_realizado='Limpieza dental y aplicacion de fluor',
                observaciones='Recomendado control cada 6 meses',
            )

        ahora = timezone.now()
        citas_datos = [
            (pacientes[0], ahora - timedelta(days=10), 'completada'),
            (pacientes[1], ahora - timedelta(days=5), 'completada'),
            (pacientes[2], ahora - timedelta(days=2), 'no_asistio'),
            (pacientes[3], ahora.replace(hour=9, minute=0), 'confirmada'),
            (pacientes[4], ahora.replace(hour=14, minute=30), 'pendiente'),
            (pacientes[5], ahora + timedelta(days=2), 'confirmada'),
            (pacientes[6], ahora + timedelta(days=4), 'pendiente'),
        ]
        for paciente, fecha_hora, estado in citas_datos:
            Cita.objects.create(
                paciente=paciente, doctor=doctora, fecha_hora=fecha_hora,
                duracion_minutos=30, motivo='Control y limpieza', estado=estado,
            )

        cotizaciones_estados = ['aprobada', 'aprobada', 'enviada', 'enviada', 'rechazada']
        for paciente, estado in zip(pacientes, cotizaciones_estados):
            cotizacion = Cotizacion.objects.create(
                paciente=paciente, doctor=doctora, estado=estado,
                notas='Presupuesto de tratamiento',
            )
            for procedimiento in procedimientos[:2]:
                CotizacionItem.objects.create(
                    cotizacion=cotizacion, procedimiento=procedimiento,
                    diente_numero='16', cantidad=1, precio_unitario=procedimiento.precio,
                )
            if estado == 'aprobada':
                cotizacion.fecha_aprobacion = timezone.now()
                cotizacion.save()
                PagoPaciente.objects.create(
                    paciente=paciente, cotizacion=cotizacion, cuenta=cuenta,
                    monto=cotizacion.total, metodo='transferencia',
                    referencia=f'REF-{paciente.cedula[-4:]}', registrado_por=admin_demo,
                )

        for paciente in pacientes[:3]:
            OdontogramaRegistro.objects.create(
                paciente=paciente, diente_numero='16', hallazgo='caries',
                doctor=doctora, notas='Caries oclusal detectada',
            )
            OdontogramaRegistro.objects.create(
                paciente=paciente, diente_numero='21', hallazgo='obturado',
                doctor=doctora, notas='Resina en buen estado',
            )
