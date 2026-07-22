from django.contrib import admin
from .models import (
    Paciente, HistoriaClinica, FotoPaciente, Procedimiento,
    Cotizacion, CotizacionItem, CuentaCobro, PagoPaciente,
    Cita, OdontogramaRegistro,
)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre_completo', 'telefono', 'doctor_responsable', 'activo')
    search_fields = ('cedula', 'nombres', 'apellidos')


@admin.register(HistoriaClinica)
class HistoriaClinicaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'doctor', 'fecha')


@admin.register(FotoPaciente)
class FotoPacienteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'momento', 'fecha')


@admin.register(Procedimiento)
class ProcedimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'duracion_minutos', 'activo')


class CotizacionItemInline(admin.TabularInline):
    model = CotizacionItem
    extra = 1


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ('numero', 'paciente', 'doctor', 'estado', 'fecha_creacion')
    list_filter = ('estado',)
    inlines = [CotizacionItemInline]


@admin.register(CuentaCobro)
class CuentaCobroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'activa')


@admin.register(PagoPaciente)
class PagoPacienteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'monto', 'metodo', 'fecha')


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'doctor', 'fecha_hora', 'estado')
    list_filter = ('estado', 'doctor')


@admin.register(OdontogramaRegistro)
class OdontogramaRegistroAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'diente_numero', 'hallazgo', 'doctor', 'fecha')
    list_filter = ('hallazgo',)
