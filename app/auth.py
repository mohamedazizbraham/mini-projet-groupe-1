"""Inscription, connexion et jetons JWT des comptes SQLite."""
import os
import sqlite3
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()
oauth2 = OAuth2PasswordBearer(tokenUrl="auth/token")
ISSUER = "stages-api"
AUDIENCE = "stages-api"
TOKEN_MINUTES = 30


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=3, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=12, max_length=128)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value):
        return value.lower()


class User(BaseModel):
    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = TOKEN_MINUTES * 60


def configure_auth(app, connection):
    username = os.getenv("AUTH_USERNAME", "groupe1").lower()
    bootstrap_hash = os.getenv("AUTH_PASSWORD_HASH", "")
    secret = os.getenv("JWT_SECRET_KEY", "")
    if len(secret) < 32:
        raise RuntimeError("Configurer JWT_SECRET_KEY avec au moins 32 caractères aléatoires.")
    dummy_hash = bootstrap_hash or password_hasher.hash("dummy-password-not-an-account")

    def initialize_users(conn):
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )""")
        if bootstrap_hash:
            password_hasher.verify("configuration-check", bootstrap_hash)
            conn.execute("INSERT INTO users (username,password_hash) VALUES (?,?) ON CONFLICT(username) DO NOTHING", (username, bootstrap_hash))
            return conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()["id"]
        return None

    def unauthorized():
        return HTTPException(401, "Identifiants ou jeton invalides", headers={"WWW-Authenticate": "Bearer"})

    def current_user(token: str = Depends(oauth2)):
        try:
            claims = jwt.decode(token, secret, algorithms=["HS256"],
                                issuer=ISSUER, audience=AUDIENCE,
                                options={"require": ["exp", "iat", "sub", "iss", "aud"]})
            user_id = int(claims["sub"])
        except (jwt.InvalidTokenError, ValueError, TypeError):
            raise unauthorized()
        with connection() as conn:
            user = conn.execute("SELECT id,username FROM users WHERE id=?", (user_id,)).fetchone()
        if user is None:
            raise unauthorized()
        return dict(user)

    router = APIRouter(prefix="/auth", tags=["Authentification"])

    def authenticate(name, password, response):
        with connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE username=?", (name.lower(),)).fetchone()
        valid = password_hasher.verify(password, user['password_hash'] if user else dummy_hash)
        if user is None or not valid:
            raise unauthorized()
        now = datetime.now(timezone.utc)
        token = jwt.encode({"sub": str(user['id']), "iat": now,
                            "exp": now + timedelta(minutes=TOKEN_MINUTES),
                            "iss": ISSUER, "aud": AUDIENCE}, secret, algorithm="HS256")
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return Token(access_token=token)

    @router.post('/signup', response_model=User, status_code=201, summary='Sign up - créer un compte')
    def signup(credentials: Credentials):
        hashed = password_hasher.hash(credentials.password)
        try:
            with connection() as conn:
                cursor = conn.execute('INSERT INTO users (username,password_hash) VALUES (?,?)', (credentials.username, hashed))
                return {'id':cursor.lastrowid,'username':credentials.username}
        except sqlite3.IntegrityError:
            raise HTTPException(409, 'Cet identifiant est déjà utilisé')

    @router.post('/signin', response_model=Token, summary='Sign in - se connecter')
    def signin(credentials: Credentials, response: Response):
        return authenticate(credentials.username, credentials.password, response)

    @router.post('/token', response_model=Token, summary='Connexion OAuth2 pour Swagger')
    def login(response: Response, form: OAuth2PasswordRequestForm = Depends()):
        return authenticate(form.username, form.password, response)

    @router.get("/me", response_model=User)
    def me(user=Depends(current_user)):
        return user

    app.include_router(router)
    return current_user, initialize_users
