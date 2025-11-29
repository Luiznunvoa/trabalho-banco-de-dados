# Trabalho de Banco de Dados

## Como Rodar

### 1. Subir o banco de dados

```bash
cp .env.example .env
docker compose build
docker compose up -d
```

### 2. Popular o banco

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r populate/requirements.txt
python3 ./populate/main.py
```

### 3. Conectar ao banco

```bash
docker exec -it trabalho-bd psql -U admin -d db
```

---

## Comandos Úteis

```bash
# Ver logs
docker logs trabalho-bd

# Reiniciar do zero
docker compose down -v
docker compose build
docker compose up -d

# Listar presets de população
python3 ./populate/main.py --list
```
