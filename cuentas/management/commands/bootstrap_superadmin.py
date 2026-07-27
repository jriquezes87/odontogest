import os

from django.core.management.base import BaseCommand

from cuentas.models import Usuario


class Command(BaseCommand):
    help = (
        "Crea (si no existe) un usuario super_admin listo para entrar a "
        "/admin/ y /panel/. Usuario, correo y clave se leen de las "
        "variables de entorno ADMIN_USERNAME, ADMIN_EMAIL y ADMIN_PASSWORD."
    )

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        password = os.environ.get('ADMIN_PASSWORD')

        if not password:
            self.stdout.write(self.style.WARNING(
                "ADMIN_PASSWORD no esta configurada, se omite la creacion del super-admin."
            ))
            return

        usuario, creado = Usuario.objects.get_or_create(
            username=username,
            defaults={'email': email},
        )
        if creado:
            usuario.set_password(password)
            self.stdout.write(self.style.SUCCESS(f"Super-admin '{username}' creado"))

        usuario.email = email
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.is_active = True
        usuario.rol = 'super_admin'
        usuario.save()
