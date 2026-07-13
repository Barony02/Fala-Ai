import datetime
import os
import uuid
from datetime import timezone

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import EXTENSOES_PERMITIDAS, TAMANHO_MAXIMO_BYTES, UPLOAD_DIR
from app.models.models import Usuario, Setor, Chamado, HistoricoChamado, Anexo
from app.schemas.schemas import (
    AtualizarChamadoSchema,
    AvaliacaoChamadoSchema,
    NotaInternaSchema,
    ReabrirChamadoSchema,
    TransferenciaSchema,
    STATUS_VALIDOS,
    PRIORIDADES_VALIDAS,
    normalizar_status,
)

PRAZOS_SLA_HORAS = {
    "Alta": 4,
    "Média": 24,
    "Baixa": 48,
}
HORA_UTIL_INICIO = 8
HORA_UTIL_FIM = 18
PRAZO_REABERTURA_HORAS_UTEIS = 48


def _agora_compativel(referencia=None):
    agora = datetime.datetime.now(timezone.utc)
    if referencia is not None and referencia.tzinfo is None:
        return agora.replace(tzinfo=None)
    return agora


def _horas_entre(inicio, fim) -> float:
    if inicio is None or fim is None:
        return 0.0
    if inicio.tzinfo is None and fim.tzinfo is not None:
        fim = fim.replace(tzinfo=None)
    if inicio.tzinfo is not None and fim.tzinfo is None:
        inicio = inicio.replace(tzinfo=None)
    return max(0.0, (fim - inicio).total_seconds() / 3600)


def _data_compativel(valor, referencia):
    if valor is None or referencia is None:
        return valor
    if valor.tzinfo is None and referencia.tzinfo is not None:
        return valor.replace(tzinfo=referencia.tzinfo)
    if valor.tzinfo is not None and referencia.tzinfo is None:
        return valor.replace(tzinfo=None)
    return valor


def _data_no_intervalo(valor, inicio, fim) -> bool:
    if valor is None or inicio is None or fim is None:
        return False
    valor = _data_compativel(valor, inicio)
    fim = _data_compativel(fim, inicio)
    return inicio <= valor <= fim


def _dentro_horario_util(momento: datetime.datetime) -> bool:
    return momento.weekday() < 5 and HORA_UTIL_INICIO <= momento.hour < HORA_UTIL_FIM


def _proximo_horario_util(momento: datetime.datetime) -> datetime.datetime:
    if momento.weekday() >= 5:
        dias = 7 - momento.weekday()
        return (momento + datetime.timedelta(days=dias)).replace(hour=HORA_UTIL_INICIO, minute=0, second=0, microsecond=0)
    if momento.hour < HORA_UTIL_INICIO:
        return momento.replace(hour=HORA_UTIL_INICIO, minute=0, second=0, microsecond=0)
    if momento.hour >= HORA_UTIL_FIM:
        proximo = momento + datetime.timedelta(days=1)
        while proximo.weekday() >= 5:
            proximo += datetime.timedelta(days=1)
        return proximo.replace(hour=HORA_UTIL_INICIO, minute=0, second=0, microsecond=0)
    return momento


def adicionar_horas_uteis(inicio: datetime.datetime, horas: int) -> datetime.datetime:
    momento = _proximo_horario_util(inicio)
    restantes = float(horas)
    while restantes > 0:
        momento = _proximo_horario_util(momento)
        fim_dia = momento.replace(hour=HORA_UTIL_FIM, minute=0, second=0, microsecond=0)
        horas_disponiveis = max(0.0, (fim_dia - momento).total_seconds() / 3600)
        consumir = min(restantes, horas_disponiveis)
        momento += datetime.timedelta(hours=consumir)
        restantes -= consumir
        if restantes > 0:
            momento = _proximo_horario_util(fim_dia + datetime.timedelta(minutes=1))
    return momento


def calcular_sla_chamado(chamado: Chamado) -> dict:
    prazo_horas = PRAZOS_SLA_HORAS.get(chamado.prioridade or "Média", 24)
    fim = chamado.data_atualizacao if normalizar_status(chamado.status) == "Concluído" else _agora_compativel(chamado.data_criacao)
    horas_decorridas = _horas_entre(chamado.data_criacao, fim)
    percentual = round((horas_decorridas / prazo_horas) * 100, 1) if prazo_horas else 0

    if normalizar_status(chamado.status) == "Concluído":
        estado = "concluido"
    elif percentual >= 100:
        estado = "atrasado"
    elif percentual >= 80:
        estado = "critico"
    else:
        estado = "no_prazo"

    return {
        "prazo_horas": prazo_horas,
        "horas_decorridas": round(horas_decorridas, 2),
        "percentual": percentual,
        "estado": estado,
    }


