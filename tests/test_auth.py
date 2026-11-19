import os
from datetime import datetime, timedelta, timezone
import jwt
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from tests.test_api import PAYLOAD

@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path/'auth.db')) as c:
        yield c

def test_login_and_me(client):
    r=client.post('/auth/token',data={'username':'test-user','password':'Test-password-123456'})
    assert r.status_code==200
    assert r.headers['cache-control']=='no-store'
    assert r.json()['expires_in']==1800
    token=r.json()['access_token']
    assert client.get('/auth/me',headers={'Authorization':'Bearer '+token}).json()=={'id':1,'username':'test-user'}
    assert client.get('/stages',headers={'Authorization':'Bearer '+token}).status_code==200

@pytest.mark.parametrize('username,password',[('test-user','wrong'),('unknown','Test-password-123456')])
def test_bad_login(client,username,password):
    r=client.post('/auth/token',data={'username':username,'password':password})
    assert r.status_code==401
    assert r.headers['www-authenticate']=='Bearer'

@pytest.mark.parametrize('method,path',[('get','/stages'),('post','/stages'),('get','/stages/1'),('put','/stages/1'),('delete','/stages/1'),('get','/auth/me')])
def test_all_routes_require_auth(client,method,path):
    kwargs={'json':PAYLOAD} if method in ('post','put') else {}
    assert getattr(client,method)(path,**kwargs).status_code==401

@pytest.mark.parametrize('kind',['expired','signature','subject','audience','missing_exp','malformed','algorithm'])
def test_invalid_token(client,kind):
    now=datetime.now(timezone.utc)
    claims={'sub':'1','iat':now,'exp':now+timedelta(minutes=1),'iss':'stages-api','aud':'stages-api'}
    key=os.environ['JWT_SECRET_KEY']
    algorithm='HS256'
    if kind=='expired':claims['exp']=now-timedelta(seconds=1)
    if kind=='signature':key='other-secret-long-enough-but-incorrect'
    if kind=='subject':claims['sub']='99999'
    if kind=='audience':claims['aud']='other-api'
    if kind=='missing_exp':del claims['exp']
    if kind=='algorithm':algorithm='HS384';key=key+'longer-for-test'
    token='malformed' if kind=='malformed' else jwt.encode(claims,key,algorithm=algorithm)
    assert client.get('/stages',headers={'Authorization':'Bearer '+token}).status_code==401

def test_missing_configuration_fails_closed(monkeypatch,tmp_path):
    monkeypatch.delenv('JWT_SECRET_KEY')
    with pytest.raises(RuntimeError):create_app(tmp_path/'fail.db')

def test_openapi_marks_protected_routes(client):
    schema=client.get('/openapi.json').json()
    assert 'OAuth2PasswordBearer' in schema['components']['securitySchemes']
    for path in ['/stages','/stages/{stage_id}']:
        for op in schema['paths'][path].values():assert op.get('security')
    assert not schema['paths']['/health']['get'].get('security')

def signup_login(client, name):
    credentials={'username':name,'password':'My-secure-password-123'}
    response=client.post('/auth/signup',json=credentials)
    assert response.status_code==201
    assert set(response.json())=={'id','username'}
    response=client.post('/auth/signin',json=credentials)
    assert response.status_code==200
    return {'Authorization':'Bearer '+response.json()['access_token']}

def test_signup_signin_isolation(client):
    alice=signup_login(client,'alice')
    bob=signup_login(client,'bob')
    created=client.post('/stages',json=PAYLOAD,headers=alice)
    assert created.status_code==201
    stage=created.json();path=f"/stages/{stage['id']}"
    assert client.get('/stages',headers=bob).json()==[]
    assert client.get('/stages',headers=alice).json()==[stage]
    assert client.get(path,headers=bob).status_code==404
    assert client.put(path,headers=bob,json=PAYLOAD).status_code==404
    assert client.delete(path,headers=bob).status_code==404
    assert client.get(path,headers=alice).json()==stage
    assert client.delete(path,headers=alice).status_code==204

def test_duplicate_and_bad_signin(client):
    signup_login(client,'alice')
    assert client.post('/auth/signup',json={'username':'ALICE','password':'Another-password-123'}).status_code==409
    assert client.post('/auth/signin',json={'username':'alice','password':'Incorrect-password-123'}).status_code==401

@pytest.mark.parametrize('payload',[{'username':'ab','password':'long-password-123'}, {'username':'new-user','password':'short'}, {'username':'new user','password':'long-password-123'}])
def test_signup_validation(client,payload):
    assert client.post('/auth/signup',json=payload).status_code==422

def test_user_storage_and_restart(tmp_path):
    import sqlite3
    db=tmp_path/'users.db'
    with TestClient(create_app(db)) as c:
        signup_login(c,'alice')
    with sqlite3.connect(db) as conn:
        hashed=conn.execute("SELECT password_hash FROM users WHERE username='alice'").fetchone()[0]
        assert hashed.startswith('$argon2') and hashed!='My-secure-password-123'
    with TestClient(create_app(db)) as c:
        assert c.post('/auth/signin',json={'username':'alice','password':'My-secure-password-123'}).status_code==200

def test_signup_without_bootstrap(monkeypatch,tmp_path):
    monkeypatch.delenv('AUTH_PASSWORD_HASH')
    with TestClient(create_app(tmp_path/'new.db')) as c:
        signup_login(c,'alice')

def test_migrate_legacy_stages(tmp_path):
    import sqlite3
    db=tmp_path/'old.db'
    with sqlite3.connect(db) as conn:
        conn.execute('CREATE TABLE stages (id INTEGER PRIMARY KEY, nom_etudiant TEXT, entreprise TEXT, intitule TEXT, date_debut TEXT, date_fin TEXT)')
        conn.execute('INSERT INTO stages VALUES (1,?,?,?,?,?)',tuple(PAYLOAD.values()))
    with TestClient(create_app(db)) as c:
        token=c.post('/auth/token',data={'username':'test-user','password':'Test-password-123456'}).json()['access_token']
        assert c.get('/stages',headers={'Authorization':'Bearer '+token}).json()[0]['id']==1
        alice=signup_login(c,'alice')
        assert c.get('/stages',headers=alice).json()==[]
