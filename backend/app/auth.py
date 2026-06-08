from app.routes import LoginSchema
from app.models import Usuario
import bcrypt

def verificarSenha(senha: str, senha_hashed: str) -> bool:
    return bcrypt.checkpw(senha.encode('utf-8'), senha_hashed.encode('utf-8'))

def autenticar(db, login: LoginSchema):
    usuario = (
        db.query(Usuario)
        .filter(Usuario.email == login.email)
        .first()
    )
    if not usuario:
        return None
    if verificarSenha(login.senha, usuario.senha_hash):
        return usuario
    return None