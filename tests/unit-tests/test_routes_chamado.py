import pytest
import httpx
import asyncio
from unittest.mock import MagicMock
from main import app
from app.config.database import get_db
from app.controllers.auth import get_current_user
from app.models.models import Usuario, Chamado, Setor

db_mock = MagicMock()
usuario_mock = Usuario(id=1, nome="Admin", perfil="Administrador", setor_id=1)

# Fixture utilizando o cliente assíncrono do httpx rodando dentro do loop de testes
@pytest.fixture
def cliente():
    app.dependency_overrides[get_db] = lambda: db_mock
    app.dependency_overrides[get_current_user] = lambda: usuario_mock

    loop = asyncio.get_event_loop_with_context() if hasattr(asyncio, "get_event_loop_with_context") else asyncio.new_event_loop()
    transport = httpx.ASGITransport(app=app)
    client = httpx.AsyncClient(transport=transport, base_url="http://testserver")
    
    # Criamos um cliente síncrono fake cujos métodos chamam o cliente assíncrono via run_until_complete
    class SyncClientWrapper:
        def get(self, url, **kwargs):
            return loop.run_until_complete(client.get(url, **kwargs))
        def put(self, url, **kwargs):
            return loop.run_until_complete(client.put(url, **kwargs))
        def post(self, url, **kwargs):
            return loop.run_until_complete(client.post(url, **kwargs))
            
    yield SyncClientWrapper()
    
    loop.run_until_complete(client.aclose())
    if not loop.is_running():
        loop.close()
    app.dependency_overrides.clear()

def test_endpoint_obter_chamado_retorna_200(cliente):
    chamado_falso = Chamado(
        id=1, titulo="Suporte", descricao="Teste", status="Aberto", prioridade="Média",
        setor_solicitante_id=1, setor_responsavel_id=1, usuario_solicitante_id=1, usuario_responsavel_id=None,
        data_criacao=None, data_atualizacao=None
    )
    setor_falso = Setor(id=1, nome="Informática", sigla="INF")
    usuario_falso = Usuario(id=1, nome="Gabriel")
    
    # Configura o mock de encadeamento do SQLAlchemy de forma genérica e resiliente
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    
    # Faz o mock retornar os respectivos objetos sequencialmente conforme as chamadas do serializar_chamado
    mock_query.first.side_effect = [chamado_falso, setor_falso, setor_falso, usuario_falso]
    db_mock.query.return_value = mock_query
    
    response = cliente.get("/api/chamados/1")
    assert response.status_code == 200
    assert response.json()["titulo"] == "Suporte"

def test_endpoint_atualizar_chamado_valido(cliente):
    chamado_falso = Chamado(id=1, status="Aberto", prioridade="Média", setor_responsavel_id=1)
    
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = chamado_falso
    db_mock.query.return_value = mock_query
    
    payload = {"status": "Em Progresso", "justificativa": "Atualização de teste"}
    response = cliente.put("/api/chamados/1", json=payload)
    assert response.status_code == 200
    assert response.json()["mensagem"] == "Chamado atualizado com sucesso"