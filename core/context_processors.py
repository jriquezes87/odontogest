from django.conf import settings


def marca_consultorio(request):
    """
    Pone a disposicion de TODOS los templates:
    - El nombre generico de la app (MARCA_APP_NOMBRE)
    - Los colores base de la marca
    - Si hay un consultorio (tenant) activo, su nombre y logo personalizados
    """
    contexto = {
        'MARCA_APP_NOMBRE': settings.MARCA_APP_NOMBRE,
        'MARCA_COLOR_FONDO': settings.MARCA_COLOR_FONDO,
        'MARCA_COLOR_AZUL_SUAVE': settings.MARCA_COLOR_AZUL_SUAVE,
        'MARCA_COLOR_AZUL_ACENTO': settings.MARCA_COLOR_AZUL_ACENTO,
        'MARCA_COLOR_GRIS_TEXTO': settings.MARCA_COLOR_GRIS_TEXTO,
        'MARCA_COLOR_GRIS_CLARO': settings.MARCA_COLOR_GRIS_CLARO,
        'consultorio_actual': None,
    }

    tenant = getattr(request, 'tenant', None)
    # El tenant "publico" no es un consultorio real, es el esquema compartido
    if tenant is not None and getattr(tenant, 'schema_name', None) != 'public':
        contexto['consultorio_actual'] = tenant
        contexto['MARCA_COLOR_AZUL_ACENTO'] = tenant.color_acento or settings.MARCA_COLOR_AZUL_ACENTO

    return contexto
