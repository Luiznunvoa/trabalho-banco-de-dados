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

CREATE TRIGGER trg_safety_usuario_delete
BEFORE DELETE ON Usuario
FOR EACH ROW
EXECUTE FUNCTION fn_bloquear_delete_usuario();

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


