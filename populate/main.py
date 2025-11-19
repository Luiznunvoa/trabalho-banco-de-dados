from db import conn_db, insert_db
from faker import Faker
from sqlalchemy import text
from sqlalchemy.orm import Session
import random
from aux_func import (
    generate_empresas, generate_conversoes, generate_paises, generate_plataformas,
    generate_usuarios, generate_plataforma_usuarios, generate_streamer_paises,
    generate_empresa_paises, generate_canais, generate_patrocinios,
    generate_nivel_canais, generate_inscricoes, generate_videos,
    generate_participacoes, generate_comentarios, generate_doacoes, generate_pagamentos
)


def suggest(base_value, variation_percent=10):
    """
    Retorna um valor que varia em torno de um valor base.
    Para inteiros, retorna um inteiro. Para floats, retorna um float.
    A variação é de +/- variation_percent.
    """
    if base_value == 0:
        return 0
        
    variation = base_value * (variation_percent / 100.0)
    min_val = base_value - variation
    max_val = base_value + variation
    
    if isinstance(base_value, int):
        # Garante que o mínimo seja pelo menos 1 se o valor base for positivo.
        min_val = max(1, int(min_val))
        max_val = int(max_val)
        if min_val > max_val: # Pode acontecer se base_value for pequeno
            return min_val
        return random.randint(min_val, max_val)
    else: # float
        return random.uniform(min_val, max_val)

# --- CONTROLE DE QUANTIDADE DE DADOS (Configuração para alta volumetria) ---
# As constantes a seguir são tratadas como "sugestões" e uma variação aleatória
# é aplicada para tornar a geração de dados menos determinística.

# --- Entidades Principais (Sugestões) ---
SUGGEST_N_USUARIOS = 100_000
SUGGEST_N_EMPRESAS = 1_000
SUGGEST_N_PLATAFORMAS = 10
N_PAISES = 192  # Número realista de países, mantido fixo.

# --- Proporções e Entidades Derivadas (Sugestões) ---
SUGGEST_PCT_STREAMERS = 0.10
SUGGEST_VIDEOS_POR_CANAL = 2
SUGGEST_COMENTARIOS_POR_VIDEO = 5
SUGGEST_PLATAFORMAS_POR_USUARIO = 1.5
SUGGEST_INSCRICOES_POR_USUARIO = 1.25
SUGGEST_PARTICIPACOES_POR_VIDEO = 2
SUGGEST_NIVEIS_POR_CANAL = 3
SUGGEST_PATROCINIOS_POR_EMPRESA = 10

# --- Geração dos Valores Variáveis ---
N_USUARIOS = suggest(SUGGEST_N_USUARIOS)
N_EMPRESAS = suggest(SUGGEST_N_EMPRESAS)
N_PLATAFORMAS = suggest(SUGGEST_N_PLATAFORMAS)

PCT_STREAMERS = suggest(SUGGEST_PCT_STREAMERS)
N_STREAMERS = int(N_USUARIOS * PCT_STREAMERS)

N_CANAIS = N_STREAMERS  # Assumimos 1 canal por streamer
N_VIDEOS = N_CANAIS * suggest(SUGGEST_VIDEOS_POR_CANAL)
N_COMENTARIOS = N_VIDEOS * suggest(SUGGEST_COMENTARIOS_POR_VIDEO)

N_PLATAFORMA_USUARIOS = int(N_USUARIOS * suggest(SUGGEST_PLATAFORMAS_POR_USUARIO))
N_INSCRICOES = int(N_USUARIOS * suggest(SUGGEST_INSCRICOES_POR_USUARIO))
N_PARTICIPACOES = N_VIDEOS * suggest(SUGGEST_PARTICIPACOES_POR_VIDEO)

N_CONVERSOES = N_PAISES  # Simplificação: 1 tipo de moeda por país
NIVEIS_POR_CANAL = suggest(SUGGEST_NIVEIS_POR_CANAL)
N_PATROCINIOS = N_EMPRESAS * suggest(SUGGEST_PATROCINIOS_POR_EMPRESA)
N_STREAMER_PAISES = N_STREAMERS  # 1 nacionalidade por streamer
N_EMPRESA_PAISES = N_EMPRESAS    # 1 país de registro por empresa


