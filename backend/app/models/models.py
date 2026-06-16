from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.config.database import Base

class Setor(Base):
    __tablename__ = "setores"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)
    sigla = Column(String(10), unique=True, nullable=False)

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(Enum('Solicitante', 'Técnico', 'Gestor'), default='Solicitante')
    setor_id = Column(Integer, ForeignKey('setores.id'))
    ativo = Column(Boolean, default=True)
    tentativas_login = Column(Integer, default=0)
    bloqueado_ate = Column(DateTime, nullable=True)