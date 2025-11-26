"""
Nível 7: Participações e comentários (MAIS CRÍTICO).

Popula Participacoes e Comentarios - maior volume de dados.
"""

import time
import random
from sqlalchemy.orm import Session
from faker import Faker

from ...config import DataConfig
from ...batch_inserter import BatchInserter
from models import Usuario, Video
from aux_func import generate_participacoes, generate_comentarios


def populate_level_7(session: Session, fake: Faker, config: DataConfig, inserter: BatchInserter) -> float:
    """
    Popula entidades do nível 7: Participações e Comentários.
    
    Args:
        session: Sessão do SQLAlchemy
        fake: Instância do Faker
        config: Configuração de volume de dados
        inserter: Instância do BatchInserter
        
    Returns:
        Tempo de execução em segundos
    """
    print(f"📦 [7/9] Gerando {config.n_participacoes:,} participações e {config.n_comentarios:,} comentários...")
    inicio = time.time()
    
    # Carrega apenas os IDs dos vídeos (muito mais eficiente em memória)
    print("    Carregando IDs dos vídeos...")
    video_ids = [row[0] for row in session.query(Video.id).all()]
    
    # Carrega IDs dos usuários
    usuario_ids = [row[0] for row in session.query(Usuario.id).all()]
    
    # Para participações, precisamos carregar objetos Video em lotes menores
    print("    Gerando Participações...")
    # Reusa a lógica de seleção de streamers (assumindo que n_streamers está configurado)
    streamer_ids = random.sample(usuario_ids, min(config.n_streamers, len(usuario_ids)))
    
    # Carrega vídeos e streamers em lotes apenas para participações
    FETCH_BATCH = 5_000  # Reduzido para economizar memória
    videos_objs = []
    for i in range(0, len(video_ids), FETCH_BATCH):
        batch_ids = video_ids[i:i+FETCH_BATCH]
        videos_objs.extend(session.query(Video).filter(Video.id.in_(batch_ids)).all())
    
    streamers = []
    for i in range(0, len(streamer_ids), FETCH_BATCH):
        batch_ids = streamer_ids[i:i+FETCH_BATCH]
        streamers.extend(session.query(Usuario).filter(Usuario.id.in_(batch_ids)).all())
    
    # Participações (assinatura: videos, streamers, count - SEM fake)
    participacoes_list = generate_participacoes(videos_objs, streamers, config.n_participacoes)
    session.add_all(participacoes_list)
    session.flush()
    del participacoes_list, videos_objs, streamers
    
    # Comentários (MAIOR VOLUME) com estado
    print("    Gerando Comentários em lotes (pode demorar)...")
    num_seq_state = {}
    
    # Comentários com commits periódicos
    inserted_comments = 0
    batch_size = config.batch_sizes.large
    total_batches = (config.n_comentarios + batch_size - 1) // batch_size
    
    for batch_num in range(1, total_batches + 1):
        current_size = min(batch_size, config.n_comentarios - inserted_comments)
        
        # Amostra IDs de usuários (não precisa carregar objetos completos)
        sample_size = min(current_size, len(usuario_ids))
        sample_usuario_ids = random.sample(usuario_ids, sample_size)
        
        # Gera comentários usando apenas IDs (muito mais eficiente)
        com_batch = generate_comentarios(fake, current_size, video_ids, sample_usuario_ids, num_seq_state)
        session.add_all(com_batch)
        session.flush()
        
        inserted_comments += len(com_batch)
        progress = (inserted_comments / config.n_comentarios) * 100
        print(f"    [{batch_num}/{total_batches}] {progress:.1f}% - {inserted_comments:,}/{config.n_comentarios:,} Comentários", end='\r')
        
        del com_batch
        
        # Commit a cada 5 lotes
        if batch_num % 5 == 0:
            session.commit()
    
    print()
    
    tempo_nivel = time.time() - inicio
    print(f"    ✓ Nível 7 concluído em {tempo_nivel:.2f}s\n")
    
    return tempo_nivel
