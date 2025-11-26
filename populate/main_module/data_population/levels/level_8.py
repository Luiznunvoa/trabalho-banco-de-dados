"""
Nível 8: Doações.

Popula Doacoes que dependem de Comentarios.
"""

import time
from sqlalchemy.orm import Session
from faker import Faker

from ...config import DataConfig
from ...batch_inserter import BatchInserter
from models import Comentario
from aux_func import generate_doacoes


def populate_level_8(session: Session, fake: Faker, config: DataConfig, inserter: BatchInserter) -> float:
    """
    Popula entidades do nível 8: Doações.
    
    Args:
        session: Sessão do SQLAlchemy
        fake: Instância do Faker
        config: Configuração de volume de dados
        inserter: Instância do BatchInserter
        
    Returns:
        Tempo de execução em segundos
    """
    print("📦 [8/9] Gerando doações...")
    inicio = time.time()
    
    # Busca comentários para gerar doações (assinatura: fake, comentarios - sem count)
    comentarios_list = session.query(Comentario).limit(config.n_comentarios).all()
    doacoes_list = generate_doacoes(fake, comentarios_list)
    session.add_all(doacoes_list)
    session.flush()
    del comentarios_list
    
    tempo_nivel = time.time() - inicio
    print(f"    ✓ Nível 8 concluído em {tempo_nivel:.2f}s\n")
    
    return tempo_nivel
