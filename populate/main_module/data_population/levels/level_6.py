"""
Nível 6: Inscrições e vídeos (CRÍTICO).

Popula Inscricoes (que dependem de NivelCanal e Usuario) e Videos (que dependem de Canal).
"""

import time
import random
from sqlalchemy.orm import Session
from faker import Faker

from ...config import DataConfig
from ...batch_inserter import BatchInserter
from models import Usuario, NivelCanal, Canal
from aux_func import generate_inscricoes, generate_videos


def populate_level_6(session: Session, fake: Faker, config: DataConfig, inserter: BatchInserter) -> float:
    """
    Popula entidades do nível 6: Inscrições e Vídeos.
    
    Args:
        session: Sessão do SQLAlchemy
        fake: Instância do Faker
        config: Configuração de volume de dados
        inserter: Instância do BatchInserter
        
    Returns:
        Tempo de execução em segundos
    """
    print(f"📦 [6/9] Gerando {config.n_inscricoes:,} inscrições e {config.n_videos:,} vídeos...")
    inicio = time.time()
    
    # Busca níveis de canal
    nivel_canais = session.query(NivelCanal).all()
    
    # Inscrições com estado
    print("    Gerando Inscrições...")
    inscricoes_pairs_state = set()
    usuario_ids = [row[0] for row in session.query(Usuario.id).all()]
    
    def generate_insc_wrapper(sample_usuarios, count, state):
        """Wrapper para adaptar generate_inscricoes."""
        return generate_inscricoes(nivel_canais, sample_usuarios, count, state['pairs'])
    
    state_insc = {'pairs': inscricoes_pairs_state}
    inserter.insert_with_state(
        generate_insc_wrapper, config.n_inscricoes, config.batch_sizes.huge,
        "Inscrições", state_insc, usuario_ids, sample_size_multiplier=2,
        fetch_model=Usuario
    )
    
    # Vídeos com offset
    print("    Gerando Vídeos...")
    canais = session.query(Canal).all()
    inserter.insert_with_offset(
        generate_videos, config.n_videos, config.batch_sizes.large,
        "Vídeos", canais
    )
    
    tempo_nivel = time.time() - inicio
    print(f"    ✓ Nível 6 concluído em {tempo_nivel:.2f}s\n")
    
    return tempo_nivel
