import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from app.controllers.auth import verificarSenha, autenticar, get_current_user, get_current_gestor
from app.models.models import Usuario
from app.schemas.schemas import LoginSchema

# 1. TESTES DA FUNÇÃO: verificarSenha
def test_verificar_senha_correta():
    senha_plana = "senha123"
    senha_hashed = "$2b$12$eA8b7Rk8JmQwErTyUiOpUuGvK1h2j3k4l5m6n7o8p9q0r1s2t3u4v"
    
    with patch("bcrypt.checkpw", return_value=True):
        assert verificarSenha(senha_plana, senha_hashed) is True

def test_verificar_senha_incorreta():
    with patch("bcrypt.checkpw", return_value=False):
        assert verificarSenha("senha_errada", "hash_qualquer") is False


# 2. TESTES DA FUNÇÃO: autenticar
def test_autenticar_sucesso():
    db_mock = MagicMock()
    
    usuario_falso = Usuario(id=1, email="teste@uol.com", senha_hash="hash_valido")
    db_mock.query.return_value.filter.return_value.first.return_value = usuario_falso
    
    dados_login = LoginSchema(email="teste@uol.com", senha="123")
    
    with patch("app.controllers.auth.verificarSenha", return_value=True):
        resultado = autenticar(db_mock, dados_login)
        assert resultado == usuario_falso

def test_autenticar_usuario_nao_encontrado():
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None
    
    dados_login = LoginSchema(email="invalido@uol.com", senha="123")
    
    resultado = autenticar(db_mock, dados_login)
    assert resultado is None

def test_autenticar_senha_incorreta():
    db_mock = MagicMock()
    usuario_falso = Usuario(id=1, email="teste@uol.com", senha_hash="hash_valido")
    db_mock.query.return_value.filter.return_value.first.return_value = usuario_falso
    
    dados_login = LoginSchema(email="teste@uol.com", senha="senha_errada")
    
    with patch("app.controllers.auth.verificarSenha", return_value=False):
        resultado = autenticar(db_mock, dados_login)
        assert resultado is None


# 3. TESTES DA FUNÇÃO: get_current_user
def test_get_current_user_sucesso():
    db_mock = MagicMock()
    credentials_mock = MagicMock()
    credentials_mock.credentials = "token_valido_string"
    
    usuario_falso = Usuario(id=1, email="user@teste.com")
    db_mock.query.return_value.filter.return_value.first.return_value = usuario_falso
    
    dados_token = {"usuario_id": 1, "perfil": "Cliente"}
    with patch("app.controllers.auth.verificar_token", return_value=dados_token):
        resultado = get_current_user(credentials=credentials_mock, db=db_mock)
        assert resultado == usuario_falso

def test_get_current_user_nao_encontrado_no_banco():
    db_mock = MagicMock()
    credentials_mock = MagicMock()
    credentials_mock.credentials = "token_valido_mas_sem_usuario"
    
    db_mock.query.return_value.filter.return_value.first.return_value = None
    dados_token = {"usuario_id": 99, "perfil": "Cliente"}
    
    with patch("app.controllers.auth.verificar_token", return_value=dados_token):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=credentials_mock, db=db_mock)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Usuário não encontrado"


# 4. TESTES DA FUNÇÃO: get_current_gestor
def test_get_current_gestor_sucesso():
    usuario_gestor = Usuario(id=1, perfil="Gestor")
    
    resultado = get_current_gestor(usuario=usuario_gestor)
    assert resultado == usuario_gestor

def test_get_current_gestor_negado():
    usuario_comum = Usuario(id=2, perfil="Cliente")
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_gestor(usuario=usuario_comum)
        
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Acesso negado" in exc_info.value.detail