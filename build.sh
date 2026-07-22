#!/usr/bin/env bash
# Este script se ejecuta automaticamente en cada despliegue de Render.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# migrate_schemas es el comando de django-tenants: migra tanto
# el schema publico (core, cuentas, landing) como cada schema
# de consultorio existente (clientes).
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
