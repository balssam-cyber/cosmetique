@echo off
echo ==============================
echo   CosmoERP - Setup Windows
echo ==============================

python -m venv venv
call venv\Scripts\activate.bat

pip install -r requirements.txt

python manage.py makemigrations rnd production stock purchase sales regulatory dashboard
python manage.py migrate

echo from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@cosmo.tn', 'admin123') | python manage.py shell

python manage.py create_sample_data

echo.
echo ==============================
echo   Setup termine!
echo   Lancer: python manage.py runserver
echo   URL: http://127.0.0.1:8000
echo   Admin: admin / admin123
echo ==============================
pause
