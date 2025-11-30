SET SEARCH_PATH TO core;

-- VIEW: vw_faturamento_doacao
-- JUSTIFICATIVA:
-- Esta view agrega o faturamento proveniente de doações por canal.
-- Facilita consultas sobre receita de doações sem necessidade de múltiplos JOINs
-- repetitivos. Considera apenas doações com pagamento concluído e filtra usuários
-- excluídos (tanto doadores quanto streamers), garantindo integridade dos dados
-- de faturamento ativo.
-- ==============================================================================
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


-- VIEW: vw_faturamento_patrocinio
-- JUSTIFICATIVA:
-- Esta view consolida os dados de patrocínios por canal, agregando quantidade
-- e valor total dos patrocínios. Simplifica análises de receita corporativa e
-- permite identificar rapidamente os canais com maior apoio de empresas.
-- Filtra streamers excluídos para manter apenas dados relevantes e ativos.
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


-- VIEW: vw_faturamento_inscricao
-- JUSTIFICATIVA:
-- Esta view agrega o faturamento recorrente proveniente de inscrições pagas
-- (memberships) por canal. Como as inscrições podem ter diferentes níveis com
-- valores distintos, a view soma os valores apropriados por nível. Essencial
-- para análise de receita recorrente e previsibilidade financeira dos canais.
-- Exclui membros e streamers inativos para refletir apenas assinaturas ativas.
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


-- MATERIALIZED VIEW: vw_faturamento_total
-- JUSTIFICATIVA:
-- Esta é a view principal da aplicação, consolidando TODAS as fontes de receita
-- de um canal (doações, patrocínios e inscrições) em uma única estrutura.
-- 
-- MOTIVOS PARA SER MATERIALIZADA:
-- 1. Performance: Evita recalcular JOINs complexos e agregações a cada consulta
-- 2. Consultas frequentes: Dashboard e relatórios acessam estes dados repetidamente
-- 3. Dados relativamente estáveis: Faturamento não muda a cada segundo
-- 4. Refresh agendado: Atualização automática a cada 5 minutos via pg_cron
--    balanceia atualidade dos dados com performance
-- 
-- DESIGN:
-- - LEFT JOINs garantem que canais apareçam mesmo sem alguma fonte de receita
-- - COALESCE trata valores NULL como 0 para cálculos corretos
-- - Filtra apenas streamers ativos (data_exclusao IS NULL)
-- - Estrutura modular: usa views base facilitando manutenção
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

-- AGENDAMENTO: Refresh Automático da Materialized View
-- JUSTIFICATIVA:
-- Agenda atualização automática da view materializada a cada 5 minutos usando
-- pg_cron. Este intervalo balanceia:
-- - Atualidade dos dados: Informações razoavelmente recentes para dashboards
-- - Performance: Evita sobrecarga de refresh muito frequente
-- - CONCURRENTLY: Permite consultas durante o refresh, sem bloquear leituras
-- 
-- REQUISITOS:
-- - Extensão pg_cron deve estar instalada e configurada
-- - Para REFRESH CONCURRENTLY funcionar, é necessário criar índice único
--   na view materializada (recomendado: CREATE UNIQUE INDEX ON vw_faturamento_total(id_canal))
-- O formato é padrão CRON: minuto, hora, dia, mes, dia_semana
SELECT
  cron.schedule(
    'refresh_faturamento_5min', -- Nome da tarefa (opcional)
    '*/5 * * * *',
    'REFRESH MATERIALIZED VIEW CONCURRENTLY core.vw_faturamento_total'
  );

-- verificação do cron
-- SELECT * FROM cron.job;