def calcular_tempos_por_status(chamado: Chamado, db: Session) -> dict:
    entradas = (
        db.query(HistoricoChamado)
        .filter(HistoricoChamado.chamado_id == chamado.id, HistoricoChamado.tipo == "Status")
        .order_by(HistoricoChamado.data_criacao.asc())
        .all()
    )
    tempos = {status: 0.0 for status in STATUS_VALIDOS}
    status_atual = "Aberto"
    inicio_periodo = chamado.data_criacao

    for entrada in entradas:
        tempos[status_atual] = tempos.get(status_atual, 0.0) + _horas_entre(inicio_periodo, entrada.data_criacao)
        status_atual = normalizar_status(entrada.valor_novo) or status_atual
        inicio_periodo = entrada.data_criacao

    fim = chamado.data_atualizacao if normalizar_status(chamado.status) == "Concluído" else _agora_compativel(inicio_periodo)
    status_final = normalizar_status(chamado.status) or status_atual
    tempos[status_final] = tempos.get(status_final, 0.0) + _horas_entre(inicio_periodo, fim)
    return {status: round(horas, 2) for status, horas in tempos.items() if horas > 0}


def calcular_tempos_por_setor(chamado: Chamado, db: Session) -> list[dict]:
    transferencias = (
        db.query(HistoricoChamado)
        .filter(HistoricoChamado.chamado_id == chamado.id, HistoricoChamado.tipo == "Transferência")
        .order_by(HistoricoChamado.data_criacao.asc())
        .all()
    )
    eventos = (
        db.query(HistoricoChamado)
        .filter(HistoricoChamado.chamado_id == chamado.id, HistoricoChamado.tipo.in_(["Status", "Responsável"]))
        .order_by(HistoricoChamado.data_criacao.asc())
        .all()
    )

    setor_inicial_id = transferencias[0].setor_origem_id if transferencias and transferencias[0].setor_origem_id else chamado.setor_responsavel_id
    setor_atual_id = setor_inicial_id
    inicio_periodo = chamado.data_criacao
    segmentos = []

    for transferencia in transferencias:
        segmentos.append({
            "setor_id": setor_atual_id,
            "entrada": inicio_periodo,
            "saida": transferencia.data_criacao,
            "transferido": True,
        })
        setor_atual_id = transferencia.setor_destino_id or setor_atual_id
        inicio_periodo = transferencia.data_criacao

    fim_final = chamado.data_atualizacao if normalizar_status(chamado.status) == "Concluído" else _agora_compativel(inicio_periodo)
    segmentos.append({
        "setor_id": setor_atual_id,
        "entrada": inicio_periodo,
        "saida": fim_final,
        "transferido": False,
    })

    ids_setores = {segmento["setor_id"] for segmento in segmentos if segmento["setor_id"]}
    setores = db.query(Setor).filter(Setor.id.in_(ids_setores)).all() if ids_setores else []
    setores_map = {s.id: {"id": s.id, "nome": s.nome, "sigla": s.sigla} for s in setores}

    possui_historico_responsavel = any(e.tipo == "Responsável" for e in eventos)
    resultado = []
    for indice, segmento in enumerate(segmentos):
        entrada = segmento["entrada"]
        saida = segmento["saida"]
        primeira_resposta = None
        resolucao = None

        for evento in eventos:
            if not _data_no_intervalo(evento.data_criacao, entrada, saida):
                continue
            if primeira_resposta is None:
                iniciou_atendimento = evento.tipo == "Status" and normalizar_status(evento.valor_novo) == "Em Atendimento"
                assumiu_responsavel = evento.tipo == "Responsável" and bool(evento.valor_novo)
                if iniciou_atendimento or assumiu_responsavel:
                    primeira_resposta = evento.data_criacao
            if resolucao is None and evento.tipo == "Status" and normalizar_status(evento.valor_novo) == "Concluído":
                resolucao = evento.data_criacao

        if indice == 0 and primeira_resposta is None and chamado.usuario_responsavel_id and not possui_historico_responsavel:
            primeira_resposta = entrada
        if not segmento["transferido"] and normalizar_status(chamado.status) == "Concluído" and resolucao is None:
            resolucao = saida

        resultado.append({
            "setor": setores_map.get(segmento["setor_id"], {"id": segmento["setor_id"], "nome": "Setor não identificado", "sigla": "-"}),
            "entrada": entrada.isoformat() if entrada else None,
            "saida": saida.isoformat() if saida else None,
            "tempo_resposta_horas": round(_horas_entre(entrada, primeira_resposta), 2) if primeira_resposta else None,
            "tempo_resolucao_horas": round(_horas_entre(entrada, resolucao), 2) if resolucao else None,
            "tempo_total_horas": round(_horas_entre(entrada, saida), 2),
            "respondido": primeira_resposta is not None,
            "resolvido": resolucao is not None,
            "transferido": segmento["transferido"],
        })
    return resultado


