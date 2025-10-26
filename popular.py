import pandas as pd
from sqlalchemy import create_engine
from faker import Faker

engine = create_engine('postgresql+psycopg2://admin:2444@72.60.156.198/banco')

sql_query = "SELECT * FROM teste_parrini.bitcoin" 

df = pd.read_sql(sql_query, con=engine)
print(df)

# --- 2. CONFIGURAÇÃO DO FAKER ---
fake = Faker('pt_BR')
NUM_CANAIS = 50
NUM_VIDEOS_POR_CANAL = 20
NUM_COMENTARIOS_POR_VIDEO = 50
NUM_NIVEIS_POR_CANAL = 3

# --- 3. MOCK IDS PARA CHAVES ESTRANGEIRAS (SUBSTITUA POR DADOS REAIS DO SEU BANCO!) ---
# IDs de Plataforma, Empresa e Usuário devem vir das suas tabelas 'bd2.plataforma', 'bd2.usuario', 'bd2.empresa'
plataforma_ids = list(range(1, 6)) # Ex: [1, 2, 3, 4, 5]
usuario_nicks = [fake.user_name() for _ in range(100)]
usuario_ids = list(range(1, 101)) # Ex: [1..100]
empresa_nros = list(range(1, 11)) # Ex: [1..10]

# Armazenará os IDs gerados
canal_ids = list(range(1, NUM_CANAIS + 1))
nivel_ids = list(range(1, (NUM_CANAIS * NUM_NIVEIS_POR_CANAL) + 1))

# Armazena as chaves compostas para uso posterior (Doacao, Bitcoin)
videos_keys = []
comentario_keys = []

# --- 5. FUNÇÃO PARA INSERÇÃO DE DADOS ---
def insert_data(conn, cursor, table_name, columns, values_list):
    if not values_list:
        return
    
    # Formata a string de colunas e placeholders
    cols_str = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))
    sql = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"
    
    # Executa o executemany para inserção em massa
    cursor.executemany(sql, values_list)
    print(f"Inseridos {len(values_list)} registros na tabela {table_name}.")
