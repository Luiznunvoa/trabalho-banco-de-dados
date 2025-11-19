
/* 1. Identificar quais são os canais patrocinados e os valores de patrocínio pagos por empresa.
   SE UMA EMPRESA FEZ MAIS DE UM PATROCINIO PARA UM CANAL, PRECISA AGRUPAR?
   */



create or replace function canaisPatrocinadosEmpresa(id_emp int default NULL)
returns table(
	nome_canal varchar(255),
	valor_patrocinio float,
	nome_empresa varchar(255))
as $$
	SELECT
	  c.nome nome_canal,
	  p.valor valor_patrocinio,
	  e.nome nome_empresa
	FROM empresa e
		JOIN patrocinio p ON p.nro_empresa = e.nro
		JOIN canal c ON p.id_canal = c.id
	WHERE id_emp is null or id_emp = e.nro
	ORDER BY c.nome ASC;

$$ language sql;

select * from canaisPatrocinadosEmpresa(1);



/*2. Descobrir de quantos canais cada usuário é membro e a soma do valor desembolsado por
usuário por mês.
  // DEVE CONSIDERAR USUARIOS SEM INSCRIÇÃO?
  */

create or replace function gastoMembresia(id_user int default null)
returns table(
	nick varchar(100),
	qnt_canais_membro int,
	valor_gasto_mes float)
as $$
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
	WHERE id_user is null or id_user = u.id 
	GROUP BY u.nick
	ORDER BY
	  valor_gasto_mes DESC,
	  nome ASC;


$$ language sql;

select * from gastoMembresia(3);



/* 3. Listar e ordenar os canais que já receberam doações e a soma dos valores recebidos em
doação.
   SE É VALOR RECEBIDO ENTÃO O STATUS_PAGAMENTO TEM QUE SER CONCLUIDO? */



create or replace function doacoesCanal(id_escolhido int default null)
returns table(
	id_canal int,
	nome_canal varchar(255),
	qtd_doacoes int,
	total_doacao float
	)
as $$
	SELECT
	  d.id_canal,
	  d.nome,
	  d.qtd_doacoes,
	  d.total_doacao
	FROM
	  vw_faturamento_doacao as d
	where id_escolhido is null or id_escolhido = d.id_canal
	ORDER BY total_doacao DESC;

$$ language sql;




/* 4. Listar a soma das doações geradas pelos comentários que foram lidos por vídeo.   */

-- Vale a pena adicionar a coluna "coment_on" na view "vw_faturamento_doacao" ?




create or replace function doacoesComentariosLidos(id_escolhido int default null)
returns table(
	id_canal int,
	titulo_video varchar(255),
	qtd_doacoes_lidas int,
	total_doacao float
	)
as $$
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
		and id_escolhido is null or id_escolhido = com.id_video
	GROUP BY v.id
	ORDER BY total_doacao DESC;

$$ language sql;



--5. Listar e ordenar os k canais que mais recebem patrocínio e os valores recebidos.

create or replace function maiorPatrocinio(k int default NULL) 
returns table (
	nome varchar(255),
	qtd_patrocinios int,
	total_patrocinio float
	) 
as $$
SELECT
  nome,
  qtd_patrocinios,
  total_patrocinio
FROM vw_faturamento_patrocinio
ORDER BY qtd_patrocinios DESC, total_patrocinio DESC -- Ordena pela QUANTIDADE, como na sua query
LIMIT COALESCE(k, NULL);
$$ language sql;




--6. Listar e ordenar os k canais que mais recebem aportes de membros e os valores recebidos.


create or replace function maiorApoioMembros(k int default NULL) 
returns table (
	nome varchar(255),
	qtd_inscricoes int,
	total_inscricao float
	) 
as $$
SELECT
	  nome,
	  qtd_inscricoes,
	  total_inscricao
	FROM vw_faturamento_inscricao
	ORDER BY total_inscricao DESC
	LIMIT COALESCE(k, NULL);
$$ language sql;




--7. Listar e ordenar os k canais que mais receberam doações considerando todos os vídeos.


create or replace function maisDoacoes(k int default NULL) 
returns table (
	nome varchar(255),
	qtd_doacoes int,
	total_doacao float
	) 
as $$
	SELECT
	  nome,
	  qtd_doacoes,
	  total_doacao
	FROM
	  vw_faturamento_doacao
	ORDER BY qtd_doacoes DESC, total_doacao DESC
	LIMIT COALESCE(k, NULL);
$$ language sql;



--8. Listar os k canais que mais faturam considerando as três fontes de receita: patrocínio, membros inscritos e doações.

create or replace function maiorFaturamento(k int default NULL) 
returns table (
	nome varchar(255),
	f_patrocinio float,
	f_inscricao float,
	f_doacao float,
	faturamento_total float
	) 
as $$
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
	LIMIT COALESCE(k, NULL);
$$ language sql;



