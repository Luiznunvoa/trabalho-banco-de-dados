CREATE SCHEMA IF NOT EXISTS core;
SET SEARCH_PATH TO core;

-- Habilita a extensão btree_gist necessária para EXCLUSION CONSTRAINTS com tipos não-geométricos
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TYPE TIPO_CANAL AS ENUM ('privado', 'publico', 'misto');

CREATE TYPE STATUSPAGAMENTO AS ENUM ('PENDENTE', 'CONCLUIDO', 'FALHOU');

-- ID Artificial 'nro': Criado pois o nome da empresa (VARCHAR) não é adequado como chave primária
-- devido a possibilidade de mudanças (rebranding), homônimos, e ineficiência em JOINs.
-- INT é mais eficiente em indexação e relacionamentos (FK em Plataforma, Patrocinio, EmpresaPais).
-- Capacidade: ~2.1 bilhões de empresas, suficiente para cenário mundial.
CREATE TABLE Empresa ( -- OK
  nro INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  nome_fantasia VARCHAR(255)
);

-- ID Artificial 'id': Criado para simplificar relacionamentos, pois VARCHAR(100) é ineficiente
-- como FK em Pais. INT ocupa 4 bytes vs até 100 bytes do VARCHAR, melhorando performance de JOINs.
-- Permite múltiplas moedas com nomes longos (ex: "Dólar Americano", "Real Brasileiro") sem
-- overhead em chaves estrangeiras. Evita problemas com encoding e caracteres especiais.
CREATE TABLE Conversao (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  moeda VARCHAR(100) NOT NULL,
  fator_conver NUMERIC(18, 8) NOT NULL
);

CREATE TABLE Pais (
  ddi INTEGER NOT NULL PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  id_moeda INTEGER NOT NULL,

  FOREIGN KEY (id_moeda) REFERENCES Conversao (id)
  ON UPDATE CASCADE ON DELETE CASCADE
);

-- ID Artificial 'nro': Criado pois nome da plataforma (VARCHAR) pode mudar ou ser duplicado
-- em diferentes contextos. INT simplifica relacionamentos em Canal e PlataformaUsuario.
-- Melhora performance de indexação e JOINs. Evita problemas com renomeações da plataforma
-- (ex: Twitter -> X), mantendo integridade referencial sem cascata de UPDATEs.
CREATE TABLE Plataforma (
  nro INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  data_fund DATE NOT NULL,
  empresa_fund INTEGER NOT NULL,
  empresa_respo INTEGER NOT NULL,

  FOREIGN KEY (empresa_fund) REFERENCES Empresa (nro)
  ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (empresa_respo) REFERENCES Empresa (nro)
  ON UPDATE CASCADE ON DELETE CASCADE
);

