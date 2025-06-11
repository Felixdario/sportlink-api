from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, DECIMAL, Table, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class MsgPayload(BaseModel):
    msg_id: Optional[int]
    msg_name: str


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    avatar = Column(String(255))
    username = Column(String(50), unique=True)
    bio = Column(Text)
    cidade = Column(String(100))
    estado = Column(String(100))
    data_criacao = Column(DateTime, default=datetime.utcnow)

    atleta = relationship("Atleta", back_populates="usuario", uselist=False)
    quadras = relationship("Quadra", back_populates="dono")


class Atleta(Base):
    __tablename__ = "atletas"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    nivel = Column(String(50))
    pontos = Column(Integer, default=0)
    conquistas = Column(Integer, default=0)
    vitorias = Column(Integer, default=0)
    derrotas = Column(Integer, default=0)
    empates = Column(Integer, default=0)

    usuario = relationship("Usuario", back_populates="atleta")


atleta_esportes = Table(
    "atleta_esportes", Base.metadata,
    Column("atleta_id", Integer, ForeignKey("atletas.id"), primary_key=True),
    Column("esporte_id", Integer, ForeignKey("esportes.id"), primary_key=True)
)

quadra_esportes = Table(
    "quadra_esportes", Base.metadata,
    Column("quadra_id", Integer, ForeignKey("quadras.id"), primary_key=True),
    Column("esporte_id", Integer, ForeignKey("esportes.id"), primary_key=True)
)


class Esporte(Base):
    __tablename__ = "esportes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False)


class Quadra(Base):
    __tablename__ = "quadras"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    endereco = Column(String(255), nullable=False)
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(String(100))
    latitude = Column(DECIMAL(9, 6))
    longitude = Column(DECIMAL(9, 6))
    avaliacao = Column(DECIMAL(2, 1))
    avaliacoes = Column(Integer)
    preco = Column(String(50))
    disponivel = Column(Boolean, default=True)
    imagem = Column(String(255))
    dono_id = Column(Integer, ForeignKey("usuarios.id"))

    dono = relationship("Usuario", back_populates="quadras")
    esportes = relationship("Esporte", secondary=quadra_esportes, backref="quadras")


class Competicao(Base):
    __tablename__ = "competicoes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    esporte_id = Column(Integer, ForeignKey("esportes.id"))
    data_inicio = Column(DateTime)
    data_fim = Column(DateTime)
    local = Column(String(100))
    endereco = Column(String(255))
    latitude = Column(DECIMAL(9, 6))
    longitude = Column(DECIMAL(9, 6))
    vagas = Column(Integer)
    premio = Column(String(255))
    taxa_inscricao = Column(String(50))
    imagem = Column(String(255))
    publica = Column(Boolean, default=True)
    inscricoes_automaticas = Column(Boolean, default=True)
    organizador_id = Column(Integer, ForeignKey("usuarios.id"))
    status = Column(String(50), default="inscricoes")


class CompeticaoParticipante(Base):
    __tablename__ = "competicao_participantes"
    id = Column(Integer, primary_key=True, index=True)
    competicao_id = Column(Integer, ForeignKey("competicoes.id"))
    atleta_id = Column(Integer, ForeignKey("atletas.id"))
    status = Column(String(50), default="pendente")
    data_inscricao = Column(DateTime, default=datetime.utcnow)


class CompeticaoRegra(Base):
    __tablename__ = "competicao_regras"
    id = Column(Integer, primary_key=True, index=True)
    competicao_id = Column(Integer, ForeignKey("competicoes.id"))
    regra = Column(Text)


class Conversa(Base):
    __tablename__ = "conversas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100))
    tipo = Column(String(20), nullable=False)  # individual, grupo
    avatar = Column(String(255))
    data_criacao = Column(DateTime, default=datetime.utcnow)


class ConversaParticipante(Base):
    __tablename__ = "conversa_participantes"
    conversa_id = Column(Integer, ForeignKey("conversas.id"), primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    status = Column(String(20), default="ativo")  # ativo, removido, etc


class Mensagem(Base):
    __tablename__ = "mensagens"
    id = Column(Integer, primary_key=True, index=True)
    conversa_id = Column(Integer, ForeignKey("conversas.id"))
    remetente_id = Column(Integer, ForeignKey("usuarios.id"))
    texto = Column(Text)
    data_envio = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="enviada")  # enviada, entregue, lida


class Conquista(Base):
    __tablename__ = "conquistas"
    id = Column(Integer, primary_key=True, index=True)
    atleta_id = Column(Integer, ForeignKey("atletas.id"))
    nome = Column(String(100))
    descricao = Column(Text)
    icone = Column(String(50))
    data_conquista = Column(Date)

class QuadraAvaliacao(Base):
    __tablename__ = "quadra_avaliacoes"
    id = Column(Integer, primary_key=True, index=True)
    quadra_id = Column(Integer, ForeignKey("quadras.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    nota = Column(Integer)
    comentario = Column(Text)
    data_avaliacao = Column(DateTime, default=datetime.utcnow)

class Atividade(Base):
    __tablename__ = "atividades"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20))  # partida, competicao
    nome = Column(String(100))
    data = Column(Date)
    local = Column(String(100))
    quadra_id = Column(Integer, ForeignKey("quadras.id"))
    status = Column(String(20), default="pendente")  # confirmado, pendente
    organizador_id = Column(Integer, ForeignKey("usuarios.id"))

class AtividadeParticipante(Base):
    __tablename__ = "atividade_participantes"
    atividade_id = Column(Integer, ForeignKey("atividades.id"), primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    status = Column(String(20), default="confirmado")
