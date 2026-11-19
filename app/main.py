"""API pédagogique de gestion des stages : FastAPI + SQLite."""
import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.auth import configure_auth


class StageInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    nom_etudiant: str = Field(min_length=1, max_length=120, examples=["Camille Exemple"])
    entreprise: str = Field(min_length=1, max_length=160, examples=["Entreprise Demo"])
    intitule: str = Field(min_length=1, max_length=200, examples=["Développement API Cloud"])
    date_debut: date
    date_fin: date

    @model_validator(mode="after")
    def dates_coherentes(self):
        if self.date_fin < self.date_debut:
            raise ValueError("La date de fin doit être égale ou postérieure à la date de début.")
        return self


class Stage(StageInput):
    id: int


def create_app(db_path=None):
    database = Path(db_path or os.getenv("DATABASE_PATH", "data/stages.db"))

    @contextmanager
    def connection():
        conn = sqlite3.connect(database, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys=ON')
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    @asynccontextmanager
    async def lifespan(app):
        database.parent.mkdir(parents=True, exist_ok=True)
        with connection() as conn:
            bootstrap_id = initialize_users(conn)
            conn.execute("""CREATE TABLE IF NOT EXISTS stages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL REFERENCES users(id),
                nom_etudiant TEXT NOT NULL,
                entreprise TEXT NOT NULL,
                intitule TEXT NOT NULL,
                date_debut TEXT NOT NULL,
                date_fin TEXT NOT NULL,
                CHECK (date_fin >= date_debut)
            )""")
            columns = {row['name'] for row in conn.execute('PRAGMA table_info(stages)')}
            if 'owner_id' not in columns:
                conn.execute('ALTER TABLE stages ADD COLUMN owner_id INTEGER REFERENCES users(id)')
            if bootstrap_id is not None:
                conn.execute('UPDATE stages SET owner_id=? WHERE owner_id IS NULL', (bootstrap_id,))
            conn.execute('CREATE INDEX IF NOT EXISTS idx_stages_owner ON stages(owner_id)')
        yield

    app = FastAPI(
        title="API de gestion des stages", version="2.0.0", lifespan=lifespan,
        description="Mini-projet Cloud Computing et Microservices. Données fictives uniquement.",
    )
    current_user, initialize_users = configure_auth(app, connection)
    stages = APIRouter(dependencies=[Depends(current_user)], tags=["Stages"])

    def find(conn, stage_id, owner_id):
        row = conn.execute("SELECT * FROM stages WHERE id = ? AND owner_id = ?", (stage_id, owner_id)).fetchone()
        if row is None:
            raise HTTPException(404, "Stage introuvable")
        return {key: row[key] for key in row.keys() if key != 'owner_id'}

    @app.get("/", tags=["Service"])
    def accueil():
        return {"message": "API de gestion des stages", "documentation": "/docs"}

    @app.get("/health", tags=["Service"])
    def health():
        with connection() as conn:
            conn.execute("SELECT COUNT(*) FROM stages").fetchone()
        return {"status": "ok"}

    @stages.post("/stages", response_model=Stage, status_code=201)
    def creer_stage(stage: StageInput, response: Response, user=Depends(current_user)):
        with connection() as conn:
            cursor = conn.execute(
                "INSERT INTO stages (nom_etudiant, entreprise, intitule, date_debut, date_fin, owner_id) VALUES (?, ?, ?, ?, ?, ?)",
                (*stage.model_dump(mode="json").values(), user['id']),
            )
            result = find(conn, cursor.lastrowid, user['id'])
        response.headers["Location"] = f"/stages/{result['id']}"
        return result

    @stages.get("/stages", response_model=list[Stage])
    def lister_stages(offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), user=Depends(current_user)):
        with connection() as conn:
            return [{key: row[key] for key in row.keys() if key != 'owner_id'} for row in conn.execute(
                "SELECT * FROM stages WHERE owner_id=? ORDER BY id LIMIT ? OFFSET ?", (user['id'], limit, offset))]

    @stages.get("/stages/{stage_id}", response_model=Stage)
    def consulter_stage(stage_id: int, user=Depends(current_user)):
        with connection() as conn:
            return find(conn, stage_id, user['id'])

    @stages.put("/stages/{stage_id}", response_model=Stage)
    def modifier_stage(stage_id: int, stage: StageInput, user=Depends(current_user)):
        with connection() as conn:
            find(conn, stage_id, user['id'])
            conn.execute(
                "UPDATE stages SET nom_etudiant=?, entreprise=?, intitule=?, date_debut=?, date_fin=? WHERE id=? AND owner_id=?",
                (*stage.model_dump(mode="json").values(), stage_id, user['id']),
            )
            return find(conn, stage_id, user['id'])

    @stages.delete("/stages/{stage_id}", status_code=204)
    def supprimer_stage(stage_id: int, user=Depends(current_user)):
        with connection() as conn:
            cursor = conn.execute("DELETE FROM stages WHERE id=? AND owner_id=?", (stage_id, user['id']))
            if cursor.rowcount == 0:
                raise HTTPException(404, "Stage introuvable")
        return Response(status_code=204)

    app.include_router(stages)
    return app


app = create_app()
