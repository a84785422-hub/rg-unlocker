# RG Unlocker Desktop — prototype corrigé

Cette version améliore le message affiché en cas de connexion refusée. Elle n'est pas un débrideur premium.

## Lancer
```bash
python rg_unlocker.py
```

## Compiler sous Windows
```bash
python -m pip install pyinstaller
pyinstaller --clean --onefile --windowed --name RGUnlocker rg_unlocker.py
```
Résultat : `dist/RGUnlocker.exe`.

Un lien Rapidgator `/file/...` est une page web et n'est généralement pas une URL directe de fichier. Ouvrez le lien dans le navigateur et utilisez une URL directe uniquement si Rapidgator vous la fournit via un accès autorisé. Cette application ne contourne ni l'authentification, ni l'attente, ni le CAPTCHA.
