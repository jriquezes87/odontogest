"""
URL configuration for odontogest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import re

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('landing.urls')),
    path('cuentas/', include('cuentas.urls')),
    path('app/', include('clientes.urls')),
    path('panel/', include('core.urls')),
]

# Mientras no haya almacenamiento externo (S3/R2) configurado, Django
# sirve los archivos subidos (logos, fotos) tambien en produccion. No se
# usa el helper static() de Django porque este se desactiva solo cuando
# DEBUG=False; aqui lo necesitamos activo tambien en produccion, si no
# los archivos subidos nunca se verian.
urlpatterns += [
    re_path(
        r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_URL.lstrip('/')),
        serve,
        {'document_root': settings.MEDIA_ROOT},
    ),
]
