from pydantic import BaseModel, EmailStr

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
 
