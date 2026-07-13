import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

EXTENSOES_PERMITIDAS = {'.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx', '.xlsx', '.txt'}
TAMANHO_MAXIMO_MB = 10
TAMANHO_MAXIMO_BYTES = TAMANHO_MAXIMO_MB * 1024 * 1024
