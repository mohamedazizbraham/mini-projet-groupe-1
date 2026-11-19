"""Charge le fichier généré par configure_auth.py, puis lance Uvicorn."""
import ast
import os
from pathlib import Path
import uvicorn

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    for line in (root/'.env').read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        key, value = line.split('=', 1)
        # literal_eval lit uniquement les chaînes générées, sans exécuter de code.
        os.environ.setdefault(key.strip(), ast.literal_eval(value.strip()))
    uvicorn.run('app.main:app', app_dir=str(root), host='127.0.0.1', port=8000)
