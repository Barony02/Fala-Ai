from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.jwt_config import verificar_token
from app.models.models import Usuario
from app.schemas.schemas import LoginSchema
import bcrypt

# Declara explicitamente o esquema Bearer
security_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme), 
    db: Session = Depends(get_db)
):
    # Recupera a string de token correta de dentro do objeto HTTPAuthorizationCredentials
    token_string = credentials.credentials
    
    print("TOKEN:", token_string)
    dados = verificar_token(token_string)

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