from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Setor
from app.security import get_token, verificar_token

router = APIRouter()

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

class SetorSchema(BaseModel):
    nome: str
    sigla: str

class UsuarioCadastroSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    
class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    usuario_id: int
    perfil: str

def verificar_perfil_gestor(token: str = Depends(get_token)):
    """Verifica se o usuário tem perfil Gestor"""
    payload = verificar_token(token)
    if payload['perfil'] != "Gestor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Apenas Gestor pode realizar esta ação")
    return payload

def verificar_autenticacao(token: str = Depends(get_token)):
    """Verifica se o usuário está autenticado"""
    return verificar_token(token)

@router.post("/setores")
def cadastrar_setor(setor: SetorSchema, db: Session = Depends(get_db), auth: dict = Depends(verificar_perfil_gestor)):
    novo_setor = Setor(nome=setor.nome, sigla=setor.sigla)
    db.add(novo_setor)
    db.commit()
    db.refresh(novo_setor)
    return {"mensagem": "Setor cadastrado com sucesso", "id": novo_setor.id}

@router.get("/setores")
def listar_setores(db: Session = Depends(get_db), auth: dict = Depends(verificar_autenticacao)):
    return db.query(Setor).all()

@router.post("/login")
def login(login: LoginSchema, db: Session = Depends(get_db)):
    from app.auth import autenticar
    from app.jwt_config import criar_access_token
    from datetime import timedelta
    
    usuario = autenticar(db, login)

    if usuario is None:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # Cria o token com usuario_id e perfil
    access_token = criar_access_token(
        data={"sub": usuario.id, "perfil": usuario.perfil},
        expires_delta=timedelta(minutes=30)
    )
    
    return {
        "mensagem": "Login realizado com sucesso",
        "access_token": access_token,
        "token_type": "bearer",
        "usuario_id": usuario.id,
        "perfil": usuario.perfil
    }

@router.post("/cadastrarUsuarios")
def cadastrar_usuario(usuarios: UsuarioCadastroSchema, db: Session = Depends(get_db), auth: dict = Depends(verificar_perfil_gestor)):
    from app.models import Usuario
    from bcrypt import hashpw, gensalt
    senha_hashed = hashpw(usuarios.senha.encode('utf-8'), gensalt()).decode('utf-8')
    usuario = Usuario(nome=usuarios.nome, email=usuarios.email, senha_hash=senha_hashed)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return {"mensagem": "Usuário cadastrado com sucesso", "id": usuario.id}
