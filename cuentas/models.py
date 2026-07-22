from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuario personalizado con 3 roles posibles:
    - super_admin: el dueno del negocio (tu). Vive en el schema publico.
    - admin_consultorio: dueno/administrador de un consultorio, ve todos
      los doctores y pacientes de SU consultorio.
    - doctor: odontologo individual, ve sus propios pacientes y agenda
      (a menos que el admin del consultorio le de acceso mas amplio).
    """
    ROLES = [
        ('super_admin', 'Super Administrador'),
        ('admin_consultorio', 'Administrador de Consultorio'),
        ('doctor', 'Doctor / Odontologo'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES, default='doctor')
    telefono = models.CharField(max_length=30, blank=True)
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)

    # Especialidad, colegiatura, etc. - datos propios del doctor
    especialidad = models.CharField(max_length=100, blank=True)
    numero_colegiatura = models.CharField(max_length=50, blank=True)

    activo_en_consultorio = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"

    @property
    def es_super_admin(self):
        return self.rol == 'super_admin'

    @property
    def es_admin_consultorio(self):
        return self.rol == 'admin_consultorio'

    @property
    def es_doctor(self):
        return self.rol == 'doctor'
