from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.jwt_config import verificar_token
from app.models.models import Usuario
from app.schemas.schemas import LoginSchema
import bcrypt

security_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme), 
    db: Session = Depends(get_db)
):
    token_string = credentials.credentials
    dados = verificar_token(token_string)

    usuario = (
        db.query(Usuario)
        .filter(Usuario.id == dados["usuario_id"])
        .first()
    )

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )

    return usuario

# Nova dependência para proteger rotas restritas a Gestores
def get_current_gestor(usuario: Usuario = Depends(get_current_user)):
    if usuario.perfil != "Gestor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas Gestor pode realizar esta ação"
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