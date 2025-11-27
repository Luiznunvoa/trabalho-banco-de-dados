/*
  CRIAÇÃO DE SCHEDULE PARA ATUALIZAR VIEW MATERIALIZADA A CADA 5 MIN
*/

-- Cria um índice único para permitir atualização sem travar a tabela (Zero Downtime)
-- obrigatorio para usar concurrently (atualização nao bloqueante)
-- JUSTIFICATIVA: Necessidade de atualizar o pagamento de maneira mais eficiente do que
-- uma atualização a cada insert
CREATE UNIQUE INDEX idx_vw_fat_total_id_canal
ON vw_faturamento_total (id_canal);

CREATE EXTENSION IF NOT EXISTS pg_cron;

-- O formato é padrão CRON: minuto, hora, dia, mes, dia_semana
SELECT cron.schedule(
  'refresh_faturamento_5min', -- Nome da tarefa (opcional)
  '*/5 * * * *',                -- A cada 5 minutos
  'REFRESH MATERIALIZED VIEW CONCURRENTLY core.vw_faturamento_total'
);
