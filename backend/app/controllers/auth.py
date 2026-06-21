from app.schemas.schemas import LoginSchema
from app.models.models import Usuario
import bcrypt

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.jwt_config import verificar_token

from fastapi import Depends, Header
from app.jwt_config import verificar_token
from app.security import get_token

from typing import Optional

def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)):
    print("TOKEN:", token)
    dados = verificar_token(token)

    usuario = (
        db.query(Usuario)
        .filter(Usuario.id == dados["usuario_id"])
        .first()
    )

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado"
        )

    return usuario

def verificarSenha(senha: str, senha_hashed: str) -> bool:
    return bcrypt.checkpw(
        senha.encode("utf-8"),
        senha_hashed.encode("utf-8")
    )


def autenticar(db: Session, login: LoginSchema):
    usuario = (
        db.query(Usuario)
        .filter(Usuario.email == login.email)
        .first()
    )

    if usuario is None:
        return None

    if not verificarSenha(login.senha, usuario.senha_hash):
        return None

    return usuario