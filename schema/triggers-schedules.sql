SET SEARCH_PATH TO core;

-- 1 - AGENDAMENTO CRON: Refresh da Materialized View
-- JUSTIFICATIVA:
-- Atualiza automaticamente vw_faturamento_total a cada 5 minutos.
-- CONCURRENTLY permite que consultas continuem durante o refresh sem bloqueio.
-- Intervalo de 5 minutos balanceia:
-- - Atualidade: Dados relativamente recentes para dashboards
-- - Performance: Evita sobrecarga de refresh muito frequente em tabelas grandes
-- - Carga do sistema: Não impacta operações transacionais (INSERTs, UPDATEs)
-- O formato é padrão CRON: minuto, hora, dia, mes, dia_semana
SELECT cron.schedule(
  'refresh_faturamento_5min', -- Nome da tarefa (opcional)
  '*/5 * * * *',                -- A cada 5 minutos
  'REFRESH MATERIALIZED VIEW CONCURRENTLY core.vw_faturamento_total'
);

-- 2 -TRIGGER: trg_usuario_soft_delete
-- OBJETIVO:
-- Implementa soft delete automático na tabela Usuario, preservando dados
-- históricos e mantendo integridade referencial sem cascatas destrutivas.
--
-- JUSTIFICATIVA:
-- 1. CONFORMIDADE LEGAL: Atende requisitos de auditoria 
-- 2. INTEGRIDADE DE DADOS: Preserva referências em Doacao, Comentario, Inscricao
--    sem necessidade de ON DELETE CASCADE
-- 3. RECUPERAÇÃO: Permite restaurar contas excluídas acidentalmente
-- 4. ANÁLISE: Mantém dados históricos para relatórios e analytics
--
-- FUNCIONAMENTO:
-- Intercepta comandos DELETE e os converte em UPDATE, marcando data_exclusao.
-- Retorna NULL para cancelar o DELETE original. Transparente para aplicação.
--
-- IMPACTO:
-- - Views e consultas devem filtrar por data_exclusao IS NULL
-- - Comandos DELETE na tabela Usuario nunca removem fisicamente os dados
--3. Trigger que substitui Delete por Update
CREATE OR REPLACE FUNCTION fn_soft_delete_automatico()
RETURNS TRIGGER AS $$
BEGIN
    -- O 'OLD' contém os dados da linha que seria deletada.
    -- Nós usamos o ID dela para fazer o UPDATE.
    UPDATE Usuario
    SET data_exclusao = CURRENT_TIMESTAMP
    WHERE id = OLD.id;

    -- Ao retornar NULL em um trigger "BEFORE DELETE",
    -- você diz ao Postgres: "Cancele o comando DELETE original".
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_usuario_soft_delete
BEFORE DELETE ON Usuario
FOR EACH ROW
EXECUTE FUNCTION fn_soft_delete_automatico();

-- 3 - TRIGGER: trg_auto_seq_comentario
-- OBJETIVO:
-- Gera automaticamente o número sequencial (num_seq) de comentários por usuário
-- em cada vídeo, garantindo sequência única e sem gaps.
--
-- JUSTIFICATIVA:
-- 1. MODELO DE DADOS: Comentario tem chave composta (id_video, id_usuario, num_seq)
--    onde num_seq é sequencial POR USUÁRIO em cada vídeo
-- 2. EXPERIÊNCIA DO USUÁRIO: Permite rastrear histórico de comentários de um
--    usuário em um vídeo específico (1º, 2º, 3º comentário, etc.)
-- 3. ATOMICIDADE: Garante que não haja conflitos de numeração em inserções
--    concorrentes usando FOR UPDATE lock
--
-- FUNCIONAMENTO:
-- - LOCK: Trava apenas a linha do usuário específico (não bloqueia outros usuários)
-- - CÁLCULO: Busca MAX(num_seq) do usuário naquele vídeo e incrementa
-- - Se usuário nunca comentou no vídeo: COALESCE retorna 0, primeiro será 1
--
-- PERFORMANCE:
-- Lock granular (por usuário) permite alta concorrência. Múltiplos usuários
-- podem comentar no mesmo vídeo simultaneamente sem contenção.
CREATE OR REPLACE FUNCTION fn_calcular_seq_comentario_usuario()
RETURNS TRIGGER AS $$
BEGIN
    -- LOCK (Segurança):
    -- Travamos a linha do USUÁRIO na tabela Usuario.
    -- Outros usuários NÃO são afetados e continuam comentando livremente.
    PERFORM 1 FROM Usuario WHERE id = NEW.id_usuario FOR UPDATE;

    -- CÁLCULO:
    -- Busca o maior num_seq que ESTE usuário (NEW.id_usuario) já tem NESTE vídeo (NEW.id_video).
    -- Se não tiver nenhum (NULL), o COALESCE transforma em 0 e soma 1.
    SELECT COALESCE(MAX(num_seq), 0) + 1
    INTO NEW.num_seq
    FROM Comentario
    WHERE id_video = NEW.id_video
      AND id_usuario = NEW.id_usuario;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auto_seq_comentario
