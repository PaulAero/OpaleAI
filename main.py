import subprocess

try:
    subprocess.run(['python3', 'autre_script.py'])
except:
    "Erreur lors du lancement du subprocess de mise à jour automatique de la base de données."

try:
