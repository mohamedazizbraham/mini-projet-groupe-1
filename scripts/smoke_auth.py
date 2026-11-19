"""Exercise Sign up, Sign in and ownership with disposable fictional accounts."""
import json
import secrets
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

base = sys.argv[1].rstrip('/')

def call(method, path, expected, data=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = Request(base + path, data=json.dumps(data).encode() if data is not None else None,
                  headers=headers, method=method)
    try:
        with urlopen(req, timeout=120) as res:
            status, body = res.status, res.read()
    except HTTPError as exc:
        status, body = exc.code, exc.read()
    assert status == expected, f'{method} {path}: expected {expected}, got {status}'
    print(f'{method} {path}: {status}', flush=True)
    return json.loads(body) if body else None

call('GET', '/health', 200)
call('GET', '/stages', 401)
tokens = []
for suffix in ('a', 'b'):
    account = {'username': 'demo_' + secrets.token_hex(6) + suffix,
               'password': secrets.token_urlsafe(24)}
    user = call('POST', '/auth/signup', 201, account)
    assert 'password' not in user and 'password_hash' not in user
    call('POST', '/auth/signup', 409, account)
    token = call('POST', '/auth/signin', 200, account)['access_token']
    assert call('GET', '/auth/me', 200, token=token)['id'] == user['id']
    tokens.append(token)
stage = {'nom_etudiant': 'Etudiant Demo', 'entreprise': 'Entreprise Fictive',
         'intitule': 'Stage API', 'date_debut': '2027-02-01', 'date_fin': '2027-06-30'}
sid = call('POST', '/stages', 201, stage, tokens[0])['id']
assert len(call('GET', '/stages', 200, token=tokens[0])) == 1
assert call('GET', '/stages', 200, token=tokens[1]) == []
for method in ('GET', 'PUT', 'DELETE'):
    call(method, f'/stages/{sid}', 404, stage if method == 'PUT' else None, tokens[1])
stage['entreprise'] = 'Entreprise Demo Modifiee'
call('PUT', f'/stages/{sid}', 200, stage, tokens[0])
call('DELETE', f'/stages/{sid}', 204, token=tokens[0])
print('Sign up, Sign in, CRUD and account isolation: OK')
