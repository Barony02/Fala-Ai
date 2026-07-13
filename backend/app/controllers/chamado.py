import datetime
from datetime import timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import Usuario, Setor, Chamado, HistoricoChamado
from app.schemas.schemas import (
    AtualizarChamadoSchema,
    NotaInternaSchema,
    TransferenciaSchema,
    STATUS_VALIDOS,
    PRIORIDADES_VALIDAS,
)


def buscar_chamado_ou_404(chamado_id: int, db: Session) -> Chamado:
    chamado = db.query(Chamado).filter(Chamado.id == chamado_id).first()
    if chamado is None:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    return chamado


def usuario_pode_gerenciar_chamado(usuario: Usuario, chamado: Chamado) -> bool:
    if usuario.perfil == "Administrador":
        return True
    if usuario.perfil == "Gestor" and usuario.setor_id == chamado.setor_responsavel_id:
        return True
    if usuario.id == chamado.usuario_responsavel_id:
        return True
    return False


def exigir_permissao_gerenciar_chamado(usuario: Usuario, chamado: Chamado) -> None:
    if not usuario_pode_gerenciar_chamado(usuario, chamado):
        raise HTTPException(status_code=403, detail="Acesso negado a este chamado")


def verificar_acesso_chamado(usuario: Usuario, chamado: Chamado) -> bool:
    """Retorna True se o usuário pertence à equipe que pode gerenciar o chamado,
    False se ele for apenas o solicitante dono. Lança 403 se não for nenhum dos dois."""
    if usuario_pode_gerenciar_chamado(usuario, chamado):
        return True
    if usuario.id == chamado.usuario_solicitante_id:
        return False
    raise HTTPException(status_code=403, detail="Acesso negado a este chamado")


def serializar_chamado(chamado: Chamado, db: Session, eh_equipe: bool) -> dict:
    setor_solicitante = db.query(Setor).filter(Setor.id == chamado.setor_solicitante_id).first()
    setor_responsavel = db.query(Setor).filter(Setor.id == chamado.setor_responsavel_id).first()
    usuario_solicitante = db.query(Usuario).filter(Usuario.id == chamado.usuario_solicitante_id).first()
    usuario_responsavel = None
    if chamado.usuario_responsavel_id:
        usuario_responsavel = db.query(Usuario).filter(Usuario.id == chamado.usuario_responsavel_id).first()

    return {
        "id": chamado.id,
        "titulo": chamado.titulo,
        "descricao": chamado.descricao,
        "status": chamado.status,
        "prioridade": chamado.prioridade,
        "data_criacao": chamado.data_criacao.isoformat() if chamado.data_criacao else None,
        "data_atualizacao": chamado.data_atualizacao.isoformat() if chamado.data_atualizacao else None,
        "setor_solicitante": {
            "id": setor_solicitante.id, "nome": setor_solicitante.nome, "sigla": setor_solicitante.sigla
        } if setor_solicitante else None,
        "setor_responsavel": {
            "id": setor_responsavel.id, "nome": setor_responsavel.nome, "sigla": setor_responsavel.sigla
        } if setor_responsavel else None,
        "usuario_solicitante": {
            "id": usuario_solicitante.id, "nome": usuario_solicitante.nome
        } if usuario_solicitante else None,
        "usuario_responsavel": {
            "id": usuario_responsavel.id, "nome": usuario_responsavel.nome
        } if usuario_responsavel else None,
        "pode_gerenciar": eh_equipe,
    }


def _registrar_historico(
    db: Session, chamado_id: int, usuario_autor_id: int, tipo: str,
    comentario=None, valor_anterior=None, valor_novo=None,
    setor_origem_id=None, setor_destino_id=None, visivel_solicitante=True,
) -> HistoricoChamado:
    entrada = HistoricoChamado(
        chamado_id=chamado_id,
        usuario_autor_id=usuario_autor_id,
        tipo=tipo,
        comentario=comentario,
        valor_anterior=valor_anterior,
        valor_novo=valor_novo,
        setor_origem_id=setor_origem_id,
        setor_destino_id=setor_destino_id,
        visivel_solicitante=visivel_solicitante,
        data_criacao=datetime.datetime.now(timezone.utc),
    )
    db.add(entrada)
    return entrada


