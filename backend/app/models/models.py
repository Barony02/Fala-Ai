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
    perfil = Column(Enum('Solicitante', 'Gestor'), default='Solicitante')
    setor_id = Column(Integer, ForeignKey('setores.id'))
    ativo = Column(Boolean, default=True)
    tentativas_login = Column(Integer, default=0)
    bloqueado_ate = Column(DateTime, nullable=True)

class Chamado(Base):
    __tablename__ = "chamados"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(String(1000), nullable=False)
    setor_solicitante_id = Column(Integer, ForeignKey('setores.id'), nullable=False)
    setor_responsavel_id = Column(Integer, ForeignKey('setores.id'), nullable=False)
    status = Column(Enum('Aberto', 'Em Progresso', 'Fechado'), default='Aberto')
    prioridade = Column(Enum('Baixa', 'Média', 'Alta'), default='Média')
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    data_criacao = Column(DateTime, nullable=False)
    data_atualizacao = Column(DateTime, nullable=False)
    
    # Relacionamento com Anexos
    anexos = relationship("Anexo", back_populates="chamado", cascade="all, delete-orphan")


class Anexo(Base):
    __tablename__ = "anexos"
    
    id = Column(Integer, primary_key=True, index=True)
    chamado_id = Column(Integer, ForeignKey('chamados.id'), nullable=False)
    nome_original = Column(String(255), nullable=False)  # Nome do arquivo original (ex: documento.pdf)
    nome_armazenado = Column(String(255), nullable=False)  # Nome único no servidor (ex: 1623456789_documento.pdf)
    caminho = Column(String(500), nullable=False)  # Caminho relativo (ex: /uploads/1623456789_documento.pdf)
    tamanho = Column(Integer, nullable=False)  # Tamanho em bytes
    tipo_mime = Column(String(50), nullable=False)  # Tipo (ex: application/pdf)
    data_upload = Column(DateTime, nullable=False)
    
    # Relacionamento com Chamado
    chamado = relationship("Chamado", back_populates="anexos")