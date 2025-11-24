"""
Módulo de população de dados organizado por níveis de dependência.

Este módulo coordena toda a lógica de geração e inserção de dados,
organizando as entidades em níveis hierárquicos baseados em suas dependências.
"""

import time
import random
from sqlalchemy.orm import Session
from faker import Faker

from .config import DataConfig
from .batch_inserter import BatchInserter
from models import Empresa, Conversao, Pais, Plataforma, Usuario, Video, Comentario
from aux_func import (
    generate_empresas, generate_conversoes, generate_paises, generate_plataformas,
    generate_usuarios, generate_plataforma_usuarios, generate_streamer_paises,
    generate_empresa_paises, generate_canais, generate_patrocinios,
    generate_nivel_canais, generate_inscricoes, generate_videos,
    generate_participacoes, generate_comentarios, generate_doacoes, generate_pagamentos
)


def populate_all_data(session: Session, fake: Faker, config: DataConfig) -> dict:
    """
    Popula todas as entidades do banco de dados seguindo a hierarquia de dependências.
    
    Args:
        session: Sessão do SQLAlchemy
        fake: Instância do Faker
        config: Configuração de volume de dados
        
    Returns:
        Dicionário com estatísticas de tempo por nível
    """
    inserter = BatchInserter(session, fake)
    timings = {}
    inicio_total = time.time()
    
    # ==================================================================================
    # NÍVEL 1: Entidades sem dependências
    # ==================================================================================
    print("📦 [1/9] Gerando empresas e conversões...")
    inicio = time.time()
    
    inserter.insert_simple(
        generate_empresas, config.n_empresas, config.batch_sizes.small,
        "Empresas"
    )
    
    inserter.insert_simple(
        generate_conversoes, config.n_conversoes, config.batch_sizes.tiny,
        "Conversões"
    )
    
    tempo_nivel1 = time.time() - inicio
    timings['nivel_1'] = tempo_nivel1
    print(f"    ✓ Nível 1 concluído em {tempo_nivel1:.2f}s\n")
    
    # ==================================================================================
    # NÍVEL 2: Dependem de empresas e conversões
    # ==================================================================================
    print("📦 [2/9] Gerando países e plataformas...")
    inicio = time.time()
    
    # Busca conversões para gerar países
    conversoes = session.query(Conversao).all()
    inserter.insert_simple(
        generate_paises, config.n_paises, config.batch_sizes.tiny,
        "Países", conversoes
    )
    
    # Busca empresas para gerar plataformas
    empresas = session.query(Empresa).all()
    inserter.insert_simple(
        generate_plataformas, config.n_plataformas, config.batch_sizes.tiny,
        "Plataformas", empresas
    )
    
    tempo_nivel2 = time.time() - inicio
    timings['nivel_2'] = tempo_nivel2
    print(f"    ✓ Nível 2 concluído em {tempo_nivel2:.2f}s\n")
    
    # ==================================================================================
    # NÍVEL 3: Usuários (CRÍTICO - MAIOR VOLUME)
    # ==================================================================================
    print(f"📦 [3/9] Gerando {config.n_usuarios:,} usuários em lotes...")
    inicio = time.time()
    
    paises = session.query(Pais).all()
    inserter.insert_with_offset(
        generate_usuarios, config.n_usuarios, config.batch_sizes.medium,
        "Usuários", paises
    )
    
    tempo_nivel3 = time.time() - inicio
    timings['nivel_3'] = tempo_nivel3
    print(f"    ✓ Nível 3 concluído em {tempo_nivel3:.2f}s\n")
    
    # Commit intermediário
    inserter.commit_with_timing("commit intermediário (após usuários)")
    
    # ==================================================================================
    # NÍVEL 4: Relacionamentos de usuários e canais
    # ==================================================================================
    print(f"📦 [4/9] Gerando relações de usuários e {config.n_canais:,} canais...")
    inicio = time.time()
    
    # Busca IDs de usuários e seleciona streamers
    print("    Carregando usuários...")
    usuario_ids = [row[0] for row in session.query(Usuario.id).all()]
    print(f"    {len(usuario_ids):,} usuários carregados")
    
    streamer_ids = random.sample(usuario_ids, config.n_streamers)
    print(f"    {len(streamer_ids):,} streamers selecionados")
    
    # Carrega objetos streamer em lotes
    streamers = []
    FETCH_BATCH = 10_000
    for i in range(0, len(streamer_ids), FETCH_BATCH):
        batch_ids = streamer_ids[i:i+FETCH_BATCH]
        streamers.extend(session.query(Usuario).filter(Usuario.id.in_(batch_ids)).all())
    
    print("    Gerando PlataformaUsuario...")
    plataformas_list = session.query(Plataforma).all()
    
    # PlataformaUsuario com estado compartilhado
    pk_pairs_state = set()
    uk_state = {p.nro: set() for p in plataformas_list}
    
    def generate_pu_wrapper(sample_usuarios, count, state):
        """Wrapper para adapt ar generate_plataforma_usuarios ao formato do BatchInserter."""
        return generate_plataforma_usuarios(
            plataformas_list, sample_usuarios, count,
            state['pk_pairs'], state['uk']
        )
    
    state_pu = {'pk_pairs': pk_pairs_state, 'uk': uk_state}
    inserter.insert_with_state(
        generate_pu_wrapper, config.n_plataforma_usuarios, config.batch_sizes.huge,
        "PlataformaUsuario", state_pu, usuario_ids, sample_size_multiplier=2
    )
    
    # StreamerPais e EmpresaPais
    print("    Gerando StreamerPais...")
    inserter.insert_simple(
        generate_streamer_paises, config.n_streamer_paises, config.batch_sizes.small,
        "StreamerPais", streamers, paises
    )
    
    print("    Gerando EmpresaPais...")
    inserter.insert_simple(
        generate_empresa_paises, config.n_empresa_paises, config.batch_sizes.small,
        "EmpresaPais", empresas, paises
    )
    
    # Canais
    print("    Gerando Canais...")
    inserter.insert_simple(
        generate_canais, config.n_canais, config.batch_sizes.medium,
        "Canais", plataformas_list, streamers
    )
    
    tempo_nivel4 = time.time() - inicio
    timings['nivel_4'] = tempo_nivel4
    print(f"    ✓ Nível 4 concluído em {tempo_nivel4:.2f}s\n")
    
    # Commit intermediário
    inserter.commit_with_timing("commit intermediário (após canais)")
    
    # ==================================================================================
    # NÍVEL 5: Patrocínios e níveis de canal
    # ==================================================================================
    print(f"📦 [5/9] Gerando {config.n_patrocinios:,} patrocínios e níveis de canal...")
    inicio = time.time()
    
    canais = session.query(Usuario).filter(Usuario.id.in_(streamer_ids)).all()  # Streamers == Canais
    
    inserter.insert_simple(
        generate_patrocinios, config.n_patrocinios, config.batch_sizes.medium,
        "Patrocínios", empresas, canais
    )
    
    inserter.insert_simple(
        generate_nivel_canais, config.n_niveis_totais, config.batch_sizes.medium,
        "NivelCanal", canais, config.niveis_por_canal
    )
    
    tempo_nivel5 = time.time() - inicio
    timings['nivel_5'] = tempo_nivel5
    print(f"    ✓ Nível 5 concluído em {tempo_nivel5:.2f}s\n")
    
    # ==================================================================================
    # NÍVEL 6: Inscrições e vídeos (CRÍTICO)
    # ==================================================================================
    print(f"📦 [6/9] Gerando {config.n_inscricoes:,} inscrições e {config.n_videos:,} vídeos...")
    inicio = time.time()
    
    # Busca níveis de canal
    from models import NivelCanal
    nivel_canais = session.query(NivelCanal).all()
    
    # Inscrições com estado
    print("    Gerando Inscrições...")
    inscricoes_pairs_state = set()
    
    def generate_insc_wrapper(sample_usuarios, count, state):
        """Wrapper para adaptar generate_inscricoes."""
        return generate_inscricoes(nivel_canais, sample_usuarios, count, state['pairs'])
    
    state_insc = {'pairs': inscricoes_pairs_state}
    inserter.insert_with_state(
        generate_insc_wrapper, config.n_inscricoes, config.batch_sizes.huge,
        "Inscrições", state_insc, usuario_ids, sample_size_multiplier=2
    )
    
    # Vídeos com offset
    print("    Gerando Vídeos...")
    inserter.insert_with_offset(
        generate_videos, config.n_videos, config.batch_sizes.large,
        "Vídeos", canais
    )
    
    tempo_nivel6 = time.time() - inicio
    timings['nivel_6'] = tempo_nivel6
    print(f"    ✓ Nível 6 concluído em {tempo_nivel6:.2f}s\n")
    
    # Commit intermediário
    inserter.commit_with_timing("commit intermediário (após vídeos)")
    
    # ==================================================================================
    # NÍVEL 7: Participações e comentários (MAIS CRÍTICO)
    # ==================================================================================
    print(f"📦 [7/9] Gerando {config.n_participacoes:,} participações e {config.n_comentarios:,} comentários...")
    inicio = time.time()
    
    # Carrega vídeos
    print("    Carregando vídeos...")
    video_ids = [row[0] for row in session.query(Video.id).all()]
    videos_objs = []
    FETCH_BATCH = 10_000
    for i in range(0, len(video_ids), FETCH_BATCH):
        batch_ids = video_ids[i:i+FETCH_BATCH]
        videos_objs.extend(session.query(Video).filter(Video.id.in_(batch_ids)).all())
    
    # Participações
    print("    Gerando Participações...")
    inserter.insert_simple(
        generate_participacoes, config.n_participacoes, config.batch_sizes.large,
        "Participações", videos_objs, streamers
    )
    
    # Comentários (MAIOR VOLUME) com estado
    print("    Gerando Comentários em lotes (pode demorar)...")
    num_seq_state = {}
    
    def generate_com_wrapper(sample_usuarios, count, state):
        """Wrapper para adaptar generate_comentarios."""
        return generate_comentarios(fake, count, videos_objs, sample_usuarios, state['num_seq'])
    
    state_com = {'num_seq': num_seq_state}
    
    # Comentários com commits periódicos
    inserted_comments = 0
    batch_size = config.batch_sizes.large
    total_batches = (config.n_comentarios + batch_size - 1) // batch_size
    
    for batch_num in range(1, total_batches + 1):
        current_size = min(batch_size, config.n_comentarios - inserted_comments)
        
        # Amostra usuários
        sample_size = min(current_size, len(usuario_ids))
        sample_ids = random.sample(usuario_ids, sample_size)
        usuarios_sample = session.query(Usuario).filter(Usuario.id.in_(sample_ids)).all()
        
        # Gera comentários
        com_batch = generate_comentarios(fake, current_size, videos_objs, usuarios_sample, num_seq_state)
        session.add_all(com_batch)
        session.flush()
        
        inserted_comments += len(com_batch)
        progress = (inserted_comments / config.n_comentarios) * 100
        print(f"    [{batch_num}/{total_batches}] {progress:.1f}% - {inserted_comments:,}/{config.n_comentarios:,} Comentários", end='\r')
        
        del com_batch, usuarios_sample
        
        # Commit a cada 5 lotes
        if batch_num % 5 == 0:
            session.commit()
    
    print()
    
    tempo_nivel7 = time.time() - inicio
    timings['nivel_7'] = tempo_nivel7
    print(f"    ✓ Nível 7 concluído em {tempo_nivel7:.2f}s\n")
    
    # Commit intermediário
    inserter.commit_with_timing("commit intermediário (após comentários)")
    
    # ==================================================================================
    # NÍVEL 8: Doações
    # ==================================================================================
    print("📦 [8/9] Gerando doações...")
    inicio = time.time()
    
    # Busca comentários para gerar doações
    comentarios_list = session.query(Comentario).limit(config.n_comentarios).all()
    inserter.insert_simple(
        generate_doacoes, len(comentarios_list), config.batch_sizes.large,
        "Doações", comentarios_list
    )
    
    tempo_nivel8 = time.time() - inicio
    timings['nivel_8'] = tempo_nivel8
    print(f"    ✓ Nível 8 concluído em {tempo_nivel8:.2f}s\n")
    
    # ==================================================================================
    # NÍVEL 9: Detalhes de pagamento
    # ==================================================================================
    print("📦 [9/9] Gerando detalhes de pagamento...")
    inicio = time.time()
    
    from models import Doacao
    doacoes = session.query(Doacao).all()
    bitcoins, cartoes, paypals, mec_plats = generate_pagamentos(fake, doacoes)
    
    session.add_all(bitcoins + cartoes + paypals + mec_plats)
    session.flush()
    
    tempo_nivel9 = time.time() - inicio
    timings['nivel_9'] = tempo_nivel9
    print(f"    ✓ Nível 9 concluído em {tempo_nivel9:.2f}s\n")
    
    # ==================================================================================
    # COMMIT FINAL
    # ==================================================================================
    inserter.commit_with_timing("commit final")
    
    timings['total'] = time.time() - inicio_total
    return timings
