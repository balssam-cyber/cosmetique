#!/bin/bash
# CosmoERP - Script de configuration automatique
# Usage: bash setup.sh

echo "=============================="
echo "  CosmoERP - Setup"
echo "=============================="

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Migrations
python manage.py makemigrations rnd production stock purchase sales regulatory dashboard
python manage.py migrate

# Create superuser (admin/admin123)
echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@cosmo.tn', 'admin123')" | python manage.py shell

# Sample data
python manage.py create_sample_data

echo ""
echo "=============================="
echo "  Setup terminé!"
echo "  Lancer: python manage.py runserver"
echo "  URL: http://127.0.0.1:8000"
echo "  Admin: admin / admin123"
echo "=============================="
