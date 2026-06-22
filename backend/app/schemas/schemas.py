from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
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