def atualizar_chamado(usuario: Usuario, chamado: Chamado, dados: AtualizarChamadoSchema, db: Session) -> dict:
    campos_enviados = dados.model_dump(exclude_unset=True)
    campos_enviados.pop("justificativa", None)  # metadado do histórico, não é coluna do Chamado

    if not campos_enviados:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar foi enviado")

    if "prioridade" in campos_enviados and not (dados.justificativa and dados.justificativa.strip()):
        raise HTTPException(status_code=422, detail="É obrigatório informar uma justificativa para alterar a prioridade")

    algo_mudou = False

    if "status" in campos_enviados:
        novo_status = campos_enviados["status"]
        if novo_status not in STATUS_VALIDOS:
            raise HTTPException(status_code=422, detail=f"Status inválido. Valores aceitos: {sorted(STATUS_VALIDOS)}")
        if novo_status != chamado.status:
            _registrar_historico(
                db, chamado.id, usuario.id, "Status",
                comentario=dados.justificativa, valor_anterior=chamado.status, valor_novo=novo_status,
            )
            chamado.status = novo_status
            algo_mudou = True

    if "prioridade" in campos_enviados:
        nova_prioridade = campos_enviados["prioridade"]
        if nova_prioridade not in PRIORIDADES_VALIDAS:
            raise HTTPException(status_code=422, detail=f"Prioridade inválida. Valores aceitos: {sorted(PRIORIDADES_VALIDAS)}")
        if nova_prioridade != chamado.prioridade:
            _registrar_historico(
                db, chamado.id, usuario.id, "Prioridade",
                comentario=dados.justificativa, valor_anterior=chamado.prioridade, valor_novo=nova_prioridade,
            )
            chamado.prioridade = nova_prioridade
            algo_mudou = True

    if "usuario_responsavel_id" in campos_enviados:
        novo_responsavel_id = campos_enviados["usuario_responsavel_id"]
        if novo_responsavel_id is not None:
            novo_responsavel = db.query(Usuario).filter(Usuario.id == novo_responsavel_id).first()
            if novo_responsavel is None or not novo_responsavel.ativo:
                raise HTTPException(status_code=422, detail="Usuário responsável inválido ou inativo")
            if novo_responsavel.setor_id != chamado.setor_responsavel_id:
                raise HTTPException(status_code=422, detail="O responsável precisa pertencer ao setor responsável do chamado")
        if novo_responsavel_id != chamado.usuario_responsavel_id:
            _registrar_historico(
                db, chamado.id, usuario.id, "Responsável",
                comentario=dados.justificativa,
                valor_anterior=str(chamado.usuario_responsavel_id) if chamado.usuario_responsavel_id else None,
                valor_novo=str(novo_responsavel_id) if novo_responsavel_id else None,
            )
            chamado.usuario_responsavel_id = novo_responsavel_id
            algo_mudou = True

    if algo_mudou:
        chamado.data_atualizacao = datetime.datetime.now(timezone.utc)

    db.commit()
    return {"mensagem": "Chamado atualizado com sucesso"}


def criar_nota_interna(usuario: Usuario, chamado: Chamado, dados: NotaInternaSchema, db: Session) -> dict:
    entrada = _registrar_historico(
        db, chamado.id, usuario.id, "Nota",
        comentario=dados.comentario, visivel_solicitante=False,
    )
    db.commit()
    db.refresh(entrada)
    return {"mensagem": "Nota adicionada com sucesso", "id": entrada.id}


def transferir_chamado(usuario: Usuario, chamado: Chamado, dados: TransferenciaSchema, db: Session) -> dict:
    setor_destino = db.query(Setor).filter(Setor.id == dados.setor_destino_id).first()
    if setor_destino is None:
        raise HTTPException(status_code=404, detail="Setor de destino não encontrado")
    if setor_destino.id == chamado.setor_responsavel_id:
        raise HTTPException(status_code=400, detail="O chamado já está neste setor")

    setor_origem_id = chamado.setor_responsavel_id

    _registrar_historico(
        db, chamado.id, usuario.id, "Transferência",
        comentario=dados.justificativa,
        setor_origem_id=setor_origem_id, setor_destino_id=setor_destino.id,
    )

    # A pessoa atribuída pertencia ao setor antigo; não faz sentido continuar responsável no setor novo.
    chamado.setor_responsavel_id = setor_destino.id
    chamado.usuario_responsavel_id = None
    chamado.data_atualizacao = datetime.datetime.now(timezone.utc)

    db.commit()
    return {"mensagem": "Chamado transferido com sucesso"}


def listar_historico_chamado(chamado: Chamado, eh_equipe: bool, db: Session) -> list:
    query = db.query(HistoricoChamado).filter(HistoricoChamado.chamado_id == chamado.id)
    if not eh_equipe:
        query = query.filter(HistoricoChamado.visivel_solicitante == True)
    entradas = query.order_by(HistoricoChamado.data_criacao.asc()).all()

    if not entradas:
        return []

    ids_usuarios = {e.usuario_autor_id for e in entradas}
    for e in entradas:
        if e.tipo == "Responsável":
            if e.valor_anterior:
                ids_usuarios.add(int(e.valor_anterior))
            if e.valor_novo:
                ids_usuarios.add(int(e.valor_novo))

    usuarios_map = {}
    if ids_usuarios:
        usuarios = db.query(Usuario).filter(Usuario.id.in_(ids_usuarios)).all()
        usuarios_map = {u.id: u.nome for u in usuarios}

    ids_setores = set()
    for e in entradas:
        if e.setor_origem_id:
            ids_setores.add(e.setor_origem_id)
        if e.setor_destino_id:
            ids_setores.add(e.setor_destino_id)

    setores_map = {}
    if ids_setores:
        setores = db.query(Setor).filter(Setor.id.in_(ids_setores)).all()
        setores_map = {s.id: {"id": s.id, "nome": s.nome} for s in setores}

    resultado = []
    for e in entradas:
        if e.tipo == "Responsável":
            valor_anterior = usuarios_map.get(int(e.valor_anterior)) if e.valor_anterior else "Nenhum"
            valor_novo = usuarios_map.get(int(e.valor_novo)) if e.valor_novo else "Nenhum"
        else:
            valor_anterior = e.valor_anterior
            valor_novo = e.valor_novo

        resultado.append({
            "id": e.id,
            "tipo": e.tipo,
            "comentario": e.comentario,
            "valor_anterior": valor_anterior,
            "valor_novo": valor_novo,
            "setor_origem": setores_map.get(e.setor_origem_id),
            "setor_destino": setores_map.get(e.setor_destino_id),
            "autor": {"id": e.usuario_autor_id, "nome": usuarios_map.get(e.usuario_autor_id, "Desconhecido")},
            "data_criacao": e.data_criacao.isoformat() if e.data_criacao else None,
        })
    return resultado