BEFORE INSERT ON Comentario
FOR EACH ROW
EXECUTE FUNCTION fn_calcular_seq_comentario_usuario();

-- 4 - PROCEDURE: proc_atualizar_qtd_user
-- OBJETIVO:
-- Atualiza o contador desnormalizado qtd_users na tabela Plataforma, refletindo
-- o número real de usuários ativos em cada plataforma.
--
-- JUSTIFICATIVA:
-- 1. PERFORMANCE: Evita COUNT(*) com JOINs em cada consulta de estatísticas
-- 2. DESNORMALIZAÇÃO CONTROLADA: Mantém dados agregados para dashboards
-- 3. CONSISTÊNCIA EVENTUAL: Execução agendada aceita pequena defasagem (6h)
--    em troca de não impactar transações em tempo real
-- 4. ANÁLISE DE NEGÓCIO: Facilita relatórios de popularidade de plataformas
--
-- FREQUÊNCIA:
-- A cada 6 horas (0 */6 * * *) - adequado para dados que mudam gradualmente
-- e não exigem precisão em tempo real.
--
-- CONSIDERAÇÕES:
-- - Filtra usuários excluídos (data_exclusao IS NULL)
-- - Atualiza todas as plataformas de uma vez
-- - Uso de RAISE NOTICE para logging de execução
CREATE OR REPLACE PROCEDURE proc_atualizar_qtd_user()
AS $$
BEGIN
    UPDATE Plataforma p
    SET qtd_users = (
        SELECT COUNT(pu.id_usuario)
        FROM PlataformaUsuario pu
        INNER JOIN Usuario u ON pu.id_usuario = u.id
        WHERE pu.nro_plataforma = p.nro
          AND u.data_exclusao IS NULL
    );
    
    RAISE NOTICE 'Contador de usuário por plataforma atualizado com sucesso.';
END;
$$ LANGUAGE plpgsql;

-- AGENDAMENTO CRON: Atualização de qtd_users por plataforma
-- Executa a cada 6 horas (às 00:00, 06:00, 12:00, 18:00)
-- Frequência adequada para dados que variam lentamente e não críticos
SELECT cron.schedule(
  'proc_atualizar_qtd_user',
  '0 */6 * * *',
  'CALL core.proc_atualizar_qtd_user()'
);

-- 5 - PROCEDURE: proc_atualizar_qtd_visu
-- OBJETIVO:
-- Atualiza o contador desnormalizado qtd_visualizacoes na tabela Canal,
-- somando as visualizações de todos os vídeos do canal.
--
-- JUSTIFICATIVA:
-- 1. PERFORMANCE CRÍTICA: qtd_visualizacoes é métrica chave para rankings e
--    recomendações - calcular em tempo real seria muito custoso
-- 2. DASHBOARDS: Estatísticas de canais são consultadas frequentemente
-- 3. PRECISÃO ADEQUADA: Atualização horária é suficiente para análises,
--    já que visualizações acumulam gradualmente
-- 4. ESCALABILIDADE: Desacopla agregação de consultas, permitindo milhões
--    de visualizações sem impactar leituras
--
-- FREQUÊNCIA:
-- A cada 1 hora (0 */1 * * *) - mais frequente que qtd_users pois visualizações
-- são métricas mais dinâmicas e importantes para o negócio.
--
-- CONSIDERAÇÕES:
-- - Usa COALESCE para canais sem vídeos (retorna 0)
-- - Considera visu_total de cada vídeo (que pode ser mantida por trigger separado)
-- - Atualiza todos os canais simultaneamente

