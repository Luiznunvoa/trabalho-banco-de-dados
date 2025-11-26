"""
Nível 2: Dependem de empresas e conversões.

Popula países (que dependem de conversões) e plataformas (que dependem de empresas).
"""

import time
from sqlalchemy.orm import Session
from faker import Faker

from ...config import DataConfig
from ...batch_inserter import BatchInserter
from models import Empresa, Conversao
from aux_func import generate_paises, generate_plataformas


def populate_level_2(session: Session, fake: Faker, config: DataConfig, inserter: BatchInserter) -> float:
    """
    Popula entidades do nível 2: Países e Plataformas.
    
    Args:
        session: Sessão do SQLAlchemy
        fake: Instância do Faker
        config: Configuração de volume de dados
        inserter: Instância do BatchInserter
        
    Returns:
        Tempo de execução em segundos
    """
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
    
    tempo_nivel = time.time() - inicio
    print(f"    ✓ Nível 2 concluído em {tempo_nivel:.2f}s\n")
    
    return tempo_nivel
