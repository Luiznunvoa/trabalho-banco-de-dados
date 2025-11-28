SET SEARCH_PATH TO core;

CREATE OR REPLACE VIEW vw_faturamento_doacao AS
SELECT
  v.id_canal,
  COUNT(d.num_seq) AS qtd_doacoes,
  SUM(d.valor) AS total_doacao
FROM
  Doacao AS d
INNER JOIN Video AS v ON d.id_video = v.id
INNER JOIN Usuario AS u_donator ON d.id_usuario = u_donator.id
INNER JOIN Canal AS c ON v.id_canal = c.id
INNER JOIN Usuario AS u_streamer ON c.id_streamer = u_streamer.id
WHERE
  d.status_pagamento = 'CONCLUIDO'
  AND u_donator.data_exclusao IS NULL
  AND u_streamer.data_exclusao IS NULL
GROUP BY
  v.id_canal;


CREATE OR REPLACE VIEW vw_faturamento_patrocinio AS
SELECT
  p.id_canal,
  COUNT(p.nro_empresa) AS qtd_patrocinios,
  SUM(p.valor) AS total_patrocinio
FROM
  patrocinio AS p
INNER JOIN Canal AS c ON p.id_canal = c.id
INNER JOIN Usuario AS u ON c.id_streamer = u.id
WHERE
  u.data_exclusao IS NULL
GROUP BY
  p.id_canal;


CREATE OR REPLACE VIEW vw_faturamento_inscricao AS
SELECT
  nc.id_canal,
  COUNT(i.id_membro) AS qtd_inscricoes,
  SUM(nc.valor) AS total_inscricao
FROM
  nivelcanal AS nc
INNER JOIN inscricao AS i ON nc.id = i.id_nivel
INNER JOIN Usuario AS u_membro ON i.id_membro = u_membro.id
INNER JOIN Canal AS c ON nc.id_canal = c.id
INNER JOIN Usuario AS u_streamer ON c.id_streamer = u_streamer.id
WHERE
  u_membro.data_exclusao IS NULL AND u_streamer.data_exclusao IS NULL
GROUP BY
  nc.id_canal;


-- o intuito principal da aplicação é a visualização do faturamento dos canais e o foco 
-- das consultas a serem respondidas
-- portanto, decidimos criar  uma view que abrange todas formas de faturamento de um canal

-- achei melhor trabalhar com blocos separados para cada fonte de faturamento para evitar erros
CREATE MATERIALIZED VIEW IF NOT EXISTS vw_faturamento_total AS
SELECT
  c.id AS id_canal,
  c.nome,
  --- 1. Patrocinio ---
  COALESCE(p.qtd_patrocinios, 0) AS qtd_patrocinio,
  COALESCE(p.total_patrocinio, 0) AS valor_patrocinio,

  --- 2. Inscrição ---
  COALESCE(i.qtd_inscricoes, 0) AS qtd_inscricao,
  COALESCE(i.total_inscricao, 0) AS valor_inscricao,

  --- 3. Doacao ---
  COALESCE(d.qtd_doacoes, 0) AS qtd_doacao,
  COALESCE(d.total_doacao, 0) AS valor_doacao,

  ---  TOTAL ---
  (
    COALESCE(p.total_patrocinio, 0)
    + COALESCE(i.total_inscricao, 0)
    + COALESCE(d.total_doacao, 0)
  ) AS faturamento_total
FROM
  canal AS c
-- precisa de LEFT JOIN para garantir que vai pegar canais sem aquela fonte de faturamento
-- exemplo canal com doacao e inscrição sem patrocinio
INNER JOIN Usuario AS u ON c.id_streamer = u.id
LEFT JOIN vw_faturamento_patrocinio AS p ON c.id = p.id_canal
LEFT JOIN vw_faturamento_inscricao AS i ON c.id = i.id_canal
LEFT JOIN vw_faturamento_doacao AS d ON c.id = d.id_canal
WHERE
  u.data_exclusao IS NULL
WITH DATA;

-- O formato é padrão CRON: minuto, hora, dia, mes, dia_semana
SELECT
  cron.schedule(
    'refresh_faturamento_5min', -- Nome da tarefa (opcional)
    '*/5 * * * *',
    'REFRESH MATERIALIZED VIEW CONCURRENTLY core.vw_faturamento_total'
  );

-- verificação do cron
-- SELECT * FROM cron.job;
