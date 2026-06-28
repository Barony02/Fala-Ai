from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.models import Setor, Usuario, Chamado
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
    usuario = Usuario(nome=usuarios.nome, email=usuarios.email, senha_hash=senha_hashed, setor_id=db.query(Setor).filter(Setor.sigla == usuarios.setor_sigla).first().id)
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

@router.get("/setores/{setor_id}/usuarios")
def listar_usuarios_por_setor(
    setor_id: int, 
    db: Session = Depends(get_db), 
    usuario_autenticado: Usuario = Depends(get_current_user)
):
    from app.models.models import Usuario
    
    # Busca apenas os usuários ativos que pertencem ao setor informado
    usuarios = db.query(Usuario).filter(
        Usuario.setor_id == setor_id, 
        Usuario.ativo == True
    ).all()
    
    # Retorna uma lista contendo apenas id e nome para o select do frontend
    return [{"id": u.id, "nome": u.nome} for u in usuarios]



@router.get("/meus-chamados")
def listar_meus_chamados(
    status: str = None, 
    db: Session = Depends(get_db), 
    usuario: Usuario = Depends(get_current_user)
):
    from app.models.models import Chamado, Setor, Usuario as ModelUsuario
    
    query = db.query(Chamado).filter(Chamado.usuario_solicitante_id == usuario.id)
    
    if status:
        query = query.filter(Chamado.status == status)
        
    chamados = query.all()
    
    resultado = []
    for c in chamados:
        # Busca o nome do setor responsável
        setor_res = db.query(Setor).filter(Setor.id == c.setor_responsavel_id).first()
        
        # Busca o nome do usuário responsável (se houver)
        usuario_res = None
        if c.usuario_responsavel_id:
            usuario_res = db.query(ModelUsuario).filter(ModelUsuario.id == c.usuario_responsavel_id).first()
            
        resultado.append({
            "id": c.id,
            "titulo": c.titulo,
            "descricao": c.descricao,
            "status": c.status,
            "prioridade": c.prioridade,
            "data_criacao": c.data_criacao.isoformat() if c.data_criacao else None,
            "setor_responsavel": setor_res.nome if setor_res else "Não informado",
            "usuario_responsavel": usuario_res.nome if usuario_res else "Enviar para todos (Nenhum específico)"
        })
        
    return resultado

@router.get("/usuarios")
def listar_usuarios(
    db: Session = Depends(get_db), 
    usuario_autenticado: Usuario = Depends(get_current_user)
):
    # Bloqueia se for solicitante comum
    if usuario_autenticado.perfil not in ["Gestor", "Administrador"]:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")

    query = db.query(Usuario)

    # REGRA DE ESCOPO: Se for Gestor, filtra apenas usuários do mesmo setor
    if usuario_autenticado.perfil == "Gestor":
        query = query.filter(Usuario.setor_id == usuario_autenticado.setor_id)
    
    usuarios = query.all()

    # Formata a resposta trazendo a sigla do setor para exibição amigável no front
    resultado = []
    for u in usuarios:
        setor = db.query(Setor).filter(Setor.id == u.setor_id).first()
        resultado.append({
            "id": u.id,
            "nome": u.nome,
            "email": u.email,
            "perfil": u.perfil,
            "setor_id": u.setor_id,
            "setor_sigla": setor.sigla if setor else ""
        })
    return resultado


