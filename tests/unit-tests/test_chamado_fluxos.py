import asyncio
import datetime
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.controllers.chamado import (
    adicionar_horas_uteis,
    avaliar_chamado,
    reabrir_chamado,
    salvar_anexo_chamado,
)
from app.models.models import Chamado, Usuario
from app.schemas.schemas import AvaliacaoChamadoSchema, ReabrirChamadoSchema


def test_adicionar_horas_uteis_pula_final_de_semana():
    sexta_17h = datetime.datetime(2026, 7, 17, 17, 0, 0)
    resultado = adicionar_horas_uteis(sexta_17h, 2)
    assert resultado == datetime.datetime(2026, 7, 20, 9, 0, 0)


def test_reabrir_chamado_concluido_dentro_do_prazo():
    usuario = Usuario(id=1, perfil="Solicitante")
    chamado = Chamado(
        id=10,
        status="Concluído",
        usuario_solicitante_id=1,
        data_atualizacao=datetime.datetime.now(),
        data_fechamento=datetime.datetime.now(),
    )
    db = MagicMock()

    resposta = reabrir_chamado(
        usuario,
        chamado,
        ReabrirChamadoSchema(justificativa="Problema persistiu"),
        db,
    )

    assert resposta["mensagem"] == "Chamado reaberto com sucesso"
    assert chamado.status == "Aberto"
    assert chamado.data_fechamento is None
    db.commit.assert_called_once()


def test_reabrir_chamado_fora_do_prazo_bloqueia():
    usuario = Usuario(id=1, perfil="Solicitante")
    chamado = Chamado(
        id=10,
        status="Concluído",
        usuario_solicitante_id=1,
        data_atualizacao=datetime.datetime.now() - datetime.timedelta(days=30),
        data_fechamento=datetime.datetime.now() - datetime.timedelta(days=30),
    )

    with pytest.raises(HTTPException) as exc:
        reabrir_chamado(
            usuario,
            chamado,
            ReabrirChamadoSchema(justificativa="Problema persistiu"),
            MagicMock(),
        )

    assert exc.value.status_code == 403


def test_avaliar_chamado_concluido_registra_nota():
    usuario = Usuario(id=1, perfil="Solicitante")
    chamado = Chamado(id=10, status="Concluído", usuario_solicitante_id=1)
    db = MagicMock()

    resposta = avaliar_chamado(
        usuario,
        chamado,
        AvaliacaoChamadoSchema(nota=5, comentario="Excelente"),
        db,
    )

    assert resposta["mensagem"] == "Avaliação registrada com sucesso"
    assert chamado.avaliacao_nota == 5
    assert chamado.avaliacao_comentario == "Excelente"
    db.commit.assert_called_once()


def test_upload_anexo_rejeita_extensao_nao_permitida():
    usuario = Usuario(id=1, perfil="Solicitante")
    chamado = Chamado(id=10, status="Aberto", usuario_solicitante_id=1)
    arquivo = MagicMock()
    arquivo.filename = "script.exe"

    with pytest.raises(HTTPException) as exc:
        asyncio.run(salvar_anexo_chamado(usuario, chamado, arquivo, MagicMock()))

    assert exc.value.status_code == 422
