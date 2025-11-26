"""
Nível 3: Usuários (CRÍTICO - MAIOR VOLUME).

Popula usuários que dependem de países.
"""

import time
from sqlalchemy.orm import Session
from faker import Faker

from ...config import DataConfig
from ...batch_inserter import BatchInserter
from models import Pais
from aux_func import generate_usuarios


def populate_level_3(session: Session, fake: Faker, config: DataConfig, inserter: BatchInserter) -> float:
    """
    Popula entidades do nível 3: Usuários.
    
    Args:
        session: Sessão do SQLAlchemy
        fake: Instância do Faker
        config: Configuração de volume de dados
        inserter: Instância do BatchInserter
        
    Returns:
        Tempo de execução em segundos
    """
    print(f"📦 [3/9] Gerando {config.n_usuarios:,} usuários em lotes...")
    inicio = time.time()
    
    paises = session.query(Pais).all()
    inserter.insert_with_offset(
        generate_usuarios, config.n_usuarios, config.batch_sizes.medium,
        "Usuários", paises
    )
    
    tempo_nivel = time.time() - inicio
    print(f"    ✓ Nível 3 concluído em {tempo_nivel:.2f}s\n")
    
    return tempo_nivel
