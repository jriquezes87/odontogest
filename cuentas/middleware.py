from django.db import connection


class TenantPorUsuarioMiddleware:
    """
    Reemplaza la resolucion de tenant por subdominio: mientras no haya un
    dominio propio, cada usuario "entra" al schema de su consultorio
    (Usuario.consultorio) apenas inicia sesion. El super_admin no tiene
    consultorio y se queda en el schema publico (para /admin/ y /panel/).

    Debe ir DESPUES de AuthenticationMiddleware (necesita request.user) y
    los datos aislados por schema (pacientes, citas, etc.) siguen
    funcionando exactamente igual que con el enfoque de dominio.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated and user.consultorio_id:
            connection.set_tenant(user.consultorio)
            request.tenant = user.consultorio

        response = self.get_response(request)

        connection.set_schema_to_public()
        return response