def usuario_pode_concluir_chamado(usuario: Usuario, chamado: Chamado) -> bool:
    if usuario.perfil == "Administrador":
        return True
    if usuario.perfil == "Gestor" and usuario.setor_id == chamado.setor_responsavel_id:
        return True
    return usuario.id == chamado.usuario_responsavel_id


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
    if chamado.usuario_responsavel_id is None and usuario.setor_id == chamado.setor_responsavel_id:
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
    data_base_fechamento = chamado.data_fechamento
    if data_base_fechamento is None and normalizar_status(chamado.status) == "Concluído":
        data_base_fechamento = chamado.data_atualizacao
    prazo_reabertura = adicionar_horas_uteis(data_base_fechamento, PRAZO_REABERTURA_HORAS_UTEIS) if data_base_fechamento else None

    return {
        "id": chamado.id,
        "titulo": chamado.titulo,
        "descricao": chamado.descricao,
        "status": normalizar_status(chamado.status),
        "prioridade": chamado.prioridade,
        "setor_solicitante_id": chamado.setor_solicitante_id,
        "setor_responsavel_id": chamado.setor_responsavel_id,
        "usuario_solicitante_id": chamado.usuario_solicitante_id,
        "usuario_responsavel_id": chamado.usuario_responsavel_id,
        "data_criacao": chamado.data_criacao.isoformat() if chamado.data_criacao else None,
        "data_atualizacao": chamado.data_atualizacao.isoformat() if chamado.data_atualizacao else None,
        "data_fechamento": data_base_fechamento.isoformat() if data_base_fechamento else None,
        "prazo_reabertura": prazo_reabertura.isoformat() if prazo_reabertura else None,
        "avaliacao": {
            "nota": chamado.avaliacao_nota,
            "comentario": chamado.avaliacao_comentario,
            "data_avaliacao": chamado.data_avaliacao.isoformat() if chamado.data_avaliacao else None,
        } if chamado.avaliacao_nota else None,
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
        "sla": calcular_sla_chamado(chamado),
        "tempos_por_status": calcular_tempos_por_status(chamado, db),
        "tempos_por_setor": calcular_tempos_por_setor(chamado, db),
        "anexos": listar_anexos_chamado(chamado, db),
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
        data_criacao=datetime.datetime.now(),
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
        novo_status = normalizar_status(campos_enviados["status"])
        if novo_status not in STATUS_VALIDOS:
            raise HTTPException(status_code=422, detail=f"Status inválido. Valores aceitos: {sorted(STATUS_VALIDOS)}")
        if novo_status == "Concluído" and not usuario_pode_concluir_chamado(usuario, chamado):
            raise HTTPException(status_code=403, detail="Apenas o responsável atribuído, gestor do setor ou administrador podem concluir o chamado")
        if novo_status != normalizar_status(chamado.status):
            agora = datetime.datetime.now()
            _registrar_historico(
                db, chamado.id, usuario.id, "Status",
                comentario=dados.justificativa, valor_anterior=normalizar_status(chamado.status), valor_novo=novo_status,
            )
            chamado.status = novo_status
            chamado.data_fechamento = agora if novo_status == "Concluído" else None
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
            if novo_responsavel is None or novo_responsavel.ativo is False:
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
        chamado.data_atualizacao = datetime.datetime.now()
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


def serializar_anexo(anexo: Anexo) -> dict:
    return {
        "id": anexo.id,
        "chamado_id": anexo.chamado_id,
        "nome_original": anexo.nome_original,
        "tamanho": anexo.tamanho,
        "tipo_mime": anexo.tipo_mime,
        "data_upload": anexo.data_upload.isoformat() if anexo.data_upload else None,
        "url": f"/api/chamados/{anexo.chamado_id}/anexos/{anexo.id}/download",
    }


def listar_anexos_chamado(chamado: Chamado, db: Session) -> list[dict]:
    anexos = (
        db.query(Anexo)
        .filter(Anexo.chamado_id == chamado.id)
        .order_by(Anexo.data_upload.asc())
        .all()
    )
    return [serializar_anexo(a) for a in anexos]


async def salvar_anexo_chamado(usuario: Usuario, chamado: Chamado, arquivo: UploadFile, db: Session) -> dict:
    nome_original = os.path.basename(arquivo.filename or "")
    if not nome_original:
        raise HTTPException(status_code=422, detail="Arquivo sem nome")

    extensao = os.path.splitext(nome_original)[1].lower()
    if extensao not in EXTENSOES_PERMITIDAS:
        raise HTTPException(status_code=422, detail=f"Extensão não permitida. Use: {', '.join(sorted(EXTENSOES_PERMITIDAS))}")

    conteudo = await arquivo.read()
    if len(conteudo) > TAMANHO_MAXIMO_BYTES:
        raise HTTPException(status_code=413, detail="Arquivo excede o tamanho máximo permitido")

    pasta_chamado = os.path.join(UPLOAD_DIR, f"chamado_{chamado.id}")
    os.makedirs(pasta_chamado, exist_ok=True)
    nome_armazenado = f"{uuid.uuid4().hex}{extensao}"
    caminho_absoluto = os.path.join(pasta_chamado, nome_armazenado)
    with open(caminho_absoluto, "wb") as destino:
        destino.write(conteudo)

    caminho_relativo = os.path.relpath(caminho_absoluto, UPLOAD_DIR)
    anexo = Anexo(
        chamado_id=chamado.id,
        nome_original=nome_original,
        nome_armazenado=nome_armazenado,
        caminho=caminho_relativo,
        tamanho=len(conteudo),
        tipo_mime=arquivo.content_type or "application/octet-stream",
        data_upload=datetime.datetime.now(),
    )
    db.add(anexo)
    _registrar_historico(
        db, chamado.id, usuario.id, "Anexo",
        comentario=f"Arquivo anexado: {nome_original}",
    )
    chamado.data_atualizacao = datetime.datetime.now()
    db.commit()
    db.refresh(anexo)
    return {"mensagem": "Anexo enviado com sucesso", "anexo": serializar_anexo(anexo)}


def buscar_anexo_ou_404(chamado: Chamado, anexo_id: int, db: Session) -> Anexo:
    anexo = db.query(Anexo).filter(Anexo.id == anexo_id, Anexo.chamado_id == chamado.id).first()
    if anexo is None:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")
    return anexo


def caminho_absoluto_anexo(anexo: Anexo) -> str:
    caminho = os.path.join(UPLOAD_DIR, anexo.caminho)
    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Arquivo físico não encontrado")
    return caminho


def reabrir_chamado(usuario: Usuario, chamado: Chamado, dados: ReabrirChamadoSchema, db: Session) -> dict:
    if usuario.id != chamado.usuario_solicitante_id:
        raise HTTPException(status_code=403, detail="Apenas o solicitante pode reabrir este chamado")
    if normalizar_status(chamado.status) != "Concluído":
        raise HTTPException(status_code=422, detail="Apenas chamados concluídos podem ser reabertos")
    data_base_fechamento = chamado.data_fechamento or chamado.data_atualizacao
    if data_base_fechamento is None:
        raise HTTPException(status_code=422, detail="Chamado sem data de fechamento registrada")

    prazo_limite = adicionar_horas_uteis(data_base_fechamento, PRAZO_REABERTURA_HORAS_UTEIS)
    agora = _agora_compativel(prazo_limite)
    if agora > prazo_limite:
        raise HTTPException(status_code=403, detail="Prazo de reabertura expirado")

    _registrar_historico(
        db, chamado.id, usuario.id, "Reabertura",
        comentario=dados.justificativa,
        valor_anterior="Concluído",
        valor_novo="Aberto",
    )
    chamado.status = "Aberto"
    chamado.data_fechamento = None
    chamado.avaliacao_nota = None
    chamado.avaliacao_comentario = None
    chamado.data_avaliacao = None
    chamado.data_atualizacao = datetime.datetime.now()
    db.commit()
    return {"mensagem": "Chamado reaberto com sucesso"}


def avaliar_chamado(usuario: Usuario, chamado: Chamado, dados: AvaliacaoChamadoSchema, db: Session) -> dict:
    if usuario.id != chamado.usuario_solicitante_id:
        raise HTTPException(status_code=403, detail="Apenas o solicitante pode avaliar este chamado")
    if normalizar_status(chamado.status) != "Concluído":
        raise HTTPException(status_code=422, detail="Apenas chamados concluídos podem ser avaliados")
    if chamado.avaliacao_nota is not None:
        raise HTTPException(status_code=422, detail="Este chamado já foi avaliado")

    chamado.avaliacao_nota = dados.nota
    chamado.avaliacao_comentario = dados.comentario
    chamado.data_avaliacao = datetime.datetime.now()
    chamado.data_atualizacao = datetime.datetime.now()
    _registrar_historico(
        db, chamado.id, usuario.id, "Avaliação",
        comentario=dados.comentario,
        valor_novo=str(dados.nota),
    )
    db.commit()
    return {"mensagem": "Avaliação registrada com sucesso"}


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

    chamado.setor_responsavel_id = setor_destino.id
    chamado.usuario_responsavel_id = None
    chamado.data_atualizacao = datetime.datetime.now()  # Ajustado aqui dentro da função

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
