# RG Unlocker Desktop v0.3

Gestionnaire local pour organiser des liens Rapidgator et télécharger une URL directe autorisée.

## Changements v0.3
- File d'attente manuelle de liens.
- Diagnostic de quota visible.
- Messages plus clairs si le serveur renvoie une page HTML ou un message de limite.
- Pas de relances automatiques et pas de contournement du quota.

## Lancer
Python 3 installé, puis :
```bash
python rg_unlocker.py
```

## Compiler sous Windows
```bash
python -m pip install pyinstaller
pyinstaller --clean --onefile --windowed --name RGUnlocker rg_unlocker.py
```
L'exécutable sera dans `dist/RGUnlocker.exe`.

Cette application ne réinitialise pas les quotas et ne contourne pas l'authentification, les CAPTCHA, les délais ou les restrictions Rapidgator. Le quota quotidien doit être réinitialisé par Rapidgator.
