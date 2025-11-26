"""
Nível 4: Relacionamentos de usuários e canais.

Popula PlataformaUsuario, StreamerPais, EmpresaPais e Canais.
"""

import time
import random
from sqlalchemy.orm import Session
from faker import Faker

from ...config import DataConfig
from ...batch_inserter import BatchInserter
from models import Usuario, Plataforma
from aux_func import (
    generate_plataforma_usuarios,
    generate_streamer_paises,
    generate_empresa_paises,
    generate_canais
)


def populate_level_4(session: Session, fake: Faker, config: DataConfig, inserter: BatchInserter) -> float:
    """
    Popula entidades do nível 4: Relacionamentos de usuários e canais.
    
    Args:
        session: Sessão do SQLAlchemy
        fake: Instância do Faker
        config: Configuração de volume de dados
        inserter: Instância do BatchInserter
        
    Returns:
        Tempo de execução em segundos
    """
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
        """Wrapper para adaptar generate_plataforma_usuarios ao formato do BatchInserter."""
        return generate_plataforma_usuarios(
            plataformas_list, sample_usuarios, count,
            state['pk_pairs'], state['uk']
        )
    
    state_pu = {'pk_pairs': pk_pairs_state, 'uk': uk_state}
    inserter.insert_with_state(
        generate_pu_wrapper, config.n_plataforma_usuarios, config.batch_sizes.huge,
        "PlataformaUsuario", state_pu, usuario_ids, sample_size_multiplier=2,
        fetch_model=Usuario
    )
    
    # StreamerPais e EmpresaPais (geradores com assinatura diferente)
    print("    Gerando StreamerPais...")
    from models import Pais, Empresa
    paises = session.query(Pais).all()
    empresas = session.query(Empresa).all()
    
    streamer_paises_list = generate_streamer_paises(fake, streamers, paises, config.n_streamer_paises)
    session.add_all(streamer_paises_list)
    session.flush()
    del streamer_paises_list
    
    print("    Gerando EmpresaPais...")
    empresa_paises_list = generate_empresa_paises(fake, empresas, paises, config.n_empresa_paises)
    session.add_all(empresa_paises_list)
    session.flush()
    del empresa_paises_list
    
    # Canais (gerador sem count - gera 1 por streamer)
    print("    Gerando Canais...")
    canais_list = generate_canais(fake, plataformas_list, streamers)
    session.add_all(canais_list)
    session.flush()
    del canais_list
    
    tempo_nivel = time.time() - inicio
    print(f"    ✓ Nível 4 concluído em {tempo_nivel:.2f}s\n")
    
    return tempo_nivel
