"""
Nível 9: Detalhes de pagamento.

Popula os diferentes tipos de pagamento (Bitcoin, Cartao, PayPal, MecanismoPlataforma).
"""

import time
from sqlalchemy.orm import Session
from faker import Faker

from ...config import DataConfig
from ...batch_inserter import BatchInserter
from models import Doacao
from aux_func import generate_pagamentos


def populate_level_9(session: Session, fake: Faker, config: DataConfig, inserter: BatchInserter) -> float:
    """
    Popula entidades do nível 9: Detalhes de Pagamento.
    
    Args:
        session: Sessão do SQLAlchemy
        fake: Instância do Faker
        config: Configuração de volume de dados
        inserter: Instância do BatchInserter
        
    Returns:
        Tempo de execução em segundos
    """
    print("📦 [9/9] Gerando detalhes de pagamento...")
    inicio = time.time()
    
    doacoes = session.query(Doacao).all()
    bitcoins, cartoes, paypals, mec_plats = generate_pagamentos(fake, doacoes)
    
    session.add_all(bitcoins + cartoes + paypals + mec_plats)
    session.flush()
    
    tempo_nivel = time.time() - inicio
    print(f"    ✓ Nível 9 concluído em {tempo_nivel:.2f}s\n")
    
    return tempo_nivel
