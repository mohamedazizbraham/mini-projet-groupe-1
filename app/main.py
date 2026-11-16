"""API pédagogique de gestion des stages : FastAPI + SQLite."""
import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator


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
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    @asynccontextmanager
    async def lifespan(app):
        database.parent.mkdir(parents=True, exist_ok=True)
        with connection() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS stages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_etudiant TEXT NOT NULL,
                entreprise TEXT NOT NULL,
                intitule TEXT NOT NULL,
                date_debut TEXT NOT NULL,
                date_fin TEXT NOT NULL,
                CHECK (date_fin >= date_debut)
            )""")
        yield

    app = FastAPI(
        title="API de gestion des stages", version="1.0.0", lifespan=lifespan,
        description="Mini-projet Cloud Computing et Microservices. Données fictives uniquement.",
    )

    def find(conn, stage_id):
        row = conn.execute("SELECT * FROM stages WHERE id = ?", (stage_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Stage introuvable")
        return dict(row)

    @app.get("/", tags=["Service"])
    def accueil():
        return {"message": "API de gestion des stages", "documentation": "/docs"}

    @app.get("/health", tags=["Service"])
    def health():
        with connection() as conn:
            conn.execute("SELECT COUNT(*) FROM stages").fetchone()
        return {"status": "ok"}

    @app.post("/stages", response_model=Stage, status_code=201, tags=["Stages"])
    def creer_stage(stage: StageInput, response: Response):
        with connection() as conn:
            cursor = conn.execute(
                "INSERT INTO stages (nom_etudiant, entreprise, intitule, date_debut, date_fin) VALUES (?, ?, ?, ?, ?)",
                tuple(stage.model_dump(mode="json").values()),
            )
            result = find(conn, cursor.lastrowid)
        response.headers["Location"] = f"/stages/{result['id']}"
        return result

    @app.get("/stages", response_model=list[Stage], tags=["Stages"])
    def lister_stages(offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
        with connection() as conn:
            return [dict(row) for row in conn.execute(
                "SELECT * FROM stages ORDER BY id LIMIT ? OFFSET ?", (limit, offset))]

    @app.get("/stages/{stage_id}", response_model=Stage, tags=["Stages"])
    def consulter_stage(stage_id: int):
        with connection() as conn:
            return find(conn, stage_id)

    @app.put("/stages/{stage_id}", response_model=Stage, tags=["Stages"])
    def modifier_stage(stage_id: int, stage: StageInput):
        with connection() as conn:
            find(conn, stage_id)
            conn.execute(
                "UPDATE stages SET nom_etudiant=?, entreprise=?, intitule=?, date_debut=?, date_fin=? WHERE id=?",
                (*stage.model_dump(mode="json").values(), stage_id),
            )
            return find(conn, stage_id)

    @app.delete("/stages/{stage_id}", status_code=204, tags=["Stages"])
    def supprimer_stage(stage_id: int):
        with connection() as conn:
            cursor = conn.execute("DELETE FROM stages WHERE id=?", (stage_id,))
            if cursor.rowcount == 0:
                raise HTTPException(404, "Stage introuvable")
        return Response(status_code=204)

    return app


app = create_app()
