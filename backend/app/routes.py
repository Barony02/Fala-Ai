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