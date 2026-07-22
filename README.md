# OdontoGest

Sistema de gestion y administracion para odontologos independientes y
consultorios con varios doctores. Multi-tenant: cada consultorio tiene
sus datos completamente aislados en su propio schema de PostgreSQL.

## Que incluye (MVP)

- **Pacientes**: identificados por cedula, con historias, fotos (antes/durante/despues), pagos y cotizaciones.
- **Odontograma**: grafico dental interactivo por diente (notacion FDI), vinculado a procedimientos.
- **Citas y calendario**: agenda individual por doctor, vista mensual/semanal con arrastrar y soltar.
- **Cotizaciones**: numeracion correlativa, PDF para enviar por WhatsApp, flujo de aprobacion.
- **Pagos**: registro centralizado, multiples cuentas de cobro.
- **Procedimientos**: catalogo de tratamientos y precios.
- **Equipo**: gestion de doctores dentro de un consultorio.
- **Panel super-admin**: KPIs globales, suscripciones, aprobacion manual de pagos, cupones.
- **Landing publica**: pagina de precios y registro de nuevos consultorios (con 14 dias de prueba).

## Stack

- Python 3.12 + Django 5.0
- PostgreSQL con `django-tenants` (multi-tenant por schema)
- WhiteNoise para archivos estaticos
- Preparado para almacenamiento externo (Cloudflare R2 / S3) para las fotos

---

## 1. Subir el proyecto a GitHub

```bash
cd odontogest
git init
git add .
git commit -m "Version inicial de OdontoGest"
```

Luego crea un repositorio vacio en GitHub (sin README, sin .gitignore, para
no generar conflictos) y conecta:

```bash
git remote add origin https://github.com/TU_USUARIO/odontogest.git
git branch -M main
git push -u origin main
```

## 2. Desplegar en Render

### Opcion A: usando render.yaml (recomendado, un solo paso)

1. Entra a [render.com](https://render.com) y haz clic en **New > Blueprint**.
2. Conecta tu repositorio de GitHub `odontogest`.
3. Render detecta el archivo `render.yaml` automaticamente y te muestra
   que va a crear: un **Web Service** y una base de datos **PostgreSQL**.
4. Haz clic en **Apply**. Render construira todo solo.

### Opcion B: manual (si prefieres controlar cada paso)

1. **Crear la base de datos**: New > PostgreSQL. Elige un nombre
   (ej. `odontogest-db`) y el plan Starter o Standard segun necesites
   (recuerda: para 10GB necesitas el plan Standard).
2. **Crear el Web Service**: New > Web Service, conecta tu repo de GitHub.
   - Build Command: `./build.sh`
   - Start Command: `gunicorn odontogest.wsgi:application`
3. **Variables de entorno** (pestaña Environment del Web Service):
   - `SECRET_KEY`: genera una clave larga y aleatoria
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.onrender.com` (o tu dominio propio cuando lo tengas)
   - `CSRF_TRUSTED_ORIGINS`: `https://tuapp.onrender.com`
   - `DATABASE_URL`: copia el "Internal Connection String" de tu base de datos Postgres
   - `MARCA_APP_NOMBRE`: el nombre generico de tu app (puedes cambiarlo cuando quieras)

## 3. Primer despliegue: crear tu usuario super-admin

Una vez desplegado, entra a la consola de Render (Shell, dentro del
Web Service) y ejecuta:

```bash
python manage.py createsuperuser
```

Esto crea un usuario que puedes usar para entrar a `/admin` y, si le
asignas `rol = super_admin` desde ahi, tambien podra usar el panel
en `/panel/`.

## 4. Crear tus planes de suscripcion

Antes de que alguien pueda registrarse desde la landing, necesitas al
menos un `Plan` creado. Entra a `/admin/core/plan/` y agrega uno o
varios (ej: Basico, Pro).

## 5. Desarrollo local (opcional)

```bash
python -m venv venv
source venv/bin/activate          # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # y edita los valores
python manage.py migrate_schemas --shared
python manage.py createsuperuser
python manage.py runserver
```

## Notas importantes

- **Fotos de pacientes**: por defecto se guardan en el servidor. Como
  Render usa almacenamiento efimero en el plan basico, para produccion
  real se recomienda configurar Cloudflare R2 o AWS S3 (variables
  `AWS_*` en `.env`). Sin esas variables, la app funciona igual pero
  las fotos se perderian en cada redeploy.
- **Multi-tenant**: cada consultorio que se registra desde la landing
  obtiene su propio schema de PostgreSQL automaticamente. Sus datos
  (pacientes, historias, citas, etc.) nunca se mezclan con los de otro
  consultorio.
- **WhatsApp**: el envio de recordatorios automaticos no esta incluido
  en este MVP (requiere decidir entre API oficial de WhatsApp Business
  o una libreria no oficial). El campo `recordatorio_whatsapp_horas_antes`
  ya existe en el modelo `Cita`, listo para conectar cuando se defina.
- **Odontograma**: usa notacion dental FDI (11-18, 21-28, 31-38, 41-48).
