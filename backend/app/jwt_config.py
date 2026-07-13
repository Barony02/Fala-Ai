from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import HTTPException, status

# Chave secreta para assinar o token (altere em produção!)
SECRET_KEY = "sua-chave-super-secreta-mude-em-producao"
ALGORITHM = "HS256"
EXPIRE_MINUTES = 30

def criar_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verificar_token(token: str) -> dict:
    """Verifica e decodifica um token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: int = payload.get("sub")
        perfil: str = payload.get("perfil")
        if usuario_id is None or perfil is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        return {"usuario_id": usuario_id, "perfil": perfil}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")