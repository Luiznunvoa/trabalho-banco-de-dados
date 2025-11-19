SET SEARCH_PATH TO core;

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
  canal AS c
INNER JOIN patrocinio AS p ON c.id = p.id_canal
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
  canal AS c
INNER JOIN nivelcanal AS nc ON c.id = nc.id_canal
INNER JOIN inscricao AS i ON nc.id = i.id_nivel
GROUP BY c.id;
