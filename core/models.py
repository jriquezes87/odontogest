from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.utils import timezone


class Consultorio(TenantMixin):
    """
    Cada Consultorio es un tenant. Django-tenants crea un schema
    de PostgreSQL separado para cada uno, aislando 100% los datos
    clinicos entre consultorios.
    """
    nombre_practica = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    color_acento = models.CharField(max_length=7, default='#5B9BD5')

    ruc_o_rif = models.CharField(max_length=30, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.CharField(max_length=255, blank=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    # django-tenants requiere esto para auto-crear el schema
    auto_create_schema = True

    def __str__(self):
        return self.nombre_practica


class Dominio(DomainMixin):
    """
    Cada Consultorio puede tener su propio subdominio,
    ej: clinicasonrisa.odontogest.com
    """
    pass


class Plan(models.Model):
    nombre = models.CharField(max_length=50)
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    limite_pacientes = models.PositiveIntegerField(default=100)
    limite_doctores = models.PositiveIntegerField(default=1)
    limite_storage_gb = models.PositiveIntegerField(default=1)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.nombre} (${self.precio_mensual}/mes)"


class Suscripcion(models.Model):
    ESTADOS = [
        ('trial', 'Periodo de prueba'),
        ('activa', 'Activa'),
        ('pausada', 'Pausada'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
    ]

    consultorio = models.OneToOneField(
        Consultorio, on_delete=models.CASCADE, related_name='suscripcion'
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='trial')
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField()
    auto_renovar = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.consultorio.nombre_practica} - {self.plan.nombre} ({self.estado})"


class Cupon(models.Model):
    TIPOS = [
        ('porcentaje', 'Porcentaje de descuento'),
        ('monto_fijo', 'Monto fijo de descuento'),
        ('dias_gratis', 'Dias gratis'),
    ]

    codigo = models.CharField(max_length=30, unique=True)
    tipo_descuento = models.CharField(max_length=20, choices=TIPOS)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_expiracion = models.DateField(null=True, blank=True)
    usos_maximos = models.PositiveIntegerField(default=1)
    usos_actuales = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.codigo

    @property
    def disponible(self):
        if not self.activo:
            return False
        if self.fecha_expiracion and self.fecha_expiracion < timezone.now().date():
            return False
        if self.usos_actuales >= self.usos_maximos:
            return False
        return True


class Pago(models.Model):
    METODOS = [
        ('pago_movil', 'Pago movil'),
        ('zelle', 'Zelle'),
        ('usdt', 'USDT / Cripto'),
        ('transferencia', 'Transferencia bancaria'),
        ('efectivo', 'Efectivo'),
    ]
    ESTADOS = [
        ('pendiente', 'Pendiente de revision'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    suscripcion = models.ForeignKey(
        Suscripcion, on_delete=models.CASCADE, related_name='pagos'
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=5, default='USD')
    metodo = models.CharField(max_length=20, choices=METODOS)
    referencia = models.CharField(max_length=100, blank=True)
    comprobante = models.ImageField(upload_to='comprobantes/', blank=True, null=True)
    cupon_aplicado = models.ForeignKey(
        Cupon, on_delete=models.SET_NULL, null=True, blank=True
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_pago = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    notas_admin = models.TextField(blank=True)

    def __str__(self):
        return f"{self.suscripcion.consultorio.nombre_practica} - {self.monto} {self.moneda} ({self.estado})"
