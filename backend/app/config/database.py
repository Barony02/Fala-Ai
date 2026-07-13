import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Para execução local direta, use o MySQL publicado pelo docker-compose em localhost:3307.
# Dentro do container, o docker-compose sobrescreve esta variável para apontar para "db:3306".
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:senhachamadosmariana@localhost:3307/camara_chamados",
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
