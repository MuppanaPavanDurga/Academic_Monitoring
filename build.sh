#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

cd academic_monitoring

# apply database migrations
python manage.py migrate

# create superuser automatically (only if not exists)
echo "from django.contrib.auth import get_user_model; \
User=get_user_model(); \
User.objects.filter(username='admin').exists() or \
User.objects.create_superuser('admin','admin@gmail.com','admin12345')" \
| python manage.py shell

# collect static files
python manage.py collectstatic --no-input
