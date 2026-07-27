import os

from django.core.management.base import BaseCommand
from django_tenants.utils import get_public_schema_name

from core.models import Consultorio, Dominio


class Command(BaseCommand):
    help = (
        "Crea (si no existe) el tenant publico y su dominio. Sin esto, "
        "django-tenants no encuentra ningun tenant para el host de Render "
        "y todas las peticiones devuelven 404."
    )

    def handle(self, *args, **options):
        schema_publico = get_public_schema_name()

        tenant, tenant_creado = Consultorio.objects.get_or_create(
            schema_name=schema_publico,
            defaults={'nombre_practica': 'OdontoGest (publico)'},
        )
        if tenant_creado:
            self.stdout.write(self.style.SUCCESS(f"Tenant publico creado (schema={schema_publico})"))

        render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
        hostnames = {'localhost', '127.0.0.1'}
        if render_hostname:
            hostnames.add(render_hostname)
        primary_hostname = render_hostname or 'localhost'

        for hostname in hostnames:
            _, dominio_creado = Dominio.objects.get_or_create(
                domain=hostname,
                defaults={'tenant': tenant, 'is_primary': hostname == primary_hostname},
            )
            if dominio_creado:
                self.stdout.write(self.style.SUCCESS(f"Dominio '{hostname}' asociado al tenant publico"))
