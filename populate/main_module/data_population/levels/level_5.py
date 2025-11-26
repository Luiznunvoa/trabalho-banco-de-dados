"""
Nível 5: Patrocínios e níveis de canal.

Popula Patrocinios e NivelCanal que dependem de canais e empresas.
"""

import time
from sqlalchemy.orm import Session
from faker import Faker

from ...config import DataConfig
from ...batch_inserter import BatchInserter
from models import Canal, Empresa
from aux_func import generate_patrocinios, generate_nivel_canais


def populate_level_5(session: Session, fake: Faker, config: DataConfig, inserter: BatchInserter) -> float:
    """
    Popula entidades do nível 5: Patrocínios e Níveis de Canal.
    
    Args:
        session: Sessão do SQLAlchemy
        fake: Instância do Faker
        config: Configuração de volume de dados
        inserter: Instância do BatchInserter
        
    Returns:
        Tempo de execução em segundos
    """
    print(f"📦 [5/9] Gerando {config.n_patrocinios:,} patrocínios e níveis de canal...")
    inicio = time.time()
    
    # Busca os canais criados
    canais = session.query(Canal).all()
    empresas = session.query(Empresa).all()
    
    # Patrocínios (assinatura: fake, empresas, canais, count)
    patrocinios_list = generate_patrocinios(fake, empresas, canais, config.n_patrocinios)
    session.add_all(patrocinios_list)
    session.flush()
    del patrocinios_list
    
    # Níveis de Canal (assinatura: fake, canais, niveis_por_canal)
    nivel_canais_list = generate_nivel_canais(fake, canais, config.niveis_por_canal)
    session.add_all(nivel_canais_list)
    session.flush()
    del nivel_canais_list
    
    tempo_nivel = time.time() - inicio
    print(f"    ✓ Nível 5 concluído em {tempo_nivel:.2f}s\n")
    
    return tempo_nivel
