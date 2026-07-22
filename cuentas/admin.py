from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'activo_en_consultorio')
    list_filter = ('rol', 'activo_en_consultorio')
    fieldsets = UserAdmin.fieldsets + (
        ('Datos OdontoGest', {
            'fields': ('rol', 'telefono', 'foto', 'especialidad', 'numero_colegiatura', 'activo_en_consultorio')
        }),
    )
