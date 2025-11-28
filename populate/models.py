from sqlalchemy import (
    create_engine, Column, Integer, String, Numeric, Date, Time, 
    Boolean, Text, ForeignKey, BigInteger, Enum, DECIMAL, TIMESTAMP, UniqueConstraint,
    ForeignKeyConstraint, text, Interval
)
from sqlalchemy.orm import declarative_base, relationship
import enum
# Importa o TypeEngine do SQLAlchemy para o utilitário de drop de ENUMs
from sqlalchemy.types import TypeEngine 

# Base deve ser importada no seu arquivo principal se estiver em um arquivo separado
Base = declarative_base() 

# Definição do Esquema
SCHEMA = "core"

# ================= ENUMS ===================

class TipoCanal(enum.Enum):
    privado = "privado"
    publico = "publico"
    misto = "misto"


class StatusPagamento(enum.Enum):
    PENDENTE = "PENDENTE"
    CONCLUIDO = "CONCLUIDO"
    FALHOU = "FALHOU"


# ================= UTILITÁRIO DE ENUMS PARA POSTGRESQL ===================

def drop_all_and_enums(engine):
    """
    Droppa todo o schema especificado com CASCADE para garantir que todos os objetos,
    incluindo tabelas e tipos ENUM, sejam removidos. Em seguida, recria o schema.
    Esta é uma abordagem mais robusta para garantir um ambiente limpo.
    """
    conn = engine.connect()
    with conn.begin():
        print(f"-> Droppando schema '{SCHEMA}' com CASCADE...")
        conn.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
        print(f"-> Criando schema '{SCHEMA}'...")
        conn.execute(text(f'CREATE SCHEMA "{SCHEMA}"'))


# ================= TABELAS =================

class Empresa(Base):
    __tablename__ = "empresa"
    nro = Column(Integer, primary_key=True, autoincrement=True) 
    # CORREÇÃO: Usando dicionário direto
    __table_args__ = {'schema': SCHEMA}

    nome = Column(String(255), nullable=False)
    nome_fantasia = Column(String(255))


class Conversao(Base):
    __tablename__ = "conversao"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # CORREÇÃO: Usando dicionário direto
    __table_args__ = {'schema': SCHEMA}

    moeda = Column(String(100), nullable=False)
    fator_conver = Column(Numeric(18, 8), nullable=False)


