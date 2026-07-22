from django.db import models
from django.conf import settings
from django.utils import timezone


class Paciente(models.Model):
    """
    El SKU/identificador principal es la cedula de identidad.
    Vive dentro del schema de cada consultorio (aislado automaticamente
    por django-tenants).
    """
    cedula = models.CharField(max_length=20, unique=True, db_index=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    telefono_whatsapp = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)

    doctor_responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='pacientes'
    )

    alergias = models.TextField(blank=True)
    antecedentes_medicos = models.TextField(blank=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.cedula})"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


class HistoriaClinica(models.Model):
    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name='historias'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    fecha = models.DateTimeField(default=timezone.now)
    motivo_consulta = models.TextField()
    diagnostico = models.TextField(blank=True)
    tratamiento_realizado = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name_plural = 'Historias clinicas'

    def __str__(self):
        return f"Historia {self.paciente} - {self.fecha.strftime('%d/%m/%Y')}"


class FotoPaciente(models.Model):
    MOMENTOS = [
        ('antes', 'Antes'),
        ('durante', 'Durante'),
        ('despues', 'Despues'),
    ]

    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name='fotos'
    )
    imagen = models.ImageField(upload_to='pacientes/fotos/%Y/%m/')
    momento = models.CharField(max_length=10, choices=MOMENTOS)
    descripcion = models.CharField(max_length=200, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    subida_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"Foto {self.get_momento_display()} - {self.paciente}"


class Procedimiento(models.Model):
    """Catalogo de procedimientos y precios del consultorio."""
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_minutos = models.PositiveIntegerField(default=30)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


class Cotizacion(models.Model):
    ESTADOS = [
        ('borrador', 'Borrador'),
        ('enviada', 'Enviada'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    numero = models.CharField(max_length=20, unique=True, editable=False)
    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name='cotizaciones'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='borrador')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    notas = models.TextField(blank=True)
    cita_generada = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_creacion']

    def save(self, *args, **kwargs):
        if not self.numero:
            ultimo = Cotizacion.objects.order_by('-id').first()
            siguiente = (ultimo.id + 1) if ultimo else 1
            anio = timezone.now().year
            self.numero = f"COT-{anio}-{siguiente:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero} - {self.paciente}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class CotizacionItem(models.Model):
    cotizacion = models.ForeignKey(
        Cotizacion, on_delete=models.CASCADE, related_name='items'
    )
    procedimiento = models.ForeignKey(Procedimiento, on_delete=models.PROTECT)
    diente_numero = models.CharField(max_length=10, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.procedimiento.nombre} x{self.cantidad}"


class CuentaCobro(models.Model):
    """Cuentas bancarias / metodos donde el consultorio recibe pagos."""
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, blank=True)
    detalles = models.CharField(max_length=255, blank=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class PagoPaciente(models.Model):
    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name='pagos'
    )
    cotizacion = models.ForeignKey(
        Cotizacion, on_delete=models.SET_NULL, null=True, blank=True
    )
    cuenta = models.ForeignKey(
        CuentaCobro, on_delete=models.SET_NULL, null=True
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(default=timezone.now)
    metodo = models.CharField(max_length=50, blank=True)
    referencia = models.CharField(max_length=100, blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"Pago {self.monto} - {self.paciente}"


class Cita(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('no_asistio', 'No asistio'),
    ]

    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name='citas'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='citas'
    )
    fecha_hora = models.DateTimeField()
    duracion_minutos = models.PositiveIntegerField(default=30)
    motivo = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    recordatorio_whatsapp_horas_antes = models.PositiveIntegerField(
        default=24,
        help_text='Cuantas horas antes de la cita se envia el recordatorio'
    )
    recordatorio_enviado = models.BooleanField(default=False)

    creada_desde_cotizacion = models.ForeignKey(
        Cotizacion, on_delete=models.SET_NULL, null=True, blank=True
    )
    notas = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_hora']

    def __str__(self):
        return f"{self.paciente} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"


class OdontogramaRegistro(models.Model):
    HALLAZGOS = [
        ('sano', 'Sano'),
        ('caries', 'Caries'),
        ('obturado', 'Obturado / Resina'),
        ('corona', 'Corona'),
        ('endodoncia', 'Endodoncia'),
        ('extraccion', 'Extraccion indicada'),
        ('ausente', 'Ausente'),
        ('implante', 'Implante'),
        ('sellante', 'Sellante'),
        ('fractura', 'Fractura'),
    ]

    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name='odontograma'
    )
    diente_numero = models.CharField(max_length=10)  # notacion FDI: 11-18, 21-28, 31-38, 41-48
    hallazgo = models.CharField(max_length=20, choices=HALLAZGOS)
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    procedimiento_relacionado = models.ForeignKey(
        Procedimiento, on_delete=models.SET_NULL, null=True, blank=True
    )
    fecha = models.DateTimeField(default=timezone.now)
    notas = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Registro de odontograma'
        verbose_name_plural = 'Registros de odontograma'

    def __str__(self):
        return f"Diente {self.diente_numero} - {self.get_hallazgo_display()} ({self.paciente})"
