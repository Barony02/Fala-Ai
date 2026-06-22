import jwt
from datetime import datetime, timedelta, timezone

# Use a mesma chave e algoritmo configurados no seu jwt_config.py
SECRET_KEY = "sua-chave-super-secreta-mude-em-producao"
ALGORITHM = "HS256"

def gerar_token_manual(usuario_id: int, perfil: str, minutos_validos: int = 30):
    to_encode = {
        "sub": usuario_id,
        "perfil": perfil,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=minutos_validos)
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

if __name__ == "__main__":
    # Altere os valores abaixo conforme necessário para os seus testes
    ID_DO_USUARIO = 3
    PERFIL_DO_USUARIO = "Solicitante"  # Pode ser 'Gestor', 'Comum', etc.
    
    token = gerar_token_manual(usuario_id=ID_DO_USUARIO, perfil=PERFIL_DO_USUARIO)
    
    print("\n" + "="*50)
    print("TOKEN GERADO COM SUCESSO:")
    print("="*50)
    print(token)
    print("="*50 + "\n")