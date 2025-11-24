"""
Main Module - Módulo principal de população do banco de dados

Este pacote contém a lógica modularizada para popular o banco de dados
com dados sintéticos para testes de performance.

Estrutura:
- config.py: Configurações e presets de volume de dados
- statistics.py: Estatísticas e relatórios sobre os dados
- database_cleaner.py: Limpeza e reset do banco de dados
- batch_inserter.py: Funções genéricas para inserção em lotes
- data_population.py: Lógica de população organizada por níveis
"""

from .config import DataConfig
from .statistics import print_data_statistics
from .database_cleaner import clean_database
from .batch_inserter import BatchInserter
from .data_population import populate_all_data

__all__ = [
    'DataConfig',
    'print_data_statistics',
    'clean_database',
    'BatchInserter',
    'populate_all_data'
]
