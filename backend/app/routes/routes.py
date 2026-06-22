from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.models import Setor, Usuario
from app.controllers.auth import get_current_user, get_current_gestor
from app.controllers.request import abrirChamado
from app.schemas.schemas import LoginSchema, SetorSchema, PedidoSchema, UsuarioCadastroSchema

router = APIRouter()

@router.get("/teste-auth")
def teste_auth(authorization: str = Header(None)):
    return {"authorization": authorization}

@router.post("/setores")
def cadastrar_setor(
    setor: SetorSchema, 
    db: Session = Depends(get_db), 
    #gestor: Usuario = Depends(get_current_gestor) # Usa a nova dependência nativa
):
    novo_setor = Setor(nome=setor.nome, sigla=setor.sigla)
    db.add(novo_setor)
    db.commit()
    db.refresh(novo_setor)
    return {"mensagem": "Setor cadastrado com sucesso", "id": novo_setor.id}

@router.get("/setores")
def listar_setores(
    db: Session = Depends(get_db), 
    usuario: Usuario = Depends(get_current_user) # Qualquer usuário autenticado pode listar
):
    return db.query(Setor).all()

@router.post("/login")
def login(login: LoginSchema, db: Session = Depends(get_db)):
    from app.controllers.auth import autenticar
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
def cadastrar_usuario(usuarios: UsuarioCadastroSchema, db: Session = Depends(get_db)):
    from app.models.models import Usuario
    from bcrypt import hashpw, gensalt
    senha_hashed = hashpw(usuarios.senha.encode('utf-8'), gensalt()).decode('utf-8')
    usuario = Usuario(nome=usuarios.nome, email=usuarios.email, senha_hash=senha_hashed)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return {"mensagem": "Usuário cadastrado com sucesso", "id": usuario.id}

@router.post("/realizarChamado")
def criar_chamado(
    pedido: PedidoSchema, 
    usuario: Usuario = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    return abrirChamado(usuario, pedido, db)