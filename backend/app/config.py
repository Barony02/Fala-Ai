import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).parent.parent

# Diretório de uploads
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# Criar pasta de uploads se não existir
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Extensões permitidas
EXTENSOES_PERMITIDAS = {'.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx', '.xlsx', '.txt'}

# Tamanho máximo de arquivo: 10MB
TAMANHO_MAXIMO_MB = 10
TAMANHO_MAXIMO_BYTES = TAMANHO_MAXIMO_MB * 1024 * 1024