CREATE OR REPLACE PROCEDURE proc_atualizar_qtd_visu()
AS $$
BEGIN

    UPDATE Canal c
    SET qtd_visualizacoes = (
        SELECT COALESCE(SUM(v.visu_total), 0)
        FROM Video v
        WHERE v.id_canal = c.id
    );

    RAISE NOTICE 'Contador de visualizações atualizado com sucesso.';
END;
$$ LANGUAGE plpgsql;


-- AGENDAMENTO CRON: Atualização de visualizações por canal
-- Executa a cada 1 hora (início de cada hora: 00:00, 01:00, 02:00, etc.)
-- Frequência maior que qtd_users pois visualizações são métrica mais dinâmica
SELECT cron.schedule(
  'proc_atualizar_qtd_visu',
  '0 */1 * * *',
  'CALL core.proc_atualizar_qtd_visu()'
);

-- 6 - PROCEDURE: proc_atualizar_max_visu_simult
-- OBJETIVO:
-- Atualiza uma métrica agregada no Canal com o pico máximo de visualizações
-- simultâneas entre todos os vídeos do canal, representando o maior número de
-- espectadores simultâneos já alcançado.
--
-- JUSTIFICATIVA:
-- 1. MÉTRICA DE POPULARIDADE: Pico de visualizações simultâneas indica alcance
--    e capacidade de engajamento ao vivo do canal
-- 2. RANKINGS: Essencial para classificar canais por desempenho de lives/streams
-- 3. ANÁLISE DE CRESCIMENTO: Permite rastrear evolução do alcance do canal
-- 4. PERFORMANCE: Evita MAX() com JOIN em consultas de dashboard
--
-- FREQUÊNCIA:
-- A cada 30 minutos (*/30 * * * *) - frequência moderada pois:
-- - Visualizações simultâneas variam durante lives mas estabilizam depois
-- - Mais frequente que qtd_visualizacoes (1h) mas menos que faturamento (5min)
-- - Balanceia atualidade com carga do sistema
--
-- CONSIDERAÇÕES:
-- - Usa COALESCE para canais sem vídeos ou sem views simultâneas (retorna 0)
-- - Considera visu_simult de cada vídeo
-- - MAX captura o pico histórico entre todos os vídeos
CREATE OR REPLACE PROCEDURE proc_atualizar_max_visu_simult()
AS $$
BEGIN
    -- Nota: Esta procedure requer a coluna max_visu_simult na tabela Canal
    -- Se a coluna não existir, descomente a linha abaixo uma vez:
    -- ALTER TABLE Canal ADD COLUMN IF NOT EXISTS max_visu_simult INT DEFAULT 0;

    UPDATE Canal c
    SET visu_simult = (
        SELECT COALESCE(MAX(v.visu_simult), 0)
        FROM Video v
        WHERE v.id_canal = c.id
    );

    RAISE NOTICE 'Pico de visualizações simultâneas atualizado com sucesso.';
END;
$$ LANGUAGE plpgsql;


-- AGENDAMENTO CRON: Atualização de pico de visualizações simultâneas por canal
-- Executa a cada 30 minutos (aos minutos 00 e 30 de cada hora)
-- Frequência intermediária entre qtd_visualizacoes (1h) e faturamento (5min)
-- Adequada para métrica que muda durante lives mas não precisa ser tempo real
SELECT cron.schedule(
  'proc_atualizar_max_visu_simult',
  '*/30 * * * *',
  'CALL core.proc_atualizar_max_visu_simult()'
);

-- 7 - TRIGGER: verificar_metodo_pagamento_unico (múltiplas tabelas)
-- OBJETIVO:
-- Garante que cada doação tenha APENAS UM método de pagamento associado,
-- implementando constraint de integridade sobre especialização de tabelas.
--
-- JUSTIFICATIVA:
-- 2. INTEGRIDADE DE NEGÓCIO: Impossível pagar uma doação com múltiplos métodos
--    (não é carrinho de compras, é transação única)
-- 3. CONSTRAINT COMPLEXA: SQL não tem suporte nativo para "OU exclusivo" entre
--    tabelas relacionadas - trigger é a solução adequada
-- 4. PREVENÇÃO DE BUGS: Evita inconsistências caso aplicação tente inserir
--    múltiplos métodos por erro
--
-- FUNCIONAMENTO:
-- - BEFORE INSERT em cada tabela de método de pagamento
-- - Verifica se já existe registro nas outras 3 tabelas para mesma doação
-- - TG_TABLE_NAME evita verificação recursiva na própria tabela
-- - RAISE EXCEPTION com mensagem clara indicando qual método já existe
--
-- TABELAS PROTEGIDAS:
-- - Bitcoin, CartaoCredito, Paypal, MecPlat (todas com mesmo trigger)
--
-- PERFORMANCE:
-- Impacto mínimo - 3 EXISTS simples em índices de chaves primárias.
-- Essencial para manter consistência do modelo.
-- Função que verifica se já existe método de pagamento para a doação
CREATE OR REPLACE FUNCTION verificar_metodo_pagamento_unico()
RETURNS TRIGGER AS $$
DECLARE
  metodo_existente TEXT;
BEGIN
  -- Verifica se já existe pagamento em Bitcoin
  IF TG_TABLE_NAME != 'bitcoin' AND EXISTS (
    SELECT 1 FROM Bitcoin
    WHERE id_video_doacao = NEW.id_video_doacao
      AND seq_doacao = NEW.seq_doacao
      AND id_usuario = NEW.id_usuario
  ) THEN
    metodo_existente := 'Bitcoin';
  END IF;

  -- Verifica se já existe pagamento em CartaoCredito
  IF TG_TABLE_NAME != 'cartaocredito' AND EXISTS (
    SELECT 1 FROM CartaoCredito
    WHERE id_video_doacao = NEW.id_video_doacao
      AND seq_doacao = NEW.seq_doacao
      AND id_usuario = NEW.id_usuario
  ) THEN
    metodo_existente := 'Cartão de Crédito';
  END IF;

  -- Verifica se já existe pagamento em Paypal
  IF TG_TABLE_NAME != 'paypal' AND EXISTS (
    SELECT 1 FROM Paypal
    WHERE id_video_doacao = NEW.id_video_doacao
      AND seq_doacao = NEW.seq_doacao
      AND id_usuario = NEW.id_usuario
  ) THEN
    metodo_existente := 'Paypal';
  END IF;

  -- Verifica se já existe pagamento em MecPlat
  IF TG_TABLE_NAME != 'mecplat' AND EXISTS (
    SELECT 1 FROM MecPlat
    WHERE id_video_doacao = NEW.id_video_doacao
      AND seq_doacao = NEW.seq_doacao
      AND id_usuario = NEW.id_usuario
  ) THEN
    metodo_existente := 'Mecanismo da Plataforma';
  END IF;

  -- Se já existe um método, lança erro
  IF metodo_existente IS NOT NULL THEN
    RAISE EXCEPTION 'Doação (video: %, seq: %, usuario: %) já possui método de pagamento: %',
      NEW.id_video_doacao, NEW.seq_doacao, NEW.id_usuario, metodo_existente;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicação dos Triggers de Método de Pagamento Único
-- Cada trigger protege sua respectiva tabela, garantindo exclusividade mútua

-- Trigger para Bitcoin
CREATE TRIGGER trigger_verificar_metodo_pagamento_bitcoin
BEFORE INSERT ON Bitcoin
FOR EACH ROW
EXECUTE FUNCTION verificar_metodo_pagamento_unico();

-- Trigger para CartaoCredito
CREATE TRIGGER trigger_verificar_metodo_pagamento_cartao
BEFORE INSERT ON CartaoCredito
FOR EACH ROW
EXECUTE FUNCTION verificar_metodo_pagamento_unico();

-- Trigger para Paypal
CREATE TRIGGER trigger_verificar_metodo_pagamento_paypal
BEFORE INSERT ON Paypal
FOR EACH ROW
EXECUTE FUNCTION verificar_metodo_pagamento_unico();

-- Trigger para MecPlat (Mecanismo da Plataforma)
CREATE TRIGGER trigger_verificar_metodo_pagamento_mecplat
BEFORE INSERT ON MecPlat
FOR EACH ROW
EXECUTE FUNCTION verificar_metodo_pagamento_unico();