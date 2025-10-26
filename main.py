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
            all_data = []

            # Nível 1: Sem dependências
            print("Gerando empresas e conversões...")
            empresas = generate_empresas(fake, N_EMPRESAS)
            conversoes = generate_conversoes(fake, N_CONVERSOES)
            lvl1_data = empresas + conversoes
            session.add_all(lvl1_data)
            all_data.extend(lvl1_data)
            session.flush()

            # Nível 2: Dependem de empresas e conversões
            print("Gerando países e plataformas...")
            paises = generate_paises(fake, N_PAISES, conversoes)
            plataformas = generate_plataformas(fake, N_PLATAFORMAS, empresas)
            lvl2_data = paises + plataformas
            session.add_all(lvl2_data)
            all_data.extend(lvl2_data)
            session.flush()

            # Nível 3: Dependem de países
            print(f"Gerando {N_USUARIOS} usuários...")
            usuarios = generate_usuarios(fake, N_USUARIOS, paises)
            session.add_all(usuarios)
            all_data.extend(usuarios)
            session.flush()

            # Nível 4: Dependem de usuários, plataformas, empresas, países
            print("Gerando relações de usuários...")
            streamers = random.sample(usuarios, N_STREAMERS)
            plataforma_usuarios = generate_plataforma_usuarios(plataformas, usuarios, N_PLATAFORMA_USUARIOS)
            streamer_paises = generate_streamer_paises(fake, streamers, paises, N_STREAMER_PAISES)
            empresa_paises = generate_empresa_paises(fake, empresas, paises, N_EMPRESA_PAISES)
            canais = generate_canais(fake, N_CANAIS, plataformas, streamers)
            lvl4_data = plataforma_usuarios + streamer_paises + empresa_paises + canais
            session.add_all(lvl4_data)
            all_data.extend(lvl4_data)
            session.flush()

            # Nível 5: Dependem de canais e empresas
            print("Gerando patrocínios e níveis de canal...")
            patrocinios = generate_patrocinios(fake, empresas, canais, N_PATROCINIOS)
            nivel_canais = generate_nivel_canais(fake, canais, NIVEIS_POR_CANAL)
            lvl5_data = patrocinios + nivel_canais
            session.add_all(lvl5_data)
            all_data.extend(lvl5_data)
            session.flush()

            # Nível 6: Dependem de níveis, usuários e canais
            print("Gerando inscrições e vídeos...")
            inscricoes = generate_inscricoes(nivel_canais, usuarios, N_INSCRICOES)
            videos = generate_videos(fake, N_VIDEOS, canais)
            lvl6_data = inscricoes + videos
            session.add_all(lvl6_data)
            all_data.extend(lvl6_data)
            session.flush()

            # Nível 7: Dependem de vídeos, usuários e streamers
            print("Gerando participações e comentários...")
            participacoes = generate_participacoes(videos, streamers, N_PARTICIPACOES)
            comentarios = generate_comentarios(fake, N_COMENTARIOS, videos, usuarios)
            lvl7_data = participacoes + comentarios
            session.add_all(lvl7_data)
            all_data.extend(lvl7_data)
            session.flush()

            # Nível 8: Dependem de comentários
            print("Gerando doações...")
            doacoes = generate_doacoes(fake, comentarios)
            session.add_all(doacoes)
            all_data.extend(doacoes)
            session.flush()

            # Nível 9: Dependem de doações
            print("Gerando detalhes de pagamento...")
            bitcoins, cartoes, paypals, mec_plats = generate_pagamentos(fake, doacoes)
            lvl9_data = bitcoins + cartoes + paypals + mec_plats
            session.add_all(lvl9_data)
            all_data.extend(lvl9_data)
            
            print(f"\nTotal de {len(all_data)} objetos gerados. Inserindo todos em uma única transação...")
            
            # Chamada única para insert_db, conforme solicitado.
            # Note que os objetos já foram adicionados à sessão com session.add_all.
            # Esta chamada pode ser redundante dependendo da implementação de insert_db,
            # mas está aqui para seguir o pedido.
            insert_db(session, all_data)
            
            session.commit()

            print("\nInserção de todos os dados concluída com sucesso!")

        except Exception as e:
            print(f"\nOcorreu um erro durante a inserção de dados: {e}")
            session.rollback()

if __name__ == "__main__":
    main()
