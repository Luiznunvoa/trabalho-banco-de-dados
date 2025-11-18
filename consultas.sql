SET SEARCH_PATH TO core;

/* 1. Identificar quais são os canais patrocinados e os valores de patrocínio pagos por empresa.
   SE UMA EMPRESA FEZ MAIS DE UM PATROCINIO PARA UM CANAL, PRECISA AGRUPAR?
   */
SELECT
  c.nome nome_canal,
  p.valor valor_patrocinio,
  e.nome nome_empresa
FROM empresa e
JOIN patrocinio p ON p.nro_empresa = e.nro
JOIN canal c ON p.id_canal = c.id
ORDER BY c.nome ASC;

/*2. Descobrir de quantos canais cada usuário é membro e a soma do valor desembolsado por
usuário por mês.
  // DEVE CONSIDERAR USUARIOS SEM INSCRIÇÃO?
  */
SELECT
  u.nick AS nome,
  COUNT(nc.id_canal) AS qnt_canais_membro,
  SUM(nc.valor) AS valor_gasto_mes
FROM
  usuario AS u
INNER JOIN inscricao AS i
  ON u.id = i.id_membro
INNER JOIN nivelcanal AS nc
  ON i.id_nivel = nc.id
GROUP BY u.nick
ORDER BY
  valor_gasto_mes DESC,
  nome ASC;

/* 3. Listar e ordenar os canais que já receberam doações e a soma dos valores recebidos em
doação.
   SE É VALOR RECEBIDO ENTÃO O STATUS_PAGAMENTO TEM QUE SER CONCLUIDO? */
SELECT
  d.id_canal,
  d.nome,
  d.qtd_doacoes,
  d.total_doacao
FROM
  vw_faturamento_doacao AS d
ORDER BY total_doacao DESC;

/* 4. Listar a soma das doações geradas pelos comentários que foram lidos por vídeo.   */

-- Vale a pena adicionar a coluna "coment_on" na view "vw_faturamento_doacao" ?
SELECT
  v.id_canal,
  v.titulo,
  COUNT(d.id_comentario) AS qtd_doacoes_lidas,
  SUM(d.valor) AS total_doacao
FROM
  doacao AS d
INNER JOIN comentario AS com
  ON d.id_comentario = com.num_seq
INNER JOIN video AS v
  ON com.id_video = v.id
WHERE com.coment_on = true AND d.status_pagamento = 'CONCLUIDO'
GROUP BY v.id
ORDER BY total_doacao DESC;

/* 5. Listar e ordenar os k canais que mais recebem patrocínio e os valores recebidos.
   usar o k = 5 por enquanto*/

SELECT
  nome,
  qtd_patrocinios,
  total_patrocinio
FROM vw_faturamento_patrocinio
ORDER BY qtd_patrocinios DESC -- Ordena pela QUANTIDADE, como na sua query
LIMIT 5; /* usei esse comando invés de Limit para evitar que empates fiquei fora da lista */

/* 6. Listar e ordenar os k canais que mais recebem aportes de membros e os valores recebidos.
   k=5 */
SELECT
  nome,
  qtd_inscricoes,
  total_inscricao
FROM vw_faturamento_inscricao
ORDER BY total_inscricao DESC
LIMIT 5;

/* 7. Listar e ordenar os k canais que mais receberam doações considerando todos os vídeos.
  k = 5  */

SELECT
  nome,
  qtd_doacoes,
  total_doacao
FROM
  vw_faturamento_doacao
ORDER BY qtd_doacoes DESC
LIMIT 5;

/* 8. Listar os k canais que mais faturam (Patrocínio + Membros + Doações). k=5 */
    /* uso de left join para pegar os casos que nao tem */
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
LEFT JOIN vw_faturamento_patrocinio pat ON c.id = pat.id_canal
LEFT JOIN vw_faturamento_inscricao ins ON c.id = ins.id_canal
LEFT JOIN vw_faturamento_doacao doa ON c.id = doa.id_canal
ORDER BY faturamento_total DESC
LIMIT 5;
