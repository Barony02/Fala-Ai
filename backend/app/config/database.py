from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Substitua pelas credenciais do seu ambiente Linux local
DATABASE_URL = f"mysql+pymysql://root:senhachamadosmariana@db:3306/camara_chamados"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()