@router.post("/usuarios")
def cadastrar_usuario_escopo(
    payload: UsuarioCadastroSchema, 
    db: Session = Depends(get_db), 
    usuario_autenticado: Usuario = Depends(get_current_user)
):
    if usuario_autenticado.perfil not in ["Gestor", "Administrador"]:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")

    # Busca o ID do setor passado por sigla
    setor_alvo = db.query(Setor).filter(Setor.sigla == payload.setor_sigla.upper()).first()
    if not setor_alvo:
        raise HTTPException(status_code=404, detail="Setor não encontrado")

    # REGRA DE ESCOPO: Gestor não pode cadastrar usuários fora de seu setor
    if usuario_autenticado.perfil == "Gestor" and setor_alvo.id != usuario_autenticado.setor_id:
        raise HTTPException(status_code=403, detail="Gestores só podem cadastrar usuários no seu próprio setor")

    # REGRA DE ESCOPO: Gestor não pode criar um Administrador
    if usuario_autenticado.perfil == "Gestor" and payload.perfil == "Administrador":
        raise HTTPException(status_code=403, detail="Um gestor não pode criar perfis de Administrador")

    # Lógica de hash de senha (exemplo usando bcrypt compatível com seu auth.py)
    import bcrypt
    senha_hashed = bcrypt.hashpw(payload.senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    novo_usuario = Usuario(
        nome=payload.nome,
        email=payload.email,
        senha_hash=senha_hashed,
        perfil=payload.perfil,
        setor_id=setor_alvo.id
    )
    
    db.add(novo_usuario)
    db.commit()
    return {"mensagem": "Usuário criado com sucesso"}


@router.put("/usuarios/{id_usuario}")
def editar_usuario_escopo(
    id_usuario: int, 
    payload: dict, # Pode mapear para um Schema específico de atualização se preferir
    db: Session = Depends(get_db), 
    usuario_autenticado: Usuario = Depends(get_current_user)
):
    if usuario_autenticado.perfil not in ["Gestor", "Administrador"]:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")

    usuario_alvo = db.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario_alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # REGRA DE ESCOPO: Gestor não pode alterar usuários de outro setor
    if usuario_autenticado.perfil == "Gestor" and usuario_alvo.setor_id != usuario_autenticado.setor_id:
        raise HTTPException(status_code=403, detail="Acesso negado às informações deste setor")

    setor_alvo = db.query(Setor).filter(Setor.sigla == payload.get("setor_sigla").upper()).first()
    if not setor_alvo:
        raise HTTPException(status_code=404, detail="Setor informado inválido")

    # REGRA DE ESCOPO: Gestor não pode mover o usuário para outro setor
    if usuario_autenticado.perfil == "Gestor" and setor_alvo.id != usuario_autenticado.setor_id:
        raise HTTPException(status_code=403, detail="Você não pode mover usuários para fora do seu setor")

    # Atualização dos campos permitidos
    usuario_alvo.nome = payload.get("nome", usuario_alvo.nome)
    usuario_alvo.email = payload.get("email", usuario_alvo.email)
    usuario_alvo.perfil = payload.get("perfil", usuario_alvo.perfil)
    usuario_alvo.setor_id = setor_alvo.id

    db.commit()
    return {"mensagem": "Usuário atualizado com sucesso"}


@router.get("/setores-dashboard")
def listar_setores_dashboard(
    db: Session = Depends(get_db), 
    usuario_autenticado: Usuario = Depends(get_current_user)
):
    if usuario_autenticado.perfil not in ["Gestor", "Administrador"]:
        raise HTTPException(status_code=403, detail="Não autorizado")

    query = db.query(Setor)
    
    # REGRA DE ESCOPO: Gestor só visualiza o próprio setor
    if usuario_autenticado.perfil == "Gestor":
        query = query.filter(Setor.id == usuario_autenticado.setor_id)
        
    setores = query.order_by(Setor.nome.asc()).all()
    
    resultado = []
    for s in setores:
        # Contagem de funcionários ativos no setor
        total_funcionarios = db.query(Usuario).filter(Usuario.setor_id == s.id, Usuario.ativo == True).count()
        
        # Agregação de chamados por status vinculados ao setor_responsavel_id
        chamados_abertos = db.query(Chamado).filter(Chamado.setor_responsavel_id == s.id, Chamado.status == "Aberto").count()
        chamados_andamento = db.query(Chamado).filter(Chamado.setor_responsavel_id == s.id, Chamado.status == "Em Progresso").count()
        chamados_fechados = db.query(Chamado).filter(Chamado.setor_responsavel_id == s.id, Chamado.status == "Fechado").count()
        
        resultado.append({
            "id": s.id,
            "nome": s.nome,
            "sigla": s.sigla,
            "total_funcionarios": total_funcionarios,
            "chamados_abertos": chamados_abertos,
            "chamados_andamento": chamados_andamento,
            "chamados_fechados": chamados_fechados
        })
        
    return resultado

@router.get("/setores/{setor_id}/chamados")
def listar_chamados_do_setor(
    setor_id: int,
    db: Session = Depends(get_db),
    usuario_autenticado: Usuario = Depends(get_current_user)
):
    if usuario_autenticado.perfil not in ["Gestor", "Administrador"]:
        raise HTTPException(status_code=403, detail="Não autorizado")
        
    # REGRA DE ESCOPO: Gestor não pode ver chamados de outros setores
    if usuario_autenticado.perfil == "Gestor" and usuario_autenticado.setor_id != setor_id:
        raise HTTPException(status_code=403, detail="Permissão negada ao escopo do setor")

    # Retorna os chamados ordenados de forma ascendente pela data_criacao (tempo de abertura)
    chamados = db.query(Chamado).filter(Chamado.setor_responsavel_id == setor_id).order_by(Chamado.data_criacao.asc()).all()
    
    return chamados

@router.put("/setores/{setor_id}")
def atualizar_setor(
    setor_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    usuario_autenticado: Usuario = Depends(get_current_user)
):
    # REGRA DE SEGURANÇA: Apenas administradores alteram setores
    if usuario_autenticado.perfil != "Administrador":
        raise HTTPException(status_code=403, detail="Apenas administradores podem gerenciar setores")
        
    setor = db.query(Setor).filter(Setor.id == setor_id).first()
    if not setor:
        raise HTTPException(status_code=404, detail="Setor não encontrado")
        
    setor.nome = payload.get("nome", setor.nome)
    setor.sigla = payload.get("sigla", setor.sigla).upper()
    db.commit()
    return {"mensagem": "Setor atualizado com sucesso"}