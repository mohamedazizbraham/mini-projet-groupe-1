"""Vérifie le cycle CRUD sur une API réelle, en supprimant uniquement son stage de test."""
import json
import sys
import uuid
import os
import getpass
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import Request, urlopen

base = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")
access_token = None

def request(method, path, payload=None, expected=200):
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    if access_token:
        headers['Authorization'] = 'Bearer ' + access_token
    req = Request(base + path, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=120) as response:
            status, body = response.status, response.read()
    except HTTPError as error:
        status, body = error.code, error.read()
    if status != expected:
        raise AssertionError(f"{method} {path}: attendu {expected}, obtenu {status}: {body!r}")
    print(f"OK {method} {path} -> {status}")
    return json.loads(body) if body else None

def main():
    global access_token
    request('GET', '/stages', expected=401)
    username = os.getenv('AUTH_USERNAME') or input('Identifiant : ')
    password = os.getenv('AUTH_PASSWORD') or getpass.getpass('Mot de passe : ')
    req = Request(base+'/auth/token', data=urlencode({'username':username,'password':password}).encode(),
                  headers={'Content-Type':'application/x-www-form-urlencoded'}, method='POST')
    with urlopen(req,timeout=120) as response:
        access_token = json.load(response)['access_token']
    print('OK POST /auth/token -> 200 (jeton non affiche)')
    assert request('GET','/auth/me')['username']==username
    payload = dict(nom_etudiant="Etudiant Fictif " + uuid.uuid4().hex[:8], entreprise="Entreprise Demo", intitule="Test API Cloud", date_debut="2027-02-01", date_fin="2027-07-31")
    path = None
    try:
        request("GET", "/health")
        created = request("POST", "/stages", payload, 201)
        path = f"/stages/{created['id']}"
        assert request("GET", path) == created
        listed = request("GET", f"/stages?offset=0&limit=1000")
        assert isinstance(listed, list)
        modified = dict(payload, entreprise="Entreprise Demo Modifiee")
        result = request("PUT", path, modified)
        assert result["entreprise"] == modified["entreprise"]
        assert request("GET", path)["entreprise"] == modified["entreprise"]
        request("POST", "/stages", dict(payload, date_fin="2026-01-01"), 422)
        request("DELETE", path, expected=204)
        deleted_path, path = path, None
        request("GET", deleted_path, expected=404)
        request("PUT", deleted_path, payload, 404)
        request("DELETE", deleted_path, expected=404)
        print("SUCCES : cycle CRUD, validation et erreurs 404 verifies.")
    finally:
        if path:
            request("DELETE", path, expected=204)

if __name__ == '__main__':
    main()
