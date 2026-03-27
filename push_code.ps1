$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

git config --global user.name "Cosmo Admin"
git config --global user.email "admin@cosmo.tn"

Write-Host "Initialisation de Git..."
git init
git branch -m main

Write-Host "Ajout des fichiers..."
git add .

Write-Host "Sauvegarde locale..."
git commit -m "Version Initiale de déploiement (Supabase + Railway ready)"

Write-Host "Connexion au compte GitHub..."
git remote add origin https://github.com/balssam-cyber/cosmetique.git

Write-Host "Transfert de code en cours... (Une fenêtre de connexion Git va apparaitre, connectez-vous)"
git push -u origin main

Write-Host "Transfert terminé avec succès!"
