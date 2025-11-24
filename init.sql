-- Cria o esquema se não existir
CREATE SCHEMA IF NOT EXISTS core;
SET SEARCH_PATH TO core;

-- -- Tabelas -- 


CREATE TYPE TIPO_CANAL AS ENUM ('privado', 'publico', 'misto');

CREATE TYPE STATUSPAGAMENTO AS ENUM ('PENDENTE', 'CONCLUIDO', 'FALHOU');

CREATE TABLE Empresa ( -- OK
  nro INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  nome_fantasia VARCHAR(255)
);

-- trocamos os nomes dos atributos para facilitar visualização, não alteramos a lógica
CREATE TABLE Conversao ( -- OK
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  moeda VARCHAR(100) NOT NULL,
  fator_conver NUMERIC(18, 8) NOT NULL
);

CREATE TABLE Pais ( -- OK
  ddi INTEGER NOT NULL PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  id_moeda INTEGER NOT NULL,

  FOREIGN KEY (id_moeda) REFERENCES Conversao (id)
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Plataforma ( -- OK
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

-- Criamos ID artificial pois nick é varchar, o que dificulta a integração com outras tabelas e
-- é menos eficiente de trabalhar
CREATE TABLE Usuario ( -- OK
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nick VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  data_nasc DATE NOT NULL,
  telefone VARCHAR(20) NOT NULL,
  pais_residencia INTEGER,
  end_postal VARCHAR(50),

  UNIQUE (nick),
  UNIQUE (email),

  FOREIGN KEY (pais_residencia) REFERENCES Pais (ddi)
  ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE PlataformaUsuario ( -- OK
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

CREATE TABLE StreamerPais ( -- OK
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

CREATE TABLE EmpresaPais ( -- OK
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

-- Criamos ID artificial pois "nome" é varchar, que é menos eficiente de usar em buscas
-- e CANAL é  referenciado em outras tabelas e achamos melhor simplificar a integração
-- o INTEGER é suficiente para acomodar o número de canais existentes em múltiplas plataformas visto que
-- o limite do int é 2.147 milhões e o youtube possui ~113.9 milhões
CREATE TABLE Canal ( -- OK
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

CREATE TABLE Patrocinio ( -- OK
  nro_empresa INT NOT NULL,
  id_canal INT NOT NULL,
  valor DECIMAL(10, 2),

  PRIMARY KEY (nro_empresa, id_canal),

  FOREIGN KEY (nro_empresa) REFERENCES Empresa (nro)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_canal) REFERENCES Canal (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

-- Criamos ID artificial pois "nível" é varchar, que é menos eficiente de usar em buscas
-- Decidimos que apenas o id na chave primária seria o suficiente para comportar todos os níveis
-- caso queira um grau de segurança maior a um prazo longo, poderia ser um BIGINT
CREATE TABLE NivelCanal ( -- OK
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

-- Criamos ID artificial pois "titulo" é varchar e "datah" é DATE, que seria bastante ineficiente para trabalhar
-- Resolvemos criar um id único sendo BIGINT pois, uma chave primária composta [id_canal,id_video] ocupa 8 bytes, o mesmo tamanho do BIGINT
-- porém a chave composta única é melhor de visualizar e integrar com outras tabelas
CREATE TABLE Video ( -- OK
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

CREATE TABLE Participa ( -- OK
  id_video BIGINT,
  id_streamer INT,

  PRIMARY KEY (id_video, id_streamer),

  FOREIGN KEY (id_streamer) REFERENCES Usuario (id)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_video) REFERENCES Video (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Comentario ( -- OK
  id_video BIGINT NOT NULL,
  num_seq INT,
  id_usuario INT,
  texto TEXT NOT NULL,
  dataH TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  coment_on BOOLEAN NOT NULL DEFAULT FALSE,

  PRIMARY KEY (id_video, num_seq, id_usuario),
  UNIQUE (id_video, num_seq),

  FOREIGN KEY (id_video) REFERENCES Video (id)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_usuario) REFERENCES Usuario (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Doacao (
  id_video BIGINT NOT NULL,
  num_seq INT NOT NULL,
  valor DECIMAL(10, 2) NOT NULL,
  status_pagamento STATUSPAGAMENTO NOT NULL DEFAULT 'PENDENTE',

  PRIMARY KEY (id_video, num_seq),

  FOREIGN KEY (id_video, num_seq) REFERENCES Comentario (id_video, num_seq)
  ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Bitcoin (
  id_video_doacao BIGINT,
  seq_doacao INT,
  tx_id VARCHAR(64),

  PRIMARY KEY (id_video_doacao, seq_doacao, tx_id),

  FOREIGN KEY (id_video_doacao, seq_doacao) REFERENCES Doacao (id_video, num_seq)
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE CartaoCredito (
  id_video_doacao BIGINT,
  seq_doacao INT,
  num VARCHAR(24),
  bandeira VARCHAR(32),

  PRIMARY KEY (id_video_doacao, seq_doacao, num),
  UNIQUE (num, bandeira),

  FOREIGN KEY (id_video_doacao, seq_doacao) REFERENCES Doacao (id_video, num_seq)
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Paypal (
  id_video_doacao BIGINT,
  seq_doacao INT,
  id INT,

  PRIMARY KEY (id_video_doacao, seq_doacao, id),

  FOREIGN KEY (id_video_doacao, seq_doacao) REFERENCES Doacao (id_video, num_seq)
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE MecPlat (
  id_video_doacao BIGINT,
  seq_doacao INT,
  seq INT,

  PRIMARY KEY (id_video_doacao, seq_doacao, seq),

  FOREIGN KEY (id_video_doacao, seq_doacao) REFERENCES Doacao (id_video, num_seq)
  ON UPDATE CASCADE ON DELETE CASCADE
);
