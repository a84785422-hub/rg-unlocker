# RG Unlocker Desktop

Prototype Windows pour gérer des liens Rapidgator et télécharger une URL directe autorisée.

## Fonctionnalités
- Validation basique des liens `rapidgator.net`
- Ouverture du lien dans le navigateur
- Téléchargement d'une URL directe HTTPS Rapidgator, avec progression
- Détection basique de certaines réponses HTML d'erreur

## Limites
Cette application ne contourne pas les comptes Premium, les temps d'attente, les CAPTCHA ou les restrictions Rapidgator. Un lien de page `/file/...` n'est généralement pas une URL directe de fichier. Les téléchargements directs peuvent nécessiter une URL temporaire fournie par le service.

## Lancer depuis Windows
1. Installer Python 3 depuis https://www.python.org/downloads/windows/
2. Télécharger/cloner ce dépôt.
3. Dans le dossier du projet, lancer :
   ```bash
   python rg_unlocker.py
   ```

## Compiler en EXE localement
```bash
python -m pip install pyinstaller
pyinstaller --onefile --windowed --name RGUnlocker rg_unlocker.py
```
L'exécutable sera créé dans le dossier `dist`.

## Sécurité
N'entrez pas de mot de passe Rapidgator dans cette application. Vérifiez les URL avant de télécharger. Ne téléchargez que les fichiers auxquels vous avez le droit d'accéder.
