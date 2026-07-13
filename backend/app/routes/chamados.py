from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.models import Usuario
from app.controllers.auth import get_current_user
from app.controllers.chamado import (
    buscar_chamado_ou_404,
    exigir_permissao_gerenciar_chamado,
    verificar_acesso_chamado,
    serializar_chamado,
    atualizar_chamado,
    avaliar_chamado,
    buscar_anexo_ou_404,
    caminho_absoluto_anexo,
    criar_nota_interna,
    listar_anexos_chamado,
    transferir_chamado,
    listar_historico_chamado,
    reabrir_chamado,
    salvar_anexo_chamado,
)
from app.schemas.schemas import (
    AtualizarChamadoSchema,
    AvaliacaoChamadoSchema,
    NotaInternaSchema,
    ReabrirChamadoSchema,
    TransferenciaSchema,
)

router = APIRouter(prefix="/chamados", tags=["chamados"])


@router.get("/{chamado_id}")
def obter_chamado(
    chamado_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    chamado = buscar_chamado_ou_404(chamado_id, db)
    eh_equipe = verificar_acesso_chamado(usuario, chamado)
    return serializar_chamado(chamado, db, eh_equipe)


@router.put("/{chamado_id}")
def atualizar_chamado_route(
    chamado_id: int,
    payload: AtualizarChamadoSchema,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    chamado = buscar_chamado_ou_404(chamado_id, db)
    exigir_permissao_gerenciar_chamado(usuario, chamado)
    return atualizar_chamado(usuario, chamado, payload, db)


@router.post("/{chamado_id}/notas")
def criar_nota_route(
    chamado_id: int,
    payload: NotaInternaSchema,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    chamado = buscar_chamado_ou_404(chamado_id, db)
    exigir_permissao_gerenciar_chamado(usuario, chamado)
    return criar_nota_interna(usuario, chamado, payload, db)


@router.post("/{chamado_id}/transferencia")
def transferir_chamado_route(
    chamado_id: int,
    payload: TransferenciaSchema,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    chamado = buscar_chamado_ou_404(chamado_id, db)
    exigir_permissao_gerenciar_chamado(usuario, chamado)
    return transferir_chamado(usuario, chamado, payload, db)


@router.get("/{chamado_id}/historico")
def obter_historico_route(
    chamado_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    chamado = buscar_chamado_ou_404(chamado_id, db)
    eh_equipe = verificar_acesso_chamado(usuario, chamado)
    return listar_historico_chamado(chamado, eh_equipe, db)


@router.get("/{chamado_id}/anexos")
def listar_anexos_route(
    chamado_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    chamado = buscar_chamado_ou_404(chamado_id, db)
    verificar_acesso_chamado(usuario, chamado)
    return listar_anexos_chamado(chamado, db)


@router.post("/{chamado_id}/anexos")
async def enviar_anexo_route(
    chamado_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    chamado = buscar_chamado_ou_404(chamado_id, db)
    verificar_acesso_chamado(usuario, chamado)
    return await salvar_anexo_chamado(usuario, chamado, arquivo, db)


@router.get("/{chamado_id}/anexos/{anexo_id}/download")
def baixar_anexo_route(
    chamado_id: int,
    anexo_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    chamado = buscar_chamado_ou_404(chamado_id, db)
    verificar_acesso_chamado(usuario, chamado)
    anexo = buscar_anexo_ou_404(chamado, anexo_id, db)
    return FileResponse(
        caminho_absoluto_anexo(anexo),
        media_type=anexo.tipo_mime,
        filename=anexo.nome_original,
    )


@router.post("/{chamado_id}/reabrir")
def reabrir_chamado_route(
    chamado_id: int,
    payload: ReabrirChamadoSchema,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    chamado = buscar_chamado_ou_404(chamado_id, db)
    verificar_acesso_chamado(usuario, chamado)
    return reabrir_chamado(usuario, chamado, payload, db)


@router.post("/{chamado_id}/avaliacao")
def avaliar_chamado_route(
    chamado_id: int,
    payload: AvaliacaoChamadoSchema,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    chamado = buscar_chamado_ou_404(chamado_id, db)
    verificar_acesso_chamado(usuario, chamado)
    return avaliar_chamado(usuario, chamado, payload, db)