class Pais(Base):
    __tablename__ = "pais"
    # CORREÇÃO: Usando dicionário direto
    __table_args__ = {'schema': SCHEMA}

    ddi = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    id_moeda = Column(Integer, ForeignKey(f"{SCHEMA}.conversao.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)


class Plataforma(Base):
    __tablename__ = "plataforma"
    nro = Column(Integer, primary_key=True, autoincrement=True)
    # CORREÇÃO: Usando dicionário direto
    __table_args__ = {'schema': SCHEMA}

    nome = Column(String(255), nullable=False)
    data_fund = Column(Date, nullable=False)
    empresa_fund = Column(Integer, ForeignKey(f"{SCHEMA}.empresa.nro", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    empresa_respo = Column(Integer, ForeignKey(f"{SCHEMA}.empresa.nro", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)


class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # CORREÇÃO: Usando dicionário direto
    __table_args__ = {'schema': SCHEMA}

    nick = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    data_nasc = Column(Date, nullable=False)
    telefone = Column(String(20), nullable=False)
    pais_residencia = Column(Integer, ForeignKey(f"{SCHEMA}.pais.ddi", onupdate="CASCADE", ondelete="SET NULL"))
    end_postal = Column(String(50))
    data_exclusao = Column(TIMESTAMP, default=None)


class PlataformaUsuario(Base):
    __tablename__ = "plataformausuario"
    # CORREÇÃO: Reordenado para (Constraint, Dictionary)
    __table_args__ = (UniqueConstraint("nro_plataforma", "nro_usuario"), {'schema': SCHEMA})

    nro_plataforma = Column(Integer, ForeignKey(f"{SCHEMA}.plataforma.nro", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    id_usuario = Column(Integer, ForeignKey(f"{SCHEMA}.usuario.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    nro_usuario = Column(Integer)


class StreamerPais(Base):
    __tablename__ = "streamerpais"
    # CORREÇÃO: Reordenado para (Constraint, Dictionary)
    __table_args__ = (UniqueConstraint("nro_passaporte"), {'schema': SCHEMA})

    id_usuario = Column(Integer, ForeignKey(f"{SCHEMA}.usuario.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    ddi_pais = Column(Integer, ForeignKey(f"{SCHEMA}.pais.ddi", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    nro_passaporte = Column(String(50))


class EmpresaPais(Base):
    __tablename__ = "empresapais"
    __table_args__ = (
        UniqueConstraint("ddi_pais", "id_nacional"), 
        {'schema': SCHEMA}
    )

    nro_empresa = Column(Integer, ForeignKey(f"{SCHEMA}.empresa.nro", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    ddi_pais = Column(Integer, ForeignKey(f"{SCHEMA}.pais.ddi", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    id_nacional = Column(String(100))


class Canal(Base):
    __tablename__ = "canal"
    id = Column(Integer, primary_key=True, autoincrement=True)
    __table_args__ = (
        UniqueConstraint("nome", "nro_plataforma"),
        {'schema': SCHEMA}
    )

    nro_plataforma = Column(Integer, ForeignKey(f"{SCHEMA}.plataforma.nro", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    id_streamer = Column(Integer, ForeignKey(f"{SCHEMA}.usuario.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    
    nome = Column(String(255), nullable=False)
    # Uso do ENUM que causava o problema de dependência
    tipo = Column(Enum(TipoCanal, name='tipo_canal', schema=SCHEMA, create_type=False), nullable=False)
    data_criacao = Column(Date, nullable=False)
    descricao = Column(String(255))
    qtd_visualizacoes = Column(Integer, nullable=False)


class Patrocinio(Base):
    __tablename__ = "patrocinio"
    __table_args__ = {'schema': SCHEMA}

    nro_empresa = Column(Integer, ForeignKey(f"{SCHEMA}.empresa.nro", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    id_canal = Column(Integer, ForeignKey(f"{SCHEMA}.canal.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    valor = Column(DECIMAL(10, 2))


class NivelCanal(Base):
    __tablename__ = "nivelcanal"
    id = Column(Integer, primary_key=True, autoincrement=True)
    __table_args__ = (
        UniqueConstraint("id_canal", "nivel"),
        {'schema': SCHEMA}
    )

    id_canal = Column(Integer, ForeignKey(f"{SCHEMA}.canal.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    nivel = Column(String(127), nullable=False)
    valor = Column(DECIMAL(5, 2))
    gif = Column(String(512))


class Inscricao(Base):
    __tablename__ = "inscricao"
    # CORREÇÃO: Usando dicionário direto
    __table_args__ = {'schema': SCHEMA}

    id_nivel = Column(Integer, ForeignKey(f"{SCHEMA}.nivelcanal.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    id_membro = Column(Integer, ForeignKey(f"{SCHEMA}.usuario.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)


class Video(Base):
    __tablename__ = "video"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    __table_args__ = (
        UniqueConstraint("id_canal", "titulo", "datah"), 
        {'schema': SCHEMA}
    )

    id_canal = Column(Integer, ForeignKey(f"{SCHEMA}.canal.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    titulo = Column(String(255))
    data_h = Column("datah", TIMESTAMP) 
    tema = Column(String(64))
    duracao = Column(Interval)
    visu_simult = Column(Integer)
    visu_total = Column(Integer)


class Participa(Base):
    __tablename__ = "participa"
    # CORREÇÃO: Usando dicionário direto
    __table_args__ = {'schema': SCHEMA}

    id_video = Column(BigInteger, ForeignKey(f"{SCHEMA}.video.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    id_streamer = Column(Integer, ForeignKey(f"{SCHEMA}.usuario.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)


class Comentario(Base):
    __tablename__ = "comentario"
    __table_args__ = (
        UniqueConstraint("id_video", "num_seq"),
        {'schema': SCHEMA}
    )

    id_video = Column(BigInteger, ForeignKey(f"{SCHEMA}.video.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    num_seq = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey(f"{SCHEMA}.usuario.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    
    texto = Column(Text, nullable=False)
    data_h = Column("datah", TIMESTAMP, nullable=False)
    coment_on = Column(Boolean, nullable=False, default=False)


class Doacao(Base):
    __tablename__ = "doacao"

    id_video = Column(BigInteger, primary_key=True)
    num_seq = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, primary_key=True)
    
    valor = Column(DECIMAL(10, 2), nullable=False)
    status_pagamento = Column(Enum(StatusPagamento, name='statuspagamento', schema=SCHEMA, create_type=False), nullable=False, default=StatusPagamento.PENDENTE)
    
    __table_args__ = (
        ForeignKeyConstraint(['id_video', 'num_seq', 'id_usuario'], [f"{SCHEMA}.comentario.id_video", f"{SCHEMA}.comentario.num_seq", f"{SCHEMA}.comentario.id_usuario"], onupdate="CASCADE", ondelete="CASCADE"),
        {'schema': SCHEMA}
    )


class Bitcoin(Base):
    __tablename__ = "bitcoin"

    id_video_doacao = Column(BigInteger, primary_key=True)
    seq_doacao = Column(Integer, primary_key=True)
    tx_id = Column(String(64), primary_key=True)
    id_usuario = Column(Integer, nullable=False, primary_key=True)
    
    __table_args__ = (
        ForeignKeyConstraint(['id_video_doacao', 'seq_doacao', 'id_usuario'], [f"{SCHEMA}.doacao.id_video", f"{SCHEMA}.doacao.num_seq", f"{SCHEMA}.doacao.id_usuario"], onupdate="CASCADE", ondelete="CASCADE"),
        {'schema': SCHEMA}
    )


class CartaoCredito(Base):
    __tablename__ = "cartaocredito"

    id_video_doacao = Column(BigInteger, primary_key=True)
    seq_doacao = Column(Integer, primary_key=True)
    num = Column(String(24), primary_key=True)
    id_usuario = Column(Integer, nullable=False, primary_key=True)
    bandeira = Column(String(32))
    
    __table_args__ = (
        ForeignKeyConstraint(['id_video_doacao', 'seq_doacao', 'id_usuario'], [f"{SCHEMA}.doacao.id_video", f"{SCHEMA}.doacao.num_seq", f"{SCHEMA}.doacao.id_usuario"], onupdate="CASCADE", ondelete="CASCADE"),
        UniqueConstraint("num", "bandeira"),
        {'schema': SCHEMA}
    )


class Paypal(Base):
    __tablename__ = "paypal"

    id_video_doacao = Column(BigInteger, primary_key=True)
    seq_doacao = Column(Integer, primary_key=True)
    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, nullable=False, primary_key=True)
    
    __table_args__ = (
        ForeignKeyConstraint(['id_video_doacao', 'seq_doacao', 'id_usuario'], [f"{SCHEMA}.doacao.id_video", f"{SCHEMA}.doacao.num_seq", f"{SCHEMA}.doacao.id_usuario"], onupdate="CASCADE", ondelete="CASCADE"),
        {'schema': SCHEMA}
    )


class MecPlat(Base):
    __tablename__ = "mecplat"

    id_video_doacao = Column(BigInteger, primary_key=True)
    seq_doacao = Column(Integer, primary_key=True)
    seq = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, nullable=False, primary_key=True)
    
    __table_args__ = (
        ForeignKeyConstraint(['id_video_doacao', 'seq_doacao', 'id_usuario'], [f"{SCHEMA}.doacao.id_video", f"{SCHEMA}.doacao.num_seq", f"{SCHEMA}.doacao.id_usuario"], onupdate="CASCADE", ondelete="CASCADE"),
        {'schema': SCHEMA}
    )
