SET SEARCH_PATH TO core;

--->>>>> verificar quando tiver muitos dados inseridos no banco

-- Indices do Vinicius --

-- Necessário para realizer o refresh Concurrently
CREATE UNIQUE INDEX idx_mv_fat_total_id ON vw_faturamento_total (id_canal);


-- -- Índices do Luiz --

-- Índice 1: Otimiza JOINs da tabela Patrocinio com Canal
-- Usado nas consultas 1, 5 e 8 que fazem JOIN entre patrocinio e canal
-- Melhora performance ao buscar patrocínios por canal (id_canal é foreign key frequentemente usada em JOINs)
CREATE INDEX idx_patrocinio_id_canal ON Patrocinio (id_canal);

-- Índice 2: Otimiza consulta 2 que agrupa inscrições por usuário
-- A consulta 2 faz JOIN entre inscricao e usuario através de id_membro
-- Este índice acelera a busca de todas as inscrições de um membro específico
CREATE INDEX idx_inscricao_id_membro ON Inscricao (id_membro);

-- Índice 3: Otimiza filtragem de doações concluídas
-- Usado nas consultas 3, 4 e views de faturamento que filtram por status_pagamento = 'CONCLUIDO'
-- Como há apenas 3 valores possíveis (PENDENTE, CONCLUIDO, FALHOU), o índice é eficiente para seletividade
CREATE INDEX idx_doacao_status_pagamento ON Doacao (status_pagamento);

-- Índice 4: Índice composto para otimizar consulta 4 (doações de comentários lidos)
-- A consulta 4 filtra comentários onde coment_on = true e depois faz JOIN com doacao
-- Este índice composto permite buscar rapidamente comentários lidos e seu vídeo associado
CREATE INDEX idx_comentario_coment_on_video ON Comentario (coment_on, id_video) WHERE coment_on
= true;
