from django.contrib import admin
from .models import Consultorio, Dominio, Plan, Suscripcion, Cupon, Pago


@admin.register(Consultorio)
class ConsultorioAdmin(admin.ModelAdmin):
    list_display = ('nombre_practica', 'schema_name', 'activo', 'fecha_registro')
    search_fields = ('nombre_practica', 'schema_name')


@admin.register(Dominio)
class DominioAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_mensual', 'limite_pacientes', 'limite_doctores', 'activo')


@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ('consultorio', 'plan', 'estado', 'fecha_vencimiento', 'auto_renovar')
    list_filter = ('estado', 'plan')


@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'tipo_descuento', 'valor', 'usos_actuales', 'usos_maximos', 'activo')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('suscripcion', 'monto', 'moneda', 'metodo', 'estado', 'fecha_pago')
    list_filter = ('estado', 'metodo')
