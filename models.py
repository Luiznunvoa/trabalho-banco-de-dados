from sqlalchemy import (
    create_engine, Column, Integer, String, Numeric, Date, Time, 
    Boolean, Text, ForeignKey, BigInteger, Enum, DECIMAL, TIMESTAMP, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship
import enum
# Importa o TypeEngine do SQLAlchemy para o utilitário de drop de ENUMs
from sqlalchemy.types import TypeEngine 

# Base deve ser importada no seu arquivo principal se estiver em um arquivo separado
Base = declarative_base() 

# Definição do Esquema
SCHEMA = "teste"

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
    Droppa todas as tabelas e, em seguida, droppa explicitamente os tipos ENUM 
    com CASCADE para evitar o erro "DependentObjectsStillExist" do PostgreSQL.
    """
    conn = engine.connect()
    with conn.begin():
        # 1. Tenta dropar todas as tabelas 
        Base.metadata.drop_all(engine)

        # 2. Droppa explicitamente os tipos ENUM com CASCADE para forçar a remoção, 
        # mesmo que as tabelas não tenham sido removidas por completo no passo 1.
        
        enum_types = [TipoCanal, StatusPagamento]
        for enum_cls in enum_types:
            enum_name = enum_cls.__name__.lower()
            # Adição do CASCADE
            sql_drop_type = f"DROP TYPE IF EXISTS {SCHEMA}.{enum_name} CASCADE"
            print(f"-> Tentando dropar tipo ENUM com CASCADE: {sql_drop_type}")
            conn.execute(sql_drop_type)


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
    # OBSERVAÇÃO: A FK aqui é para Usuario.nick, o que requer que nick seja INDEXADO (UNIQUE já resolve)
    nick_streamer = Column(String(255), ForeignKey(f"{SCHEMA}.usuario.nick", onupdate="CASCADE", ondelete="CASCADE"))
    
    nome = Column(String(255), nullable=False)
    # Uso do ENUM que causava o problema de dependência
    tipo = Column(Enum(TipoCanal, name='tipo_canal'), nullable=False)
    data = Column(Date, nullable=False)
    descricao = Column(String(255))
    qtd_visualizacoes = Column(Integer, nullable=False)


class Patrocinio(Base):
    __tablename__ = "patrocinio"
    id = Column(Integer, primary_key=True, autoincrement=True)
    __table_args__ = (
        UniqueConstraint("nro_empresa", "id_canal"),
        {'schema': SCHEMA}
    )

    nro_empresa = Column(Integer, ForeignKey(f"{SCHEMA}.empresa.nro", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    id_canal = Column(Integer, ForeignKey(f"{SCHEMA}.canal.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
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
        UniqueConstraint("id_canal", "titulo", "data_h"), 
        {'schema': SCHEMA}
    )

    id_canal = Column(Integer, ForeignKey(f"{SCHEMA}.canal.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    titulo = Column(String(255))
    data_h = Column(Date) 
    tema = Column(String(64))
    duracao = Column(Time)
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
    # CORREÇÃO: Reordenado para (Constraint, Dictionary)
    __table_args__ = (UniqueConstraint("num_seq"), {'schema': SCHEMA})

    id_video = Column(BigInteger, ForeignKey(f"{SCHEMA}.video.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    num_seq = Column(BigInteger, primary_key=True, autoincrement=True) 

    id_usuario = Column(Integer, ForeignKey(f"{SCHEMA}.usuario.id", onupdate="CASCADE", ondelete="SET NULL"))
    texto = Column(Text, nullable=False)
    data_h = Column(TIMESTAMP, nullable=False)
    coment_on = Column(Boolean, nullable=False, default=True)


class Doacao(Base):
    __tablename__ = "doacao"
    # CORREÇÃO: Usando dicionário direto
    __table_args__ = {'schema': SCHEMA}

    id_comentario = Column(BigInteger, ForeignKey(f"{SCHEMA}.comentario.num_seq", ondelete="CASCADE"), primary_key=True)
    valor = Column(DECIMAL(10, 2), nullable=False)
    # Uso do ENUM que causava o problema de dependência
    status_pagamento = Column(Enum(StatusPagamento, name='status_pagamento'), nullable=False, default=StatusPagamento.PENDENTE)


class Bitcoin(Base):
    __tablename__ = "bitcoin"
    # CORREÇÃO: Usando dicionário direto
    __table_args__ = {'schema': SCHEMA}

    id_doacao = Column(BigInteger, ForeignKey(f"{SCHEMA}.doacao.id_comentario", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    tx_id = Column(String(64), primary_key=True)


class CartaoCredito(Base):
    __tablename__ = "cartaocredito"
    __table_args__ = (
        UniqueConstraint("num", "bandeira"),
        {'schema': SCHEMA}
    )

    id_doacao = Column(BigInteger, ForeignKey(f"{SCHEMA}.doacao.id_comentario", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    num = Column(String(16), primary_key=True)
    bandeira = Column(String(32))


class Paypal(Base):
    __tablename__ = "paypal"
    # CORREÇÃO: Usando dicionário direto
    __table_args__ = {'schema': SCHEMA}

    id_doacao = Column(BigInteger, ForeignKey(f"{SCHEMA}.doacao.id_comentario", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    id = Column(Integer, primary_key=True)


class MecPlat(Base):
    __tablename__ = "mecplat"
    # CORREÇÃO: Usando dicionário direto
    __table_args__ = {'schema': SCHEMA}

    id_doacao = Column(BigInteger, ForeignKey(f"{SCHEMA}.doacao.id_comentario", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    seq = Column(Integer, primary_key=True)
