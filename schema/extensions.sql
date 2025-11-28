-- Instala extensões necessárias antes de criar as tabelas
-- Este arquivo deve ser executado primeiro (00-extensions.sql)

CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE EXTENSION IF NOT EXISTS pg_cron;
