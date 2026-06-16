from typing import Optional
from fastapi import HTTPException, status, Header
from app.jwt_config import verificar_token

def get_token(authorization: Optional[str] = Header(None)) -> str:
    """Extrai o token do header Authorization"""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token não fornecido")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Esquema inválido")
        return token
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Formato de token inválido")
