from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.models import Setor

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


@router.post("/setores")
def cadastrar_setor(setor: SetorSchema, db: Session = Depends(get_db)):
    novo_setor = Setor(nome=setor.nome, sigla=setor.sigla)
    db.add(novo_setor)
    db.commit()
    db.refresh(novo_setor)
    return {"mensagem": "Setor cadastrado com sucesso", "id": novo_setor.id}

@router.get("/setores")
def listar_setores(db: Session = Depends(get_db)):
    return db.query(Setor).all()

@router.post("/login")
def login(login: LoginSchema, db: Session = Depends(get_db)):
    from app.controllers.auth import autenticar
    usuario = autenticar(db, login)

    if usuario is None:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    return {"mensagem": "Login realizado"}

@router.post("/cadastrarUsuarios")
def cadastrar_usuario(usuarios: UsuarioCadastroSchema, db: Session = Depends(get_db)):
    from app.models import Usuario
    from bcrypt import hashpw, gensalt
    senha_hashed = hashpw(usuarios.senha.encode('utf-8'), gensalt()).decode('utf-8')
    usuario = Usuario(nome=usuarios.nome, email=usuarios.email, senha_hash=senha_hashed)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return {"mensagem": "Usuário cadastrado com sucesso", "id": usuario.id}