-- ID Artificial 'id': Essencial pois nick (VARCHAR) é mutável e inadequado como PK.
-- Usuários frequentemente mudam nicknames, causaria cascata de UPDATEs em 8+ tabelas
-- (Canal, Comentario, Doacao, Inscricao, Participa, PlataformaUsuario, StreamerPais).
-- INT ocupa 4 bytes vs até 100 do VARCHAR, melhorando drasticamente performance de JOINs.
-- Facilita integração com sistemas externos que usam IDs numéricos.
CREATE TABLE Usuario (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nick VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  data_nasc DATE NOT NULL,
  telefone VARCHAR(20) NOT NULL,
  pais_residencia INTEGER,
  end_postal VARCHAR(50),
  active BOOLEAN NOT NULL DEFAULT True,

  UNIQUE (nick),
  UNIQUE (email),

  FOREIGN KEY (pais_residencia) REFERENCES Pais (ddi)
  ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE PlataformaUsuario (
  nro_plataforma INTEGER NOT NULL,
  id_usuario INTEGER NOT NULL,
  nro_usuario INTEGER,

  PRIMARY KEY (nro_plataforma, id_usuario),
  UNIQUE (nro_plataforma, nro_usuario),

  FOREIGN KEY (nro_plataforma) REFERENCES Plataforma (nro)
  ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (id_usuario) REFERENCES Usuario (id)
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE StreamerPais (
  id_usuario INTEGER NOT NULL,
  ddi_pais INTEGER NOT NULL,
  nro_passaporte VARCHAR(50),

  PRIMARY KEY (id_usuario, ddi_pais),
  UNIQUE (nro_passaporte),

  FOREIGN KEY (id_usuario) REFERENCES Usuario (id)
  ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (ddi_pais) REFERENCES Pais (ddi)
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE EmpresaPais (
  nro_empresa INTEGER NOT NULL,
  ddi_pais INTEGER NOT NULL,
  id_nacional VARCHAR(100),

  PRIMARY KEY (nro_empresa, ddi_pais),
  UNIQUE (ddi_pais, id_nacional),

  FOREIGN KEY (nro_empresa) REFERENCES Empresa (nro)
  ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (ddi_pais) REFERENCES Pais (ddi)
  ON UPDATE CASCADE ON DELETE CASCADE
);

-- ID Artificial 'id': Criado pois nome do canal (VARCHAR) pode ser renomeado e não é único
-- globalmente (apenas dentro da plataforma). Canal é altamente referenciado em Video, 
-- Patrocinio, NivelCanal - usar chave composta (nome, nro_plataforma) seria ineficiente,
-- ocupando ~259 bytes vs 4 bytes do INT. Melhora significativa em performance de JOINs e índices.
-- Capacidade: ~2.1 bilhões de canais, suficiente considerando YouTube com ~113.9 milhões.
CREATE TABLE Canal (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_streamer INT NOT NULL,
  nro_plataforma INT NOT NULL,
  nome VARCHAR(255) NOT NULL,
  tipo TIPO_CANAL NOT NULL,
  qtd_visualizacoes INT NOT NULL,
  data_criacao DATE NOT NULL,
  descricao VARCHAR(255),

  UNIQUE (nome, nro_plataforma),

  FOREIGN KEY (nro_plataforma) REFERENCES Plataforma (nro)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_streamer) REFERENCES Usuario (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Patrocinio (
  nro_empresa INT NOT NULL,
  id_canal INT NOT NULL,
  valor DECIMAL(10, 2),

  PRIMARY KEY (nro_empresa, id_canal),

  FOREIGN KEY (nro_empresa) REFERENCES Empresa (nro)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_canal) REFERENCES Canal (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

-- ID Artificial 'id': Criado pois nível (VARCHAR 127) é descritivo e mutável, inadequado como PK.
-- Chave composta (id_canal, nivel) seria ineficiente em Inscricao, ocupando ~131 bytes vs 4 do INT.
-- Níveis podem ter nomes longos ("Assinante Premium Plus Gold") e serem renomeados.
-- INT oferece performance superior em JOINs e indexação. Capacidade de ~2.1 bilhões de registros
-- é suficiente, considerando que cada canal tem poucos níveis (tipicamente 3-5).
CREATE TABLE NivelCanal (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_canal INT NOT NULL,
  nivel VARCHAR(127) NOT NULL,
  valor DECIMAL(5, 2),
  gif VARCHAR(512),

  UNIQUE (id_canal, nivel),

  FOREIGN KEY (id_canal) REFERENCES Canal (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Inscricao (
  id_nivel INT,
  id_membro INT,

  PRIMARY KEY (id_nivel, id_membro),

  FOREIGN KEY (id_membro) REFERENCES Usuario (id)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_nivel) REFERENCES NivelCanal (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

-- ID Artificial 'id': BIGINT escolhido pois vídeos são entidades de altíssimo volume.
-- Alternativa seria chave composta (id_canal, titulo, dataH), ocupando ~264 bytes vs 8 do BIGINT.
-- Simplifica drasticamente relacionamentos em Participa, Comentario, Doacao e subtipos de pagamento.
-- Título pode ser alterado e não é único (mesmo título em datas diferentes).
-- BIGINT suporta ~9.2 quintilhões de vídeos, essencial dado que YouTube recebe 720k horas/dia.
-- Mesma ocupação de memória (8 bytes) que chave composta, mas com performance muito superior.
CREATE TABLE Video (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_canal INT NOT NULL,
  titulo VARCHAR(255),
  dataH DATE,
  tema VARCHAR(64),
  duracao TIME,
  visu_simult INT,
  visu_total INT,

  UNIQUE (id_canal, titulo, dataH),

  FOREIGN KEY (id_canal) REFERENCES Canal (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Participa (
  id_video BIGINT,
  id_streamer INT,

  PRIMARY KEY (id_video, id_streamer),

  FOREIGN KEY (id_streamer) REFERENCES Usuario (id)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_video) REFERENCES Video (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Comentario (
  id_video BIGINT NOT NULL,
  num_seq INT NOT NULL,
  id_usuario INT NOT NULL,
  texto TEXT NOT NULL,
  dataH TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  coment_on BOOLEAN NOT NULL DEFAULT False,

  PRIMARY KEY (id_video, num_seq, id_usuario),

  FOREIGN KEY (id_video) REFERENCES Video (id)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_usuario) REFERENCES Usuario (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

-- RESTRIÇÃO DE MÉTODO DE PAGAMENTO ÚNICO:
-- Uma doação pode ter apenas UM método de pagamento (Bitcoin, CartaoCredito, Paypal ou MecPlat).
-- Esta restrição é garantida através de EXCLUSION CONSTRAINTS que utilizam a extensão btree_gist.
-- Cada tabela de pagamento possui uma constraint que impede a existência de registros nas outras
-- tabelas para a mesma doação, garantindo que apenas um método seja usado por doação.
-- JUSTIFICATIVA: Não faz sentido uma única doação possuir dois pagamentos diferentes.
CREATE TABLE Doacao (
  id_video BIGINT NOT NULL,
  num_seq INT NOT NULL,
  id_usuario INT NOT NULL,
  valor DECIMAL(10, 2) NOT NULL,
  status_pagamento STATUSPAGAMENTO NOT NULL DEFAULT 'PENDENTE',

  PRIMARY KEY (id_video, num_seq, id_usuario),

  FOREIGN KEY (id_video, num_seq, id_usuario) REFERENCES Comentario (id_video, num_seq, id_usuario)
  ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Bitcoin (
  id_video_doacao BIGINT,
  seq_doacao INT,
  id_usuario INT NOT NULL,
  tx_id VARCHAR(64),

  PRIMARY KEY (id_video_doacao, seq_doacao, tx_id, id_usuario),

  -- EXCLUSION CONSTRAINT: Garante que não existe registro em outras tabelas para a mesma doação
  -- usando a chave composta (id_video_doacao, seq_doacao, id_usuario)
  CONSTRAINT bitcoin_exclusao_metodo_unico
  EXCLUDE USING gist (
    id_video_doacao WITH =,
    seq_doacao WITH =,
    id_usuario WITH =
  ),

  FOREIGN KEY (id_video_doacao, seq_doacao, id_usuario) REFERENCES Doacao (
    id_video, num_seq, id_usuario
  )
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE CartaoCredito (
  id_video_doacao BIGINT,
  seq_doacao INT,
  num VARCHAR(24),
  id_usuario INT NOT NULL,
  bandeira VARCHAR(32),

  PRIMARY KEY (id_video_doacao, seq_doacao, num, id_usuario),
  UNIQUE (num, bandeira),

  -- EXCLUSION CONSTRAINT: Garante que não existe registro em outras tabelas para a mesma doação
  CONSTRAINT cartao_exclusao_metodo_unico
  EXCLUDE USING gist (
    id_video_doacao WITH =,
    seq_doacao WITH =,
    id_usuario WITH =
  ),

  FOREIGN KEY (id_video_doacao, seq_doacao, id_usuario) REFERENCES Doacao (
    id_video, num_seq, id_usuario
  )
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Paypal (
  id_video_doacao BIGINT,
  seq_doacao INT,
  id_usuario INT NOT NULL,
  id INT,

  PRIMARY KEY (id_video_doacao, seq_doacao, id, id_usuario),

  -- EXCLUSION CONSTRAINT: Garante que não existe registro em outras tabelas para a mesma doação
  CONSTRAINT paypal_exclusao_metodo_unico
  EXCLUDE USING gist (
    id_video_doacao WITH =,
    seq_doacao WITH =,
    id_usuario WITH =
  ),

  FOREIGN KEY (id_video_doacao, seq_doacao, id_usuario) REFERENCES Doacao (
    id_video, num_seq, id_usuario
  )
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE MecPlat (
  id_video_doacao BIGINT,
  seq_doacao INT,
  id_usuario INT NOT NULL,
  seq INT,

  PRIMARY KEY (id_video_doacao, seq_doacao, seq, id_usuario),

  -- EXCLUSION CONSTRAINT: Garante que não existe registro em outras tabelas para a mesma doação
  CONSTRAINT mecplat_exclusao_metodo_unico
  EXCLUDE USING gist (
    id_video_doacao WITH =,
    seq_doacao WITH =,
    id_usuario WITH =
  ),

  FOREIGN KEY (id_video_doacao, seq_doacao, id_usuario) REFERENCES Doacao (
    id_video, num_seq, id_usuario
  )
  ON UPDATE CASCADE ON DELETE CASCADE
);

