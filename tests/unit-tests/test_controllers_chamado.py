import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from app.models.models import Usuario, Chamado, Setor
from app.schemas.schemas import PedidoSchema, AtualizarChamadoSchema, TransferenciaSchema
from app.controllers.chamado import usuario_pode_gerenciar_chamado, buscar_chamado_ou_404, atualizar_chamado
from app.controllers.request import abrirChamado

def test_buscar_chamado_retorna_objeto_se_existir():
    db_mock = MagicMock()
    chamado_falso = Chamado(id=1, titulo="Erro de Rede")
    db_mock.query().filter().first.return_value = chamado_falso
    
    resultado = buscar_chamado_ou_404(1, db_mock)
    assert resultado.id == 1
    assert resultado.titulo == "Erro de Rede"

def test_buscar_chamado_lanca_404_se_nao_existir():
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        buscar_chamado_ou_404(999, db_mock)
    assert exc_info.value.status_code == 404

def test_usuario_pode_gerenciar_chamado_sem_dono_do_mesmo_setor():
    tecnico = Usuario(id=2, setor_id=1, perfil="Técnico")
    chamado = Chamado(id=10, setor_responsavel_id=1, usuario_responsavel_id=None)
    
    pode_mexer = usuario_pode_gerenciar_chamado(tecnico, chamado)
    assert pode_mexer is True

def test_usuario_nao_pode_gerenciar_chamado_de_outro_setor():
    tecnico = Usuario(id=2, setor_id=2, perfil="Técnico")
    chamado = Chamado(id=10, setor_responsavel_id=1, usuario_responsavel_id=None)
    
    pode_mexer = usuario_pode_gerenciar_chamado(tecnico, chamado)
    assert pode_mexer is False

def test_abrir_chamado_com_sucesso():
    db_mock = MagicMock()
    solicitante = Usuario(id=5, setor_id=3)
    pedido = PedidoSchema(
        titulo="Impressora quebrada",
        descricao="Não liga na tomada",
        setor_solicitante_id=3, 
        setor_responsavel_id=1,
        prioridade="Média",
        usuario_responsavel_id=None
    )
    
    resposta = abrirChamado(solicitante, pedido, db_mock)
    assert resposta["mensagem"] == "Chamado aberto com sucesso"
    assert db_mock.add.called
    assert db_mock.commit.called

def test_atualizar_chamado_exige_justificativa_para_prioridade():
    db_mock = MagicMock()
    tecnico = Usuario(id=2, setor_id=1)
    chamado = Chamado(id=1, prioridade="Baixa", status="Aberto")
    
    dados = AtualizarChamadoSchema(prioridade="Alta", justificativa="   ") # Justificativa vazia
    
    with pytest.raises(HTTPException) as exc_info:
        atualizar_chamado(tecnico, chamado, dados, db_mock)
    assert exc_info.value.status_code == 422