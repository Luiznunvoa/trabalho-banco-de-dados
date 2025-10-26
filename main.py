from db import conn_db, insert_db
from faker import Faker
from models import Base 
from sqlalchemy.orm import Session 
import random
from aux_func import (
    generate_empresas, generate_conversoes, generate_paises, generate_plataformas,
    generate_usuarios, generate_plataforma_usuarios, generate_streamer_paises,
    generate_empresa_paises, generate_canais, generate_patrocinios,
    generate_nivel_canais, generate_inscricoes, generate_videos,
    generate_participacoes, generate_comentarios, generate_doacoes, generate_pagamentos
)

# --- CONTROLE DE QUANTIDADE DE DADOS ---
N_EMPRESAS = 1000
N_CONVERSOES = 100
N_PAISES = 50
N_PLATAFORMAS = 50
N_USUARIOS = 1000
N_STREAMERS = 100
N_PLATAFORMA_USUARIOS = 2000
N_STREAMER_PAISES = 150
N_EMPRESA_PAISES = 200
N_CANAIS = 150
N_PATROCINIOS = 100
NIVEIS_POR_CANAL = 3
N_INSCRICOES = 500
N_VIDEOS = 1000
N_PARTICIPACOES = 1500
N_COMENTARIOS = 5000
# -----------------------------------------

def main():
    engine = conn_db()
    fake = Faker('pt_BR') 
    
    try:
        print("Criando tabelas no banco de dados...")
        Base.metadata.create_all(engine)
        print("Tabelas verificadas/criadas com sucesso.")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        return
        
    with Session(engine) as session:
        try:
            # Nível 1: Sem dependências
            print(f"Gerando e inserindo {N_EMPRESAS} empresas e {N_CONVERSOES} conversões...")
            empresas = generate_empresas(fake, N_EMPRESAS)
            insert_db(session, empresas)
            conversoes = generate_conversoes(fake, N_CONVERSOES)
            insert_db(session, conversoes)
            session.commit()

            # Nível 2: Dependem de empresas e conversões
            print(f"Gerando e inserindo {N_PAISES} países e {N_PLATAFORMAS} plataformas...")
            paises = generate_paises(fake, N_PAISES, conversoes)
            insert_db(session, paises)
            plataformas = generate_plataformas(fake, N_PLATAFORMAS, empresas)
            insert_db(session, plataformas)
            session.commit()

            # Nível 3: Dependem de países
            print(f"Gerando e inserindo {N_USUARIOS} usuários...")
            usuarios = generate_usuarios(fake, N_USUARIOS, paises)
            insert_db(session, usuarios)
            session.commit()

            # Nível 4: Dependem de usuários, plataformas, empresas, países
            print("Gerando e inserindo relações de usuários...")
            streamers = random.sample(usuarios, N_STREAMERS)
            plataforma_usuarios = generate_plataforma_usuarios(plataformas, usuarios, N_PLATAFORMA_USUARIOS)
            insert_db(session, plataforma_usuarios)
            streamer_paises = generate_streamer_paises(fake, streamers, paises, N_STREAMER_PAISES)
            insert_db(session, streamer_paises)
            empresa_paises = generate_empresa_paises(fake, empresas, paises, N_EMPRESA_PAISES)
            insert_db(session, empresa_paises)
            canais = generate_canais(fake, N_CANAIS, plataformas, streamers)
            insert_db(session, canais)
            session.commit()

            # Nível 5: Dependem de canais e empresas
            print("Gerando e inserindo patrocínios e níveis de canal...")
            patrocinios = generate_patrocinios(fake, empresas, canais, N_PATROCINIOS)
            insert_db(session, patrocinios)
            nivel_canais = generate_nivel_canais(fake, canais, NIVEIS_POR_CANAL)
            insert_db(session, nivel_canais)
            session.commit()

            # Nível 6: Dependem de níveis, usuários e canais
            print("Gerando e inserindo inscrições e vídeos...")
            inscricoes = generate_inscricoes(nivel_canais, usuarios, N_INSCRICOES)
            insert_db(session, inscricoes)
            videos = generate_videos(fake, N_VIDEOS, canais)
            insert_db(session, videos)
            session.commit()

            # Nível 7: Dependem de vídeos, usuários e streamers
            print("Gerando e inserindo participações e comentários...")
            participacoes = generate_participacoes(videos, streamers, N_PARTICIPACOES)
            insert_db(session, participacoes)
            comentarios = generate_comentarios(fake, N_COMENTARIOS, videos, usuarios)
            insert_db(session, comentarios)
            session.commit()

            # Nível 8: Dependem de comentários
            print("Gerando e inserindo doações...")
            doacoes = generate_doacoes(fake, comentarios)
            insert_db(session, doacoes)
            session.commit()

            # Nível 9: Dependem de doações
            print("Gerando e inserindo detalhes de pagamento...")
            bitcoins, cartoes, paypals, mec_plats = generate_pagamentos(fake, doacoes)
            insert_db(session, bitcoins)
            insert_db(session, cartoes)
            insert_db(session, paypals)
            insert_db(session, mec_plats)
            session.commit()

            print("\nInserção de todos os dados concluída com sucesso!")

        except Exception as e:
            print(f"\nOcorreu um erro durante a inserção de dados: {e}")
            session.rollback()

if __name__ == "__main__":
    main()
