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
#### Possível erro com doação caso nao possa ter 2 pagamentos para uma mesma doacao
O Risco: Nada no banco impede que uma mesma Doacao (ex: id_video 10, seq 5)
tenha registros na tabela Bitcoin E na tabela Paypal ao mesmo tempo.

Podemos considerar feature, ou ter que fazer alguma especie de verificação/lock
*/


/*
#### Trigger para visu_total
alternativa 1 -> asicamente todas alternativas que o gemini gera envolvem usar uma tablea de buffer rápida e depois atualizar a principal
-----> então as alternativas seguidas variam
a. uso de redis (banco de dados NoSQL de código aberto, na memória (in-memory), de chave-valor usado principalmente como cache ou banco de dados de alta performance)
b. schedule (pg_cron)
c. shards (fragmentação)
d. probabilistico (chance de atualizar toda vez que inserir)

alternativa 2-> trigger padrão a cada insert (paia)

alternativa 3-> deixar o backend se virar com um buffer
como que sabe que usuario deu play? problema de backend?

#### visu_simult
isso seria provavelmente algo do backend
o dado do servidor do frontend deve saber as conexões simultaneas, logo é preciso apenas um update regular
enquanto a stream está ativa, mas provavelmetne seria com um schedule no backend
ou guardaria um dado velho (ex. att a cada 2min)
*/


/*
#### Remoção de usuário, teremos que definit política
- Criação de coluna de verificação data_exclusão

teria que desconsiderar esses usuários em consultas? (talvez mais um parâmetro nas functions)
*/
-- 1. retirar permissao de delete na tabela
REVOKE DELETE ON TABLE Usuario FROM app_user;

--2. Trigger de bloqueio de delete
CREATE OR REPLACE FUNCTION fn_bloquear_delete_usuario()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Proibido deletar usuários fisicamente. Use UPDATE SET data_exclusao = NOW() para Soft Delete.';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_safety_usuario_delete
BEFORE DELETE ON Usuario
FOR EACH ROW
EXECUTE FUNCTION fn_bloquear_delete_usuario();

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
#### Sequencial de comentário
terá que usar trigger? (vai perder eficiencia) lock no usuario depois somar num+=1
*/
-- Ele vai dar lock no usuário específico comentando, calcular o proximo sequencial
    -- terá uma trigger antes do comentário ser inserido
    -- garante que o numero será sequencial por usuário em cada vídeo

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

*/