def main():
    engine = conn_db()
    fake = Faker('pt_BR') 
    
    try:
        print("Recriando tabelas no banco de dados a partir de schema.sql...")
        with open('/home/luiz/Dev/UFF/BD2/trabalho banco de dados/schema.sql', 'r') as f:
            sql_script = f.read()

        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text(sql_script))
        
        print("Tabelas recriadas com sucesso.")
    except Exception as e:
        print(f"Erro ao recriar tabelas: {e}")
        return
        
    with Session(engine) as session:
        try:
            # Nível 1: Sem dependências
            print("Gerando empresas e conversões...")
            empresas = generate_empresas(fake, N_EMPRESAS)
            session.add_all(empresas)
            conversoes = generate_conversoes(fake, N_CONVERSOES)
            session.add_all(conversoes)
            session.flush()

            # Nível 2: Dependem de empresas e conversões
            print("Gerando países e plataformas...")
            paises = generate_paises(fake, N_PAISES, conversoes)
            session.add_all(paises)
            plataformas = generate_plataformas(fake, N_PLATAFORMAS, empresas)
            session.add_all(plataformas)
            session.flush()

            # Nível 3: Dependem de países
            print(f"Gerando {N_USUARIOS} usuários...")
            # NOTA: Para volumes realmente massivos (ex: >1M), esta parte precisaria ser dividida em lotes.
            usuarios = generate_usuarios(fake, N_USUARIOS, paises)
            session.add_all(usuarios)
            session.flush()

            # Nível 4: Dependem de usuários, plataformas, etc.
            print("Gerando relações de usuários e canais...")
            streamers = random.sample(usuarios, N_STREAMERS)
            plataforma_usuarios = generate_plataforma_usuarios(plataformas, usuarios, N_PLATAFORMA_USUARIOS)
            session.add_all(plataforma_usuarios)
            streamer_paises = generate_streamer_paises(fake, streamers, paises, N_STREAMER_PAISES)
            session.add_all(streamer_paises)
            empresa_paises = generate_empresa_paises(fake, empresas, paises, N_EMPRESA_PAISES)
            session.add_all(empresa_paises)
            canais = generate_canais(fake, plataformas, streamers)
            session.add_all(canais)
            session.flush()

            # Nível 5: Dependem de canais e empresas
            print("Gerando patrocínios e níveis de canal...")
            patrocinios = generate_patrocinios(fake, empresas, canais, N_PATROCINIOS)
            session.add_all(patrocinios)
            nivel_canais = generate_nivel_canais(fake, canais, NIVEIS_POR_CANAL)
            session.add_all(nivel_canais)
            session.flush()

            # Nível 6: Dependem de níveis, usuários e canais
            print("Gerando inscrições e vídeos...")
            inscricoes = generate_inscricoes(nivel_canais, usuarios, N_INSCRICOES)
            session.add_all(inscricoes)
            # NOTA: Geração de vídeos e comentários são os pontos mais críticos de memória.
            videos = generate_videos(fake, N_VIDEOS, canais)
            session.add_all(videos)
            session.flush()

            # Nível 7: Dependem de vídeos, usuários e streamers
            print("Gerando participações e comentários...")
            participacoes = generate_participacoes(videos, streamers, N_PARTICIPACOES)
            session.add_all(participacoes)
            comentarios = generate_comentarios(fake, N_COMENTARIOS, videos, usuarios)
            session.add_all(comentarios)
            session.flush()

            # Nível 8: Dependem de comentários
            print("Gerando doações...")
            doacoes = generate_doacoes(fake, comentarios)
            session.add_all(doacoes)
            session.flush()

            # Nível 9: Dependem de doações
            print("Gerando detalhes de pagamento...")
            bitcoins, cartoes, paypals, mec_plats = generate_pagamentos(fake, doacoes)
            session.add_all(bitcoins + cartoes + paypals + mec_plats)
            
            print(f"\nTodos os objetos foram gerados. Realizando o commit final da transação...")
            session.commit()

            print("\nInserção de todos os dados concluída com sucesso!")

        except Exception as e:
            print(f"\nOcorreu um erro durante a inserção de dados: {e}")
            session.rollback()

if __name__ == "__main__":
    main()
