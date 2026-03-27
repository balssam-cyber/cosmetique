Write-Host "=============================="
Write-Host "  CosmoERP - Full Setup"
Write-Host "=============================="

Write-Host "[1/6] Installing Python 3.11..."
winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements --silent

Write-Host "[2/6] Refreshing Environment Variables..."
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "[3/6] Creating Virtual Environment..."
if (!(Test-Path "venv")) {
    python -m venv venv
}

Write-Host "[4/6] Installing Dependencies..."
& .\venv\Scripts\python.exe -m pip install --upgrade pip
& .\venv\Scripts\pip.exe install -r requirements.txt

Write-Host "[5/6] Running Database Migrations..."
& .\venv\Scripts\python.exe manage.py makemigrations rnd production stock purchase sales regulatory dashboard
& .\venv\Scripts\python.exe manage.py migrate

Write-Host "[6/6] Initializing Admin & Sample Data..."
"from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@cosmo.tn', 'admin123')" | & .\venv\Scripts\python.exe manage.py shell
& .\venv\Scripts\python.exe manage.py create_sample_data

Write-Host "=============================="
Write-Host "  Setup completed successfully!"
Write-Host "  You can now run: .\venv\Scripts\python.exe manage.py runserver"
Write-Host "=============================="
