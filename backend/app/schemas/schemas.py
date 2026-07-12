from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

STATUS_VALIDOS = {"Aberto", "Em Progresso", "Fechado"}
PRIORIDADES_VALIDAS = {"Baixa", "Média", "Alta"}
class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

class SetorSchema(BaseModel):
    nome: str
    sigla: str

class UsuarioCadastroSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    setor_sigla: str
    perfil: Optional[str] = "Solicitante" # Define como opcional, assumindo "Solicitante" por padrão
    
class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    usuario_id: int
    perfil: str

class PedidoSchema(BaseModel):
    titulo: str
    descricao: str
    setor_solicitante_id: int
    setor_responsavel_id: int
    prioridade: str
    usuario_responsavel_id: Optional[int] = None

    # Intercepta o valor antes da validação final do Pydantic
    @field_validator('usuario_responsavel_id', mode='before')
    @classmethod
    def tratar_usuario_nulo(cls, v):
        # Se vier 0, string vazia "" ou se for avaliado como falso (com exceção de None puro)
        if v == 0 or v == "" or v is None:
            return None
        return int(v)


class AtualizarChamadoSchema(BaseModel):
    status: Optional[str] = None
    prioridade: Optional[str] = None
    usuario_responsavel_id: Optional[int] = None
    justificativa: Optional[str] = None


class NotaInternaSchema(BaseModel):
    comentario: str

    @field_validator('comentario')
    @classmethod
    def comentario_nao_vazio(cls, v):
        if not v or not v.strip():
            raise ValueError("O comentário não pode ser vazio")
        return v.strip()


class TransferenciaSchema(BaseModel):
    setor_destino_id: int
    justificativa: str

    @field_validator('justificativa')
    @classmethod
    def justificativa_nao_vazia(cls, v):
        if not v or not v.strip():
            raise ValueError("A justificativa é obrigatória")
        return v.strip()

class AtualizarPerfilSchema(BaseModel):
    nome: str

class AlterarSenhaSchema(BaseModel):
    senha_atual: str
    nova_senha: str