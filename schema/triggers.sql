SET SEARCH_PATH TO core;

/*
  SCHEDULE PARA ATUALIZAR VIEW MATERIALIZADA A CADA 5 MIN
*/

CREATE UNIQUE INDEX idx_vw_fat_total_id_canal
ON core.vw_faturamento_total (id_canal);

-- O formato é padrão CRON: minuto, hora, dia, mes, dia_semana
SELECT cron.schedule(
  'refresh_faturamento_5min', -- Nome da tarefa (opcional)
  '*/5 * * * *',                -- A cada 5 minutos
  'REFRESH MATERIALIZED VIEW CONCURRENTLY core.vw_faturamento_total'
);

-- NOTA: A função fn_bloquear_delete_usuario() não foi criada em funcoes.sql
-- Este trigger está comentado até que a função seja implementada
-- CREATE TRIGGER trg_safety_usuario_delete
-- BEFORE DELETE ON Usuario
-- FOR EACH ROW
-- EXECUTE FUNCTION fn_bloquear_delete_usuario();

/*
  TRIGGER PAR GARANTIR SOFT DELETE DE USUÁRIO
  Luiz: Eu escolhi essa pq parece fazer mais sentido
*/

--3. Trigger que substitui Delete por Update
CREATE OR REPLACE FUNCTION fn_soft_delete_automatico()
RETURNS TRIGGER AS $$
BEGIN
    -- O 'OLD' contém os dados da linha que seria deletada.
    -- Nós usamos o ID dela para fazer o UPDATE.
    UPDATE Usuario
    SET data_exclusao = CURRENT_TIMESTAMP
    WHERE id = OLD.id;

    -- O PULO DO GATO:
    -- Ao retornar NULL em um trigger "BEFORE DELETE",
    -- você diz ao Postgres: "Cancele o comando DELETE original".
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_usuario_soft_delete
BEFORE DELETE ON Usuario
FOR EACH ROW
EXECUTE FUNCTION fn_soft_delete_automatico();

/*
  TRIGGER PAR GARANTIR SEQUENCIALIDADE DO NÚMERO SEQUENCIAL DE COMENTÁRIO
*/
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






/*
  PROCEDURES PARA ATUALIZAÇÃO DE CONTADORES
*/
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


SELECT cron.schedule(
    'proc_atualizar_qtd_user',
    '0 */6 * * *',
    'CALL core.proc_atualizar_qtd_user()'
);


/*
  PROCEDURE PARA ATUALIZAÇÃO DE CONTADOR DE VISUALIZAÇÕES
*/

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


SELECT cron.schedule(
    'proc_atualizar_qtd_visu',
    '0 */1 * * *',
    'CALL core.proc_atualizar_qtd_visu()'
);