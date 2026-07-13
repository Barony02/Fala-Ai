from pydantic import BaseModel, field_validator
from typing import Optional

STATUS_VALIDOS = {"Aberto", "Em Atendimento", "Pausado", "Concluído"}
STATUS_ALIASES = {
    "Aberto": "Aberto",
    "Em Progresso": "Em Atendimento",
    "Em Andamento": "Em Atendimento",
    "Em Atendimento": "Em Atendimento",
    "Pausado": "Pausado",
    "Fechado": "Concluído",
    "Concluido": "Concluído",
    "Concluído": "Concluído",
    "Resolvido": "Concluído",
}
PRIORIDADES_VALIDAS = {"Baixa", "Média", "Alta"}


def normalizar_status(status: Optional[str]) -> Optional[str]:
    if status is None:
        return None
    return STATUS_ALIASES.get(status.strip(), status.strip())
class LoginSchema(BaseModel):
    email: str
    senha: str

    @field_validator('email')
    @classmethod
    def email_login_valido(cls, v):
        email = (v or "").strip().lower()
        if "@" not in email:
            raise ValueError("Informe um e-mail válido")
        return email

class SetorSchema(BaseModel):
    nome: str
    sigla: str

class UsuarioCadastroSchema(BaseModel):
    nome: str
    email: str
    senha: str
    setor_sigla: str
    perfil: Optional[str] = "Solicitante" # Define como opcional, assumindo "Solicitante" por padrão

    @field_validator('email')
    @classmethod
    def email_cadastro_valido(cls, v):
        email = (v or "").strip().lower()
        if "@" not in email:
            raise ValueError("Informe um e-mail válido")
        return email
    
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

class AvaliacaoChamadoSchema(BaseModel):
    nota: int
    comentario: Optional[str] = None

    @field_validator('nota')
    @classmethod
    def nota_valida(cls, v):
        if v < 1 or v > 5:
            raise ValueError("A nota deve estar entre 1 e 5")
        return v

    @field_validator('comentario')
    @classmethod
    def comentario_limpo(cls, v):
        if v is None:
            return None
        texto = v.strip()
        return texto or None


class ReabrirChamadoSchema(BaseModel):
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
