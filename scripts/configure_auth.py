"""Génère une configuration privée sans écrire les secrets dans le dépôt."""
import getpass
import json
import secrets
from pathlib import Path
from pwdlib import PasswordHash


def main():
    path = Path('.env')
    if path.exists():
        raise SystemExit('.env existe déjà : configuration conservée. Déplacer ce fichier pour régénérer les accès.')
    username = input('Identifiant [groupe1] : ').strip() or 'groupe1'
    password = getpass.getpass('Mot de passe (16 caractères minimum, vide pour générer) : ') or secrets.token_urlsafe(24)
    if len(password) < 16:
        raise SystemExit('Choisir un mot de passe de 16 caractères minimum.')
    values = {'AUTH_USERNAME': username, 'AUTH_PASSWORD_HASH': PasswordHash.recommended().hash(password),
              'JWT_SECRET_KEY': secrets.token_urlsafe(48)}
    # Les apostrophes empêchent Compose d'interpréter les $ du hash Argon2.
    path.write_text('\n'.join(f"{k}='{v}'" for k, v in values.items())+'\n', encoding='utf-8')
    Path('acces-prives.json').write_text(json.dumps({'username': username, 'password': password},indent=2),encoding='utf-8')
    print('Configuration : .env. Identifiants privés : acces-prives.json. Ne pas publier ces fichiers.')


if __name__ == '__main__':
    main()
