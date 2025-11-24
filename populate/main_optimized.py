#!/usr/bin/env python3
"""
Script principal de população do banco de dados (versão otimizada).

Este script modular orquestra a geração e inserção de dados sintéticos
para testes de performance do banco de dados PostgreSQL.

Uso:
    python main_optimized.py [PRESET]
    
Presets disponíveis:
    - DESENVOLVIMENTO_RAPIDO: ~10k usuários, ~1-2min
    - TESTE_FUNCIONAL: ~50k usuários, ~5-10min
    - TESTE_PERFORMANCE: ~500k usuários, ~15-45min (padrão)
    - TESTE_INDICES: ~800k usuários, ~30-60min
    - STRESS_TEST_EXTREMO: ~1M usuários, ~1-3h

Exemplos:
    python main_optimized.py
    python main_optimized.py DESENVOLVIMENTO_RAPIDO
    python main_optimized.py STRESS_TEST_EXTREMO
    python main_optimized.py --list
"""

import sys
from sqlalchemy.orm import Session
from faker import Faker

from db import conn_db
from main_module.config import get_preset, list_presets
from main_module.statistics import print_data_statistics
from main_module.database_cleaner import clean_database
from main_module.data_population import populate_all_data


def print_timings_summary(timings: dict) -> None:
    """Exibe resumo dos tempos de execução por nível."""
    print("\n" + "="*80)
    print("RESUMO DE TEMPOS DE EXECUÇÃO")
    print("="*80)
    
    for i in range(1, 10):
        key = f'nivel_{i}'
        if key in timings:
            print(f"  Nível {i}: {timings[key]:.2f}s ({timings[key]/60:.1f}min)")
    
    total = timings.get('total', 0)
    print(f"\n  ⏱️  TEMPO TOTAL: {total:.2f}s ({total/60:.2f}min)")
    print("="*80 + "\n")


def main():
    """Função principal do script."""
    
    # Determina qual preset usar
    preset_name = "TESTE_PERFORMANCE"  # Padrão
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h', 'help']:
            print(__doc__)
            list_presets()
            return
        elif sys.argv[1] == '--list':
            list_presets()
            return
        else:
            preset_name = sys.argv[1]
    
    # Carrega configuração
    try:
        config = get_preset(preset_name)
    except KeyError as e:
        print(f"❌ Erro: {e}")
        print("\nUse 'python main_optimized.py --list' para ver os presets disponíveis.")
        return
    
    # Inicialização
    engine = conn_db()
    fake = Faker('pt_BR')
    
    # Exibe estatísticas
    print_data_statistics(config)
    
    # Confirmação do usuário
    resposta = input("Deseja prosseguir com a geração destes dados? (s/n): ")
    if resposta.lower() not in ['s', 'sim', 'y', 'yes']:
        print("Operação cancelada pelo usuário.")
        return
    
    # Limpeza do banco
    try:
        clean_database(engine)
    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")
        return
    
    # População dos dados
    with Session(engine) as session:
        try:
            timings = populate_all_data(session, fake, config)
            
            # Exibe resumo
            print_timings_summary(timings)
            
            print(f"{'='*80}")
            print(f"✅ SUCESSO! Inserção de todos os dados concluída!")
            print(f"⏱️  Tempo total: {timings['total']/60:.2f} minutos ({timings['total']:.1f} segundos)")
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"\n❌ Ocorreu um erro durante a inserção de dados: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()


if __name__ == "__main__":
    main()
