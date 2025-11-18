-- Exclui e recria o esquema para garantir um ambiente limpo
-- DROP SCHEMA IF EXISTS teste4 CASCADE;
CREATE SCHEMA core;
SET SEARCH_PATH TO core;

-- -- Tabelas -- 


CREATE TYPE TIPO_CANAL AS ENUM ('privado', 'publico', 'misto');

CREATE TABLE empresa (
  nro INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  nome_fantasia VARCHAR(255)
);

CREATE TABLE conversao (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  moeda VARCHAR(100) NOT NULL,
  fator_conver NUMERIC(18, 8) NOT NULL
);

CREATE TABLE pais (
  ddi INTEGER NOT NULL PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  id_moeda INTEGER NOT NULL
  REFERENCES conversao (id)
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE plataforma (
  nro INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  data_fund DATE NOT NULL,
  empresa_fund INTEGER NOT NULL
  REFERENCES empresa (nro)
  ON UPDATE CASCADE ON DELETE CASCADE,
  empresa_respo INTEGER NOT NULL
  REFERENCES empresa (nro)
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE usuario (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nick VARCHAR(100) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  data_nasc DATE NOT NULL,
  telefone VARCHAR(20) NOT NULL,
  pais_residencia INTEGER REFERENCES pais (ddi)
  ON UPDATE CASCADE ON DELETE SET NULL,
  end_postal VARCHAR(50)
);

CREATE TABLE plataformausuario (
  nro_plataforma INTEGER NOT NULL
  REFERENCES plataforma (nro)
  ON UPDATE CASCADE ON DELETE CASCADE,
  id_usuario INTEGER NOT NULL
  REFERENCES usuario (id)
  ON UPDATE CASCADE ON DELETE CASCADE,
  nro_usuario INTEGER,
  PRIMARY KEY (nro_plataforma, id_usuario),
  UNIQUE (nro_plataforma, nro_usuario)
);

CREATE TABLE streamerpais (
  id_usuario INTEGER NOT NULL
  REFERENCES usuario (id)
  ON UPDATE CASCADE ON DELETE CASCADE,
  ddi_pais INTEGER NOT NULL
  REFERENCES pais (ddi)
  ON UPDATE CASCADE ON DELETE CASCADE,
  nro_passaporte VARCHAR(50) UNIQUE,
  PRIMARY KEY (id_usuario, ddi_pais)
);

CREATE TABLE empresapais (
  nro_empresa INTEGER NOT NULL
  REFERENCES empresa (nro)
  ON UPDATE CASCADE ON DELETE CASCADE,
  ddi_pais INTEGER NOT NULL
  REFERENCES pais (ddi)
  ON UPDATE CASCADE ON DELETE CASCADE,
  id_nacional VARCHAR(100),
  PRIMARY KEY (nro_empresa, ddi_pais),
  UNIQUE (ddi_pais, id_nacional)
);

CREATE TABLE Canal (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_streamer INT NOT NULL,
  nro_plataforma INT NOT NULL,
  nome VARCHAR(255) NOT NULL,
  tipo TIPO_CANAL NOT NULL,
  qtd_visualizacoes INT NOT NULL,
  data DATE NOT NULL,
  descricao VARCHAR(255),

  UNIQUE (nome, nro_plataforma),
  FOREIGN KEY (nro_plataforma) REFERENCES plataforma (nro)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_streamer) REFERENCES usuario (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

-- Um canal pode ser patrocinado pela mesma empresa 2 vezes
-- 
CREATE TABLE Patrocinio (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nro_empresa INT NOT NULL,
  id_canal INT NOT NULL,
  valor DECIMAL(10, 2),
  -- dataInicio TIMESTAMP NOT NULL,
  -- dataFim TIMESTAMP,

  UNIQUE (nro_empresa, id_canal),

  FOREIGN KEY (nro_empresa) REFERENCES empresa (nro)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_canal) REFERENCES Canal (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

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
  FOREIGN KEY (id_membro) REFERENCES usuario (id)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_nivel) REFERENCES NivelCanal (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

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

  FOREIGN KEY (id_streamer) REFERENCES usuario (id)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_video) REFERENCES Video (id)
  ON DELETE CASCADE ON UPDATE CASCADE
);

-- 🔹 Apenas uma tabela Comentario deve existir (havia duas)
CREATE TABLE Comentario (
  id_video BIGINT NOT NULL,
  num_seq BIGINT GENERATED ALWAYS AS IDENTITY UNIQUE,
  id_usuario INT,
  texto TEXT NOT NULL,
  dataH TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  coment_on BOOLEAN NOT NULL DEFAULT TRUE,

  PRIMARY KEY (id_video, num_seq),

  FOREIGN KEY (id_video) REFERENCES Video (id)
  ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_usuario) REFERENCES usuario (id)
  ON DELETE SET NULL ON UPDATE CASCADE
);

-- Corrigido nome do tipo (estava 'StatusPagemento')
CREATE TYPE StatusPagamento AS ENUM ('PENDENTE', 'CONCLUIDO', 'FALHOU');

CREATE TABLE Doacao (
  id_comentario BIGINT PRIMARY KEY,
  valor DECIMAL(10, 2) NOT NULL,
  status_pagamento STATUSPAGAMENTO NOT NULL DEFAULT 'PENDENTE',

  FOREIGN KEY (id_comentario) REFERENCES Comentario (num_seq)
  ON DELETE CASCADE
);

CREATE TABLE Bitcoin (
  id_doacao BIGINT,
  tx_id VARCHAR(64),

  PRIMARY KEY (id_doacao, tx_id),

  FOREIGN KEY (id_doacao) REFERENCES Doacao (id_comentario)
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE CartaoCredito (
  id_doacao BIGINT,
  num VARCHAR(24),
  bandeira VARCHAR(32),

  PRIMARY KEY (id_doacao, num),
  UNIQUE (num, bandeira),

  FOREIGN KEY (id_doacao) REFERENCES Doacao (id_comentario)
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Paypal (
  id_doacao BIGINT,
  id INT,

  PRIMARY KEY (id_doacao, id),

  FOREIGN KEY (id_doacao) REFERENCES Doacao (id_comentario)
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE MecPlat (
  id_doacao BIGINT,
  seq INT,

  PRIMARY KEY (id_doacao, seq),

  FOREIGN KEY (id_doacao) REFERENCES Doacao (id_comentario)
  ON UPDATE CASCADE ON DELETE CASCADE
);

-- -- Índices -- 


-- -- Funções e Triggers --- 

--5. Listar e ordenar os k canais que mais recebem patrocínio e os valores recebidos.

CREATE OR REPLACE FUNCTION MAIORPATROCINIO(k INT)
RETURNS TABLE (
  id INT,
  nome VARCHAR(255),
  nro_plataforma INT,
  total_recebido FLOAT
)
AS $$
	select c.id, c.nome, c.nro_plataforma, sum(p.valor) as total_recebido
	from canal c join patrocinio p on c.id = p.id_canal
	group by c.id, c.nome, c.nro_plataforma
	order by sum(p.valor) desc limit k;
$$ LANGUAGE sql;


--6. Listar e ordenar os k canais que mais recebem aportes de membros e os valores recebidos.


CREATE OR REPLACE FUNCTION MAIORAPOIOMEMBROS(k INT)
RETURNS TABLE (
  id INT,
  nome VARCHAR(255),
  nro_plataforma INT,
  total_aporte FLOAT
)
AS $$
	select c.id, c.nome, c.nro_plataforma, sum(nc.valor) as total_aporte	
	from canal c join NivelCanal nc on c.id = nc.id_canal
		join Inscricao i on nc.id = i.id_nivel
	group by c.id, c.nome, c.nro_plataforma
	order by sum(nc.valor) desc limit k;
$$ LANGUAGE sql;


--7. Listar e ordenar os k canais que mais receberam doações considerando todos os vídeos.


CREATE OR REPLACE FUNCTION MAISDOACOES(k INT)
RETURNS TABLE (
  id INT,
  nome VARCHAR(255),
  nro_plataforma INT,
  total_doacoes FLOAT
)
AS $$
	select c.id, c.nome, c.nro_plataforma, sum(d.valor) as total_doacoes	
	from Doacao d join Comentario co on d.id_comentario = co.num_seq and d.status_pagamento = 'CONCLUIDO'
	join Video v on co.id_video = v.id
	join Canal c on v.id_canal = c.id
	group by c.id, c.nome, c.nro_plataforma
	order by sum(d.valor) desc limit k;
$$ LANGUAGE sql;


--8. Listar os k canais que mais faturam considerando as 
-- três fontes de receita: patrocínio, membros inscritos e doações.

-- FIX: Essa função

-- CREATE OR REPLACE FUNCTION MAIORFATURAMENTO(k INT)
-- RETURNS TABLE (
--   id INT,
--   nome VARCHAR(255),
--   nro_plataforma INT,
--   total_faturamento FLOAT
-- )
-- AS $$
-- 	with c1 as(
-- 			select c.id, c.nome, c.nro_plataforma, sum(p.valor) as total_valor_patrocinio
-- 			from canal c join patrocinio p on c.id = p.id_canal
-- 			group by c.id, c.nome, c.nro_plataforma
-- 	), c2 as (
-- 		select c.id, c.nome, c.nro_plataforma, sum(nc.valor) as total_aporte	
-- 		from Canal c join NivelCanal nc on c.id = nc.id_canal
-- 			join Inscricao i on nc.id = i.id_nivel
-- 		group by c.id, c.nome, c.nro_plataforma
-- 	), c3 as (
-- 		select c.id, c.nome, c.nro_plataforma, sum(d.valor) as total_doacoes	
-- 		from Doacao d join Comentario co on d.id_comentario = co.num_seq and d.status_pagamento = 'CONCLUIDO'
-- 		join Video v on co.id_video = v.id
-- 		join Canal c on v.id_canal = c.id
-- 		group by c.id, c.nome, c.nro_plataforma
-- 	)
-- 	select c.id, c.nome, c.nro_plataforma, (coalesce(total_valor_patrocinio,0)+coalesce(total_aporte,0)+coalesce(total_doacoes,0)) as total_faturamento
-- 	from Canal c left join c1 on c.id = c1.id
-- 		left join c2 on c.id = c2.id
-- 		left join c3 on c.id = c3.id
-- 	group by c.id, c.nome, c.nro_plataforma
-- 	order by total_faturamento desc limit k;
-- $$ LANGUAGE sql;

-- -- Views -- --- 

-- Faz sentido ser view materializada?
-- Se sim, faz sentido implementar um TRIGGER?
CREATE VIEW vw_faturamento_doacao AS
SELECT
  c.id AS id_canal,
  c.nome,
  COUNT(d.id_comentario) AS qtd_doacoes,
  SUM(d.valor) AS total_doacao
FROM
  canal AS c
INNER JOIN video AS v
  ON c.id = v.id_canal
INNER JOIN comentario AS com
  ON v.id = com.id_video
INNER JOIN doacao AS d
  ON
    com.num_seq = d.id_comentario
    AND d.status_pagamento = 'CONCLUIDO'
GROUP BY c.id;

/* V2 TOTAL DE PATROCINIOS
       usado na Q5 e Q8 */
CREATE VIEW vw_faturamento_patrocinio AS
SELECT
  c.id AS id_canal,
  c.nome,
  COUNT(p.id) AS qtd_patrocinios,
  SUM(p.valor) AS total_patrocinio
FROM
  canal c
JOIN patrocinio p ON c.id = p.id_canal
GROUP BY c.id;

/* V2 TOTAL DE MEMBROS
       usado na Q6 e Q8 */
CREATE VIEW vw_faturamento_inscricao AS
SELECT
  c.id AS id_canal,
  c.nome,
  COUNT(i.id_membro) AS qtd_inscricoes,
  SUM(nc.valor) AS total_inscricao
FROM
  canal c
JOIN nivelcanal nc ON c.id = nc.id_canal
JOIN inscricao i ON nc.id = i.id_nivel
GROUP BY c.id;


