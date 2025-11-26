"""
Coordenador principal de população de dados.

Este módulo coordena a execução de todos os níveis de inserção de dados,
gerenciando a hierarquia de dependências e coletando estatísticas de tempo.
"""

import time
from sqlalchemy.orm import Session
from faker import Faker

from ..config import DataConfig
from ..batch_inserter import BatchInserter

from .levels import (
    populate_level_1,
    populate_level_2,
    populate_level_3,
    populate_level_4,
    populate_level_5,
    populate_level_6,
    populate_level_7,
    populate_level_8,
    populate_level_9
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
    
    # Executa cada nível sequencialmente
    print("🚀 Iniciando população do banco de dados...\n")
    
    # Nível 1: Entidades sem dependências
    tempo_nivel1 = populate_level_1(session, fake, config, inserter)
    timings['nivel_1'] = tempo_nivel1
    
    # Nível 2: Dependem de empresas e conversões
    tempo_nivel2 = populate_level_2(session, fake, config, inserter)
    timings['nivel_2'] = tempo_nivel2
    
    # Nível 3: Usuários (CRÍTICO - MAIOR VOLUME)
    tempo_nivel3 = populate_level_3(session, fake, config, inserter)
    timings['nivel_3'] = tempo_nivel3
    
    # Commit intermediário
    inserter.commit_with_timing("commit intermediário (após usuários)")
    
    # Nível 4: Relacionamentos de usuários e canais
    tempo_nivel4 = populate_level_4(session, fake, config, inserter)
    timings['nivel_4'] = tempo_nivel4
    
    # Commit intermediário
    inserter.commit_with_timing("commit intermediário (após canais)")
    
    # Nível 5: Patrocínios e níveis de canal
    tempo_nivel5 = populate_level_5(session, fake, config, inserter)
    timings['nivel_5'] = tempo_nivel5
    
    # Nível 6: Inscrições e vídeos (CRÍTICO)
    tempo_nivel6 = populate_level_6(session, fake, config, inserter)
    timings['nivel_6'] = tempo_nivel6
    
    # Commit intermediário
    inserter.commit_with_timing("commit intermediário (após vídeos)")
    
    # Nível 7: Participações e comentários (MAIS CRÍTICO)
    tempo_nivel7 = populate_level_7(session, fake, config, inserter)
    timings['nivel_7'] = tempo_nivel7
    
    # Commit intermediário
    inserter.commit_with_timing("commit intermediário (após comentários)")
    
    # Nível 8: Doações
    tempo_nivel8 = populate_level_8(session, fake, config, inserter)
    timings['nivel_8'] = tempo_nivel8
    
    # Nível 9: Detalhes de pagamento
    tempo_nivel9 = populate_level_9(session, fake, config, inserter)
    timings['nivel_9'] = tempo_nivel9
    
    # Commit final
    inserter.commit_with_timing("commit final")
    
    timings['total'] = time.time() - inicio_total
    
    print("\n✅ População concluída com sucesso!")
    return timings
