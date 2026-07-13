from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.jwt_config import verificar_token
from app.models.models import Usuario
from app.schemas.schemas import LoginSchema
import bcrypt
import datetime

security_scheme = HTTPBearer()
MAX_TENTATIVAS_LOGIN = 5
BLOQUEIO_MINUTOS = 15

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
    if usuario.ativo is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
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

def get_current_administrador(usuario: Usuario = Depends(get_current_user)):
    if usuario.perfil != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas Administrador pode realizar esta ação"
        )
    return usuario

def verificarSenha(senha: str, senha_hashed: str) -> bool:
    return bcrypt.checkpw(
        senha.encode("utf-8"),
        senha_hashed.encode("utf-8")
    )

def autenticar(db: Session, login: LoginSchema):
    agora = datetime.datetime.now()
    usuario = (
        db.query(Usuario)
        .filter(Usuario.email == login.email)
        .first()
    )

    if usuario is None:
        return None

    if usuario.ativo is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    if usuario.bloqueado_ate and usuario.bloqueado_ate > agora:
        minutos = max(1, int((usuario.bloqueado_ate - agora).total_seconds() // 60) + 1)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso temporariamente bloqueado. Tente novamente em {minutos} minuto(s)."
        )

    if not verificarSenha(login.senha, usuario.senha_hash):
        usuario.tentativas_login = (usuario.tentativas_login or 0) + 1
        if usuario.tentativas_login >= MAX_TENTATIVAS_LOGIN:
            usuario.bloqueado_ate = agora + datetime.timedelta(minutes=BLOQUEIO_MINUTOS)
        db.commit()
        return None

    usuario.tentativas_login = 0
    usuario.bloqueado_ate = None
    db.commit()
    return usuario
