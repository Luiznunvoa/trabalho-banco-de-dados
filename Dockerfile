# Use a imagem oficial do PostgreSQL 17
FROM postgres:17

# Instala pg_cron
RUN apt-get update && \
    apt-get install -y postgresql-17-cron && \
    rm -rf /var/lib/apt/lists/*

# Copia o arquivo de configuração customizado
COPY postgresql.conf /tmp/postgresql.conf

# Script para adicionar configurações ao postgresql.conf
RUN cat /tmp/postgresql.conf >> /usr/share/postgresql/postgresql.conf.sample
