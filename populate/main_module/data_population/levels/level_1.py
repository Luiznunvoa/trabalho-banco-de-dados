"""
Nível 1: Entidades sem dependências.

Popula empresas e conversões que não dependem de outras entidades.
"""

import time
from sqlalchemy.orm import Session
from faker import Faker

from ...config import DataConfig
from ...batch_inserter import BatchInserter
from aux_func import generate_empresas, generate_conversoes


def populate_level_1(session: Session, fake: Faker, config: DataConfig, inserter: BatchInserter) -> float:
    """
    Popula entidades do nível 1: Empresas e Conversões.
    
    Args:
        session: Sessão do SQLAlchemy
        fake: Instância do Faker
        config: Configuração de volume de dados
        inserter: Instância do BatchInserter
        
    Returns:
        Tempo de execução em segundos
    """
    print("📦 [1/9] Gerando empresas e conversões...")
    inicio = time.time()
    
    # Empresas
    inserter.insert_simple(
        generate_empresas, config.n_empresas, config.batch_sizes.small,
        "Empresas"
    )
    
    # Conversões
    inserter.insert_simple(
        generate_conversoes, config.n_conversoes, config.batch_sizes.tiny,
        "Conversões"
    )
    
    tempo_nivel = time.time() - inicio
    print(f"    ✓ Nível 1 concluído em {tempo_nivel:.2f}s\n")
    
    return tempo_nivel
