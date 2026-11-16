import pytest
from fastapi.testclient import TestClient
from app.main import create_app

PAYLOAD = dict(nom_etudiant="Camille Exemple", entreprise="Entreprise Demo", intitule="API Cloud", date_debut="2027-02-01", date_fin="2027-07-31")

@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "test.db")) as client:
        yield client

def test_crud(client):
    assert client.get("/stages").json() == []
    response = client.post("/stages", json=PAYLOAD)
    assert response.status_code == 201
    stage = response.json()
    path = f"/stages/{stage['id']}"
    assert response.headers["location"] == path
    assert client.get(path).json() == stage
    assert client.get("/stages").json() == [stage]
    updated = dict(PAYLOAD, entreprise="Autre Entreprise Demo")
    assert client.put(path, json=updated).json()["entreprise"] == updated["entreprise"]
    assert client.get(path).json()["entreprise"] == updated["entreprise"]
    deleted = client.delete(path)
    assert deleted.status_code == 204 and deleted.content == b""
    assert client.get(path).status_code == 404

@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_missing(client, method):
    kwargs = {"json": PAYLOAD} if method == "put" else {}
    assert getattr(client, method)("/stages/99999", **kwargs).status_code == 404

@pytest.mark.parametrize("change", [
    {"date_fin": "2026-01-01"}, {"date_debut": "invalide"},
    {"nom_etudiant": "   "}, {"entreprise": ""}, {"intitule": "x"*201}, {"id": 1},
])
def test_invalid(client, change):
    assert client.post("/stages", json=dict(PAYLOAD, **change)).status_code == 422
    assert client.get("/stages").json() == []

def test_put_requires_complete_body(client):
    stage = client.post("/stages", json=PAYLOAD).json()
    path = f"/stages/{stage['id']}"
    assert client.put(path, json={"entreprise": "Test"}).status_code == 422
    assert client.get(path).json() == stage

def test_persistence(tmp_path):
    db = tmp_path / "persistent.db"
    with TestClient(create_app(db)) as first:
        created = first.post("/stages", json=PAYLOAD).json()
    with TestClient(create_app(db)) as second:
        assert second.get(f"/stages/{created['id']}").json() == created

def test_sql_and_pagination(client):
    text = "Demo'); DROP TABLE stages;--"
    first = client.post("/stages", json=dict(PAYLOAD, entreprise=text)).json()
    second = client.post("/stages", json=PAYLOAD).json()
    assert client.get(f"/stages/{first['id']}").json()["entreprise"] == text
    assert client.get("/stages?offset=1&limit=1").json() == [second]
    assert client.get("/stages?limit=0").status_code == 422

def test_service(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/docs").status_code == 200
    assert "/stages" in client.get("/openapi.json").json()["paths"]
