"""
Módulo de população de dados do banco de dados.

Este módulo organiza a lógica de geração e inserção de dados em níveis hierárquicos
baseados em suas dependências.

Uso:
    from main_module.data_population import populate_all_data
    
    timings = populate_all_data(session, fake, config)
"""

from .coordinator import populate_all_data

__all__ = ['populate_all_data']
