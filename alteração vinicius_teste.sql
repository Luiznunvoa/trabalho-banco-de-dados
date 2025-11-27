SET SEARCH_PATH TO core;

/*
CRIAÇÃO DE SCHEDULE PARA ATUALIZAR VIEW MATERIALIZADA A CADA 5 MIN
*/

-- Cria um índice único para permitir atualização sem travar a tabela (Zero Downtime)
    -- obrigatorio para usar concurrently (atualização nao bloqueante)
CREATE UNIQUE INDEX idx_vw_fat_total_id_canal
ON vw_faturamento_total (id_canal);

CREATE EXTENSION IF NOT EXISTS pg_cron;

-- O formato é padrão CRON: minuto, hora, dia, mes, dia_semana
SELECT cron.schedule(
  'refresh_faturamento_5min', -- Nome da tarefa (opcional)
  '*/5 * * * *',                -- A cada 5 minutos
  'REFRESH MATERIALIZED VIEW CONCURRENTLY core.vw_faturamento_total'
);

-- verificação do cron
SELECT * FROM cron.job;


/*
#### Possível erro com doação
O Risco: Nada no banco impede que uma mesma Doacao (ex: id_video 10, seq 5) tenha registros na tabela Bitcoin E na tabela Paypal ao mesmo tempo.

Via Banco (Recomendado): Adicionar uma coluna tipo_pagamento na tabela Doacao e usar uma Constraint Check ou Trigger para garantir a integridade.
*/


/*
#### Trigger para visu_total
gemini sugeriu redis para memo + cron para update (nao sei se pode usar redis)
como que sabe que usuario deu play? problema de backend?

#### visu_simult
isso seria provavelmente algo do backend
ou guardaria um dado velho (ex. att a cada 2min)
*/


/*
#### Remoção de usuário, teremos que definit política
1. usuário default (perde um pouco de valor nos dados (de onde que a pessoa é por exemplo) )
2. criação de coluna de verificação ex. data_exclusão ou ativo (pode dar problema pois altera o modelo do professor)

dos 2 jeitos precisaria de uma trigger e possivelmente function para atualizar
teria que desconsiderar esses usuários em consultas? (talvez mais um parâmetro nas functions)
*/


/*
#### Sequencial de comentário
terá que usar trigger? (vai perder eficiencia) lock no usuario depois somar num+=1
*/


/*

*/