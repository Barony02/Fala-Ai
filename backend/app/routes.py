from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Setor

router = APIRouter()

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

class SetorSchema(BaseModel):
    nome: str
    sigla: str

@router.post("/auth/login")
def login(dados: LoginSchema, db: Session = Depends(get_db)):
    usuario, mensagem = autenticar_usuario(db, dados.email, dados.senha)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=mensagem)
    
    return {
        "status": "success",
        "usuario": {
            "nome": usuario.nome,
            "email": usuario.email,
            "perfil": usuario.perfil
        }
    }

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