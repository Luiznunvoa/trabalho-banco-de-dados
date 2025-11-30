SET SEARCH_PATH TO core;

/* 1. Identificar quais são os canais patrocinados e os valores de patrocínio pagos por empresa. */

-- 1. Versão para buscar TUDO (sem parâmetros)
CREATE OR REPLACE FUNCTION CANAISPATROCINADOSEMPRESA()
RETURNS TABLE (
	nome_canal varchar,
	valor_patrocinio float,
	nome_empresa varchar
) AS $$
    SELECT
      	c.nome,
		p.valor,
		e.nome
    FROM empresa e
        JOIN patrocinio p ON p.nro_empresa = e.nro
        JOIN canal c ON p.id_canal = c.id
        JOIN usuario u ON c.id_streamer = u.id
    WHERE u.data_exclusao IS NULL
    ORDER BY c.nome ASC;

$$ LANGUAGE sql;



-- 2. Versão para buscar por ID (recebe INT)
CREATE OR REPLACE FUNCTION CANAISPATROCINADOSEMPRESA(p_id int)
RETURNS TABLE (
	nome_canal varchar,
	valor_patrocinio float,
	nome_empresa varchar) 
AS $$
    SELECT
      	c.nome,
		p.valor,
		e.nome
    FROM empresa e
        JOIN patrocinio p ON p.nro_empresa = e.nro
        JOIN canal c ON p.id_canal = c.id
        JOIN usuario u ON c.id_streamer = u.id
    WHERE e.nro = p_id
      AND u.data_exclusao IS NULL
    ORDER BY c.nome ASC;

$$ LANGUAGE sql;



-- 3. Versão para buscar por NOME (recebe VARCHAR)
CREATE OR REPLACE FUNCTION CANAISPATROCINADOSEMPRESA(p_nome varchar)
RETURNS TABLE (
	nome_canal varchar,
	valor_patrocinio float,
	nome_empresa varchar) 
AS $$
    SELECT
      c.nome, p.valor, e.nome
    FROM empresa e
        JOIN patrocinio p ON p.nro_empresa = e.nro
        JOIN canal c ON p.id_canal = c.id
        JOIN usuario u ON c.id_streamer = u.id
    WHERE e.nome ILIKE p_nome
      AND u.data_exclusao IS NULL
    ORDER BY c.nome ASC;
$$ LANGUAGE sql;



/* 2. Descobrir de quantos canais cada usuário é membro e a soma do valor desembolsado por
usuário por mês. */


-- 1. Versão para buscar TUDO (sem parâmetros)
CREATE OR REPLACE FUNCTION GASTOMEMBRESIA()
RETURNS TABLE (
  nick varchar(100),
  qnt_canais_membro int,
  valor_gasto_mes float
)
AS $$
    SELECT
        u.nick AS nome,
        COUNT(nc.id_canal) AS qnt_canais_membro,
        SUM(nc.valor) AS valor_gasto_mes
    FROM
        usuario AS u
        INNER JOIN inscricao AS i ON u.id = i.id_membro
        INNER JOIN nivelcanal AS nc ON i.id_nivel = nc.id
        INNER JOIN canal AS c ON nc.id_canal = c.id
        INNER JOIN usuario AS u_streamer ON c.id_streamer = u_streamer.id
    WHERE u.data_exclusao IS NULL
      AND u_streamer.data_exclusao IS NULL
    GROUP BY u.nick
    ORDER BY
      valor_gasto_mes DESC,
      nome ASC;
$$ LANGUAGE sql;



-- 2. Versão para buscar por ID (recebe INT)
CREATE OR REPLACE FUNCTION GASTOMEMBRESIA(p_id_user int)
RETURNS TABLE (
  nick varchar(100),
  qnt_canais_membro int,
  valor_gasto_mes float
)
AS $$
    SELECT
        u.nick AS nome,
        COUNT(nc.id_canal) AS qnt_canais_membro,
        SUM(nc.valor) AS valor_gasto_mes
    FROM
        usuario AS u
        INNER JOIN inscricao AS i ON u.id = i.id_membro
        INNER JOIN nivelcanal AS nc ON i.id_nivel = nc.id
        INNER JOIN canal AS c ON nc.id_canal = c.id
        INNER JOIN usuario AS u_streamer ON c.id_streamer = u_streamer.id
    WHERE u.id = p_id_user
      AND u.data_exclusao IS NULL
      AND u_streamer.data_exclusao IS NULL
    GROUP BY u.nick
    ORDER BY
      valor_gasto_mes DESC,
      nome ASC;
$$ LANGUAGE sql;



-- 3. Versão para buscar por NOME (recebe VARCHAR)
CREATE OR REPLACE FUNCTION GASTOMEMBRESIA(p_nick varchar)
RETURNS TABLE (
  nick varchar(100),
  qnt_canais_membro int,
  valor_gasto_mes float
)
AS $$
    SELECT
        u.nick AS nome,
        COUNT(nc.id_canal) AS qnt_canais_membro,
        SUM(nc.valor) AS valor_gasto_mes
    FROM
        usuario AS u
        INNER JOIN inscricao AS i ON u.id = i.id_membro
        INNER JOIN nivelcanal AS nc ON i.id_nivel = nc.id
        INNER JOIN canal AS c ON nc.id_canal = c.id
        INNER JOIN usuario AS u_streamer ON c.id_streamer = u_streamer.id
    WHERE u.nick ILIKE p_nick -- ILIKE permite buscar 'User' ou 'user'
      AND u.data_exclusao IS NULL
      AND u_streamer.data_exclusao IS NULL
    GROUP BY u.nick
    ORDER BY
      valor_gasto_mes DESC,
      nome ASC;
$$ LANGUAGE sql;



/* 3. Listar e ordenar os canais que já receberam doações e a soma dos valores recebidos em doação. */



-- 1. Versão para buscar TUDO (sem parâmetros)
CREATE OR REPLACE FUNCTION DOACOESCANAL()
RETURNS TABLE (
  nome_canal varchar(255),
  qtd_doacoes int,
  total_doacao float
)
AS $$
    SELECT
      c.nome,
      d.qtd_doacoes,
      d.total_doacao
    FROM
      vw_faturamento_doacao as d
      JOIN Canal c ON d.id_canal = c.id
      JOIN Usuario u ON c.id_streamer = u.id
    WHERE u.data_exclusao IS NULL
    ORDER BY total_doacao DESC;
$$ LANGUAGE sql;



-- 2. Versão para buscar por ID (recebe INT)
CREATE OR REPLACE FUNCTION DOACOESCANAL(p_id_canal int)
RETURNS TABLE (
  nome_canal varchar(255),
  qtd_doacoes int,
  total_doacao float
)
AS $$
    SELECT
      c.nome,
      d.qtd_doacoes,
      d.total_doacao
    FROM
      vw_faturamento_doacao as d
      JOIN Canal c ON d.id_canal = c.id
      JOIN Usuario u ON c.id_streamer = u.id
    WHERE d.id_canal = p_id_canal
      AND u.data_exclusao IS NULL
    ORDER BY total_doacao DESC;
$$ LANGUAGE sql;



-- 3. Versão para buscar por NOME (recebe VARCHAR)
CREATE OR REPLACE FUNCTION DOACOESCANAL(p_nome_canal varchar)
RETURNS TABLE (
  nome_canal varchar(255),
  qtd_doacoes int,
  total_doacao float
)
AS $$
    SELECT
      c.nome,
      d.qtd_doacoes,
      d.total_doacao
    FROM
      vw_faturamento_doacao as d
      JOIN Canal c ON d.id_canal = c.id
      JOIN Usuario u ON c.id_streamer = u.id
    WHERE c.nome ILIKE p_nome_canal -- Busca Flexível (Ex: 'canal do joao')
      AND u.data_exclusao IS NULL
    ORDER BY total_doacao DESC;
$$ LANGUAGE sql;



/* 4. Listar a soma das doações geradas pelos comentários que foram lidos por vídeo. */



-- 1. Versão para buscar TUDO (sem parâmetros)
CREATE OR REPLACE FUNCTION DOACOESCOMENTARIOSLIDOS()
RETURNS TABLE (
  titulo_video varchar(255),
  qtd_doacoes_lidas int,
  total_doacao float
)
AS $$
    SELECT
      v.titulo,
      COUNT(*) AS qtd_doacoes_lidas,
      SUM(d.valor) AS total_doacao
    FROM
      doacao AS d
    INNER JOIN comentario AS com
      ON d.id_video = com.id_video AND d.num_seq = com.num_seq
    INNER JOIN video AS v ON com.id_video = v.id
    INNER JOIN usuario AS u_donator ON d.id_usuario = u_donator.id
    INNER JOIN canal AS c ON v.id_canal = c.id
    INNER JOIN usuario AS u_streamer ON c.id_streamer = u_streamer.id
    WHERE com.coment_on = true 
      AND d.status_pagamento = 'CONCLUIDO'
      AND u_donator.data_exclusao IS NULL
      AND u_streamer.data_exclusao IS NULL
    GROUP BY v.id, v.id_canal, v.titulo
    ORDER BY total_doacao DESC;
$$ LANGUAGE sql;



-- 2. Versão para buscar por ID (recebe INT)
CREATE OR REPLACE FUNCTION DOACOESCOMENTARIOSLIDOS(p_id_video int)
RETURNS TABLE (
  titulo_video varchar(255),
  qtd_doacoes_lidas int,
  total_doacao float
)
AS $$
    SELECT
      v.titulo,
      COUNT(*) AS qtd_doacoes_lidas,
      SUM(d.valor) AS total_doacao
    FROM
      doacao AS d
    INNER JOIN comentario AS com
      ON d.id_video = com.id_video AND d.num_seq = com.num_seq
    INNER JOIN video AS v ON com.id_video = v.id
    INNER JOIN usuario AS u_donator ON d.id_usuario = u_donator.id
    INNER JOIN canal AS c ON v.id_canal = c.id
    INNER JOIN usuario AS u_streamer ON c.id_streamer = u_streamer.id
    WHERE v.id = p_id_video -- Filtro direto no ID do vídeo
      AND com.coment_on = true 
      AND d.status_pagamento = 'CONCLUIDO'
      AND u_donator.data_exclusao IS NULL
      AND u_streamer.data_exclusao IS NULL
    GROUP BY v.id, v.id_canal, v.titulo
    ORDER BY total_doacao DESC;
$$ LANGUAGE sql;



-- 3. Versão para buscar por NOME (recebe VARCHAR)
CREATE OR REPLACE FUNCTION DOACOESCOMENTARIOSLIDOS(p_titulo_video varchar)
RETURNS TABLE (
  titulo_video varchar(255),
  qtd_doacoes_lidas int,
  total_doacao float
)
AS $$
    SELECT
      v.titulo,
      COUNT(*) AS qtd_doacoes_lidas,
      SUM(d.valor) AS total_doacao
    FROM
      doacao AS d
    INNER JOIN comentario AS com
      ON d.id_video = com.id_video AND d.num_seq = com.num_seq
    INNER JOIN video AS v ON com.id_video = v.id
    INNER JOIN usuario AS u_donator ON d.id_usuario = u_donator.id
    INNER JOIN canal AS c ON v.id_canal = c.id
    INNER JOIN usuario AS u_streamer ON c.id_streamer = u_streamer.id
    WHERE v.titulo ILIKE p_titulo_video -- Busca por título (Ex: 'Gameplay%')
      AND com.coment_on = true 
      AND d.status_pagamento = 'CONCLUIDO'
      AND u_donator.data_exclusao IS NULL
      AND u_streamer.data_exclusao IS NULL
    GROUP BY v.id, v.id_canal, v.titulo
    ORDER BY total_doacao DESC;
$$ LANGUAGE sql;



/* 5. Listar e ordenar os k canais que mais recebem patrocínio e os valores recebidos. */

CREATE OR REPLACE FUNCTION MAIORPATROCINIO(k int DEFAULT NULL)
RETURNS TABLE (
  nome varchar(255),
  qtd_patrocinios int,
  total_patrocinio float
)
AS $$
SELECT
  c.nome,
  p.qtd_patrocinios,
  p.total_patrocinio
FROM vw_faturamento_patrocinio p
JOIN Canal c ON p.id_canal = c.id
JOIN Usuario u ON c.id_streamer = u.id
WHERE u.data_exclusao IS NULL
ORDER BY qtd_patrocinios DESC, total_patrocinio DESC
LIMIT COALESCE(k, NULL);
$$ LANGUAGE sql;


/* 6. Listar e ordenar os k canais que mais recebem aportes de membros e os valores recebidos. */

CREATE OR REPLACE FUNCTION MAIORAPOIOMEMBROS(k int DEFAULT NULL)
RETURNS TABLE (
  nome varchar(255),
  qtd_inscricoes int,
  total_inscricao float
)
AS $$
SELECT
	  c.nome,
	  i.qtd_inscricoes,
	  i.total_inscricao
	FROM vw_faturamento_inscricao i
	JOIN Canal c ON i.id_canal = c.id
	JOIN Usuario u ON c.id_streamer = u.id
	WHERE u.data_exclusao IS NULL
	ORDER BY total_inscricao DESC
	LIMIT COALESCE(k, NULL);
$$ LANGUAGE sql;


/* 7. Listar e ordenar os k canais que mais receberam doações considerando todos os vídeos. */

CREATE OR REPLACE FUNCTION MAISDOACOES(k int DEFAULT NULL)
RETURNS TABLE (
  nome varchar(255),
  qtd_doacoes int,
  total_doacao float
)
AS $$
	SELECT
	  c.nome,
	  d.qtd_doacoes,
	  d.total_doacao
	FROM
	  vw_faturamento_doacao d
	  JOIN Canal c ON d.id_canal = c.id
	  JOIN Usuario u ON c.id_streamer = u.id
	WHERE u.data_exclusao IS NULL
	ORDER BY qtd_doacoes DESC, total_doacao DESC
	LIMIT COALESCE(k, NULL);
$$ LANGUAGE sql;


/* 8. Listar os k canais que mais faturam considerando as três fontes de receita. */

CREATE OR REPLACE FUNCTION MAIORFATURAMENTO(k int DEFAULT NULL)
RETURNS TABLE (
  nome varchar(255),
  f_patrocinio float,
  f_inscricao float,
  f_doacao float,
  faturamento_total float
)
AS $$
	SELECT
	  c.nome,
	  COALESCE(pat.total_patrocinio, 0) AS f_patrocinio,
	  COALESCE(ins.total_inscricao, 0) AS f_inscricao,
	  COALESCE(doa.total_doacao, 0) AS f_doacao,
	  (
	    COALESCE(pat.total_patrocinio, 0)
	    + COALESCE(ins.total_inscricao, 0)
	    + COALESCE(doa.total_doacao, 0)
	  ) AS faturamento_total
	FROM
	  canal c
	JOIN usuario u ON c.id_streamer = u.id
	LEFT JOIN vw_faturamento_patrocinio pat ON c.id = pat.id_canal
	LEFT JOIN vw_faturamento_inscricao ins ON c.id = ins.id_canal
	LEFT JOIN vw_faturamento_doacao doa ON c.id = doa.id_canal
	WHERE u.data_exclusao IS NULL
	ORDER BY faturamento_total DESC
	LIMIT COALESCE(k, NULL);
$$ LANGUAGE sql;
