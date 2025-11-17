-- 1. Identificar quais são os canais patrocinados e os valores de patrocínio pagos por empresa.
--Dar a opção de filtrar os resultados por empresa como um parâmetro opcional na forma de uma 
-- stored procedure.


CREATE OR REPLACE FUNCTION VALORESPOREMPRESA(id_empresa int DEFAULT null)
RETURNS TABLE (
  id int,
  nome_canal varchar(255),
  nro_plataforma int,
  nome_empresa varchar(255),
  valor_pago float
)
AS $$
	select c.id, c.nome as nome_canal, c.nro_plataforma, e.nome as nome_empresa, sum(p.valor) as valor_pago
	from Canal c join Patrocinio p on c.id = p.id_canal
		join Empresa e on p.nro_empresa = e.nro
	where id_empresa is null or e.nro = id_empresa
	group by c.id, c.nome, c.nro_plataforma, e.nome
	
$$ LANGUAGE sql;
