CREATE SCHEMA IF NOT EXISTS core2;
SET SEARCH_PATH TO core2;

-- As extensões btree_gist e pg_cron são instaladas em 00-extensions.sql

CREATE TYPE TIPO_CANAL AS ENUM ('privado', 'publico', 'misto');

CREATE TYPE STATUSPAGAMENTO AS ENUM ('PENDENTE', 'CONCLUIDO', 'FALHOU');

CREATE TABLE Empresa ( -- OK
  nro INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  nome_fantasia VARCHAR(255)
);

-- Só alteramos nome de moeda para id para facilitar a visualização
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

-- ID Artificial 'id': Criado pois 'nick' (VARCHAR) é mutável e dificulta integração com outras 
-- tabelas. INT é mais eficiente para JOINs e indexação, ocupando apenas 4 bytes vs ~100 do VARCHAR.
-- Uso de data_exclusao para conseguir manter dados mesmo após o delete do usuario
-- isso possibilita uma análise de negócios mais profunda e
-- a possibilidade de reativar um usuário
CREATE TABLE Usuario ( -- OK
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nick VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  data_nasc DATE NOT NULL,
  telefone VARCHAR(20) NOT NULL,
  pais_residencia INTEGER,
  end_postal VARCHAR(50),
  data_exclusao TIMESTAMP DEFAULT NULL,

  -- UNIQUE (nick): Garante unicidade do nickname na plataforma, evitando confusão entre usuários
  UNIQUE (nick),
  -- UNIQUE (email): Garante que cada email só pode estar associado a uma conta, 
  -- prevenindo duplicação de contas e facilitando recuperação de senha
  UNIQUE (email),

  FOREIGN KEY (pais_residencia) REFERENCES Pais (ddi)
  ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE PlataformaUsuario (
  nro_plataforma INTEGER NOT NULL,
  id_usuario INTEGER NOT NULL,
  nro_usuario INTEGER,

  PRIMARY KEY (nro_plataforma, id_usuario),
  -- UNIQUE (nro_plataforma, nro_usuario): Garante que o número de identificação do usuário
  -- seja único dentro de cada plataforma, evitando conflitos de identificação
  UNIQUE (nro_plataforma, nro_usuario),

  FOREIGN KEY (nro_plataforma) REFERENCES Plataforma (nro)
  ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (id_usuario) REFERENCES Usuario (id)
  ON UPDATE RESTRICT ON DELETE CASCADE
);

CREATE TABLE StreamerPais (
  id_usuario INTEGER NOT NULL,
  ddi_pais INTEGER NOT NULL,
  nro_passaporte VARCHAR(50),

  PRIMARY KEY (id_usuario, ddi_pais),
  -- UNIQUE (nro_passaporte): Garante unicidade global do passaporte, pois um passaporte
  -- não pode pertencer a múltiplos usuários ou países simultaneamente
  UNIQUE (nro_passaporte),

  FOREIGN KEY (id_usuario) REFERENCES Usuario (id)
  ON UPDATE RESTRICT ON DELETE CASCADE,
  FOREIGN KEY (ddi_pais) REFERENCES Pais (ddi)
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE EmpresaPais (
  nro_empresa INTEGER NOT NULL,
  ddi_pais INTEGER NOT NULL,
  id_nacional VARCHAR(100),

  PRIMARY KEY (nro_empresa, ddi_pais),
  -- UNIQUE (ddi_pais, id_nacional): Garante que cada ID nacional (CNPJ, EIN, etc.) seja
  -- único dentro de um país, pois cada país tem seu próprio sistema de identificação empresarial
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

  -- UNIQUE (nome, nro_plataforma): Garante que o nome do canal seja único dentro de cada
  -- plataforma, evitando confusão entre canais e permitindo que o mesmo nome exista em
  -- plataformas diferentes (ex: "GamersUnited" no YouTube e Twitch)
  UNIQUE (nome, nro_plataforma),

  FOREIGN KEY (nro_plataforma) REFERENCES Plataforma (nro)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_streamer) REFERENCES Usuario (id)
  ON DELETE RESTRICT ON UPDATE CASCADE
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

  -- UNIQUE (id_canal, nivel): Garante que não existam dois níveis com o mesmo nome dentro
  -- de um canal, evitando confusão para os membros (ex: não pode haver dois níveis "Gold")
  UNIQUE (id_canal, nivel),

  FOREIGN KEY (id_canal) REFERENCES Canal (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Inscricao (
  id_nivel INT,
  id_membro INT,

  PRIMARY KEY (id_nivel, id_membro),

  FOREIGN KEY (id_membro) REFERENCES Usuario (id)
  ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (id_nivel) REFERENCES NivelCanal (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

-- ID Artificial 'id': Criado pois titulo (VARCHAR 255) e dataH (TIMESTAMP) são ineficientes como PK.
-- Vídeo é altamente referenciado em Participa, Comentario, Doacao. Usar chave composta 
-- (id_canal, titulo, dataH) seria ineficiente, ocupando ~263 bytes vs 8 bytes do BIGINT.
-- BIGINT foi escolhido pois oferece capacidade para ~9 quintilhões de vídeos, suficiente
-- considerando que YouTube tem ~800 milhões de vídeos e cresce ~500h de conteúdo/minuto.
CREATE TABLE Video ( -- OK
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_canal INT NOT NULL,
  titulo VARCHAR(255),
  dataH TIMESTAMP,
  tema VARCHAR(64),
  duracao INTERVAL, -- para vídeos>24h
  visu_simult INT,
  visu_total INT,

  -- UNIQUE (id_canal, titulo, dataH): Garante que um canal não possa ter dois vídeos com
  -- o mesmo título na mesma data/hora, evitando duplicação acidental de uploads
  UNIQUE (id_canal, titulo, dataH),

  FOREIGN KEY (id_canal) REFERENCES Canal (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Participa (
  id_video BIGINT,
  id_streamer INT,

  PRIMARY KEY (id_video, id_streamer),

  FOREIGN KEY (id_streamer) REFERENCES Usuario (id)
  ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (id_video) REFERENCES Video (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Comentario (
  id_video BIGINT NOT NULL,
  num_seq INT NOT NULL,
  id_usuario INT NOT NULL,
  texto TEXT NOT NULL,
  dataH TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  coment_on BOOLEAN NOT NULL DEFAULT FALSE,

  PRIMARY KEY (id_video, num_seq, id_usuario),

  FOREIGN KEY (id_video) REFERENCES Video (id)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_usuario) REFERENCES Usuario (id)
  ON UPDATE CASCADE ON DELETE RESTRICT -- Não pode deletar usuários com comentários?
);

-- RESTRIÇÃO DE MÉTODO DE PAGAMENTO ÚNICO:
-- Uma doação pode ter apenas UM método de pagamento (Bitcoin, CartaoCredito, Paypal ou MecPlat).
-- Esta restrição é garantida através de TRIGGERS que verificam antes de cada inserção se já existe
-- algum registro de pagamento nas outras tabelas para a mesma doação.
-- A função verificar_metodo_pagamento_unico() é executada em cada tabela de pagamento e impede
-- a inserção caso já exista um método de pagamento associado àquela doação.
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
  id_video_doacao BIGINT NOT NULL,
  seq_doacao INT NOT NULL,
  id_usuario INT NOT NULL,
  tx_id VARCHAR(64) NOT NULL,

  PRIMARY KEY (id_video_doacao, seq_doacao, id_usuario),

  FOREIGN KEY (id_video_doacao, seq_doacao, id_usuario) REFERENCES Doacao (
    id_video, num_seq, id_usuario
  )
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE CartaoCredito (
  id_video_doacao BIGINT NOT NULL,
  seq_doacao INT NOT NULL,
  id_usuario INT NOT NULL,
  num VARCHAR(24) NOT NULL,
  bandeira VARCHAR(32),

  PRIMARY KEY (id_video_doacao, seq_doacao, id_usuario),
  -- UNIQUE (num, bandeira): Garante que a combinação de número de cartão e bandeira seja
  -- única no sistema, prevenindo fraudes e duplicação de dados de pagamento
  UNIQUE (num, bandeira),

  FOREIGN KEY (id_video_doacao, seq_doacao, id_usuario) REFERENCES Doacao (
    id_video, num_seq, id_usuario
  )
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Paypal (
  id_video_doacao BIGINT NOT NULL,
  seq_doacao INT NOT NULL,
  id_usuario INT NOT NULL,
  id INT NOT NULL,

  PRIMARY KEY (id_video_doacao, seq_doacao, id_usuario),

  FOREIGN KEY (id_video_doacao, seq_doacao, id_usuario) REFERENCES Doacao (
    id_video, num_seq, id_usuario
  )
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE MecPlat (
  id_video_doacao BIGINT NOT NULL,
  seq_doacao INT NOT NULL,
  id_usuario INT NOT NULL,
  seq INT NOT NULL,

  PRIMARY KEY (id_video_doacao, seq_doacao, id_usuario),

  FOREIGN KEY (id_video_doacao, seq_doacao, id_usuario) REFERENCES Doacao (
    id_video, num_seq, id_usuario
  )
  ON UPDATE CASCADE ON DELETE CASCADE
);
