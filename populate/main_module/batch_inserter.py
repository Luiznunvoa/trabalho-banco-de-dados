"""
Módulo genérico para inserção de dados em lotes.

Este módulo fornece uma classe BatchInserter que abstrai toda a lógica
de inserção em lotes, controle de progresso, garbage collection e commits.
"""

import gc
import time
from typing import Callable, Any, Optional, Dict, List
from sqlalchemy.orm import Session
from faker import Faker


class BatchInserter:
    """
    Classe para gerenciar inserções em lotes de forma genérica e eficiente.
    
    Características:
    - Inserção em lotes com tamanho configurável
    - Controle de progresso com impressão em tempo real
    - Garbage collection automático entre lotes
    - Commits intermediários configuráveis
    - Suporte a offset para garantir unicidade
    - Suporte a estados compartilhados entre lotes
    """
    
    def __init__(self, session: Session, fake: Faker):
        """
        Inicializa o BatchInserter.
        
        Args:
            session: Sessão do SQLAlchemy
            fake: Instância do Faker para geração de dados
        """
        self.session = session
        self.fake = fake
    
    def insert_simple(
        self,
        generator_func: Callable,
        total_count: int,
        batch_size: int,
        entity_name: str,
        *args,
        **kwargs
    ) -> float:
        """
        Insere dados simples em lotes (sem offset, sem estados complexos).
        
        Args:
            generator_func: Função que gera os dados (fake, count, *args, **kwargs)
            total_count: Total de registros a inserir
            batch_size: Tamanho de cada lote
            entity_name: Nome da entidade (para logging)
            *args: Argumentos posicionais para a função geradora
            **kwargs: Argumentos nomeados para a função geradora
            
        Returns:
            Tempo total de execução em segundos
        """
        inicio = time.time()
        inserted = 0
        total_batches = (total_count + batch_size - 1) // batch_size
        
        for batch_num in range(1, total_batches + 1):
            current_size = min(batch_size, total_count - inserted)
            
            # Gera o lote
            batch_data = generator_func(self.fake, current_size, *args, **kwargs)
            
            # Insere no banco
            self.session.add_all(batch_data)
            self.session.flush()
            
            inserted += len(batch_data)
            progress = (inserted / total_count) * 100
            print(f"    [{batch_num}/{total_batches}] {progress:.1f}% - {inserted:,}/{total_count:,} {entity_name}", end='\r')
            
            # Limpa memória
            del batch_data
            gc.collect()
        
        print()  # Nova linha após progresso
        return time.time() - inicio
    
    def insert_with_offset(
        self,
        generator_func: Callable,
        total_count: int,
        batch_size: int,
        entity_name: str,
        *args,
        **kwargs
    ) -> float:
        """
        Insere dados em lotes com offset incremental (garante unicidade).
        
        Args:
            generator_func: Função que gera os dados (fake, count, *args, offset, **kwargs)
            total_count: Total de registros a inserir
            batch_size: Tamanho de cada lote
            entity_name: Nome da entidade (para logging)
            *args: Argumentos posicionais para a função geradora
            **kwargs: Argumentos nomeados para a função geradora
            
        Returns:
            Tempo total de execução em segundos
        """
        inicio = time.time()
        inserted = 0
        offset = 0
        total_batches = (total_count + batch_size - 1) // batch_size
        
        for batch_num in range(1, total_batches + 1):
            current_size = min(batch_size, total_count - inserted)
            
            # Gera o lote com offset
            batch_data = generator_func(self.fake, current_size, *args, offset, **kwargs)
            
            # Insere no banco
            self.session.add_all(batch_data)
            self.session.flush()
            
            inserted += len(batch_data)
            offset += current_size
            progress = (inserted / total_count) * 100
            print(f"    [{batch_num}/{total_batches}] {progress:.1f}% - {inserted:,}/{total_count:,} {entity_name}", end='\r')
            
            # Limpa memória
            del batch_data
            gc.collect()
        
        print()
        return time.time() - inicio
    
    def insert_with_state(
        self,
        generator_func: Callable,
        total_count: int,
        batch_size: int,
        entity_name: str,
        state: Dict[str, Any],
        sample_data: List[Any],
        sample_size_multiplier: int = 2,
        *args,
        **kwargs
    ) -> float:
        """
        Insere dados em lotes com estado compartilhado (para relacionamentos complexos).
        
        Args:
            generator_func: Função que gera os dados (sample, count, state, *args, **kwargs)
            total_count: Total de registros a inserir
            batch_size: Tamanho de cada lote
            entity_name: Nome da entidade (para logging)
            state: Dicionário de estado compartilhado entre lotes
            sample_data: Lista de IDs ou objetos para amostrar
            sample_size_multiplier: Multiplicador do tamanho da amostra (padrão: 2x)
            *args: Argumentos posicionais para a função geradora
            **kwargs: Argumentos nomeados para a função geradora
            
        Returns:
            Tempo total de execução em segundos
        """
        inicio = time.time()
        inserted = 0
        total_batches = (total_count + batch_size - 1) // batch_size
        
        for batch_num in range(1, total_batches + 1):
            current_size = min(batch_size, total_count - inserted)
            
            # Amostra dados para este lote
            import random
            sample_size = min(current_size * sample_size_multiplier, len(sample_data))
            sample = random.sample(sample_data, sample_size)
            
            # Gera o lote com estado
            batch_data = generator_func(sample, current_size, state, *args, **kwargs)
            
            # Insere no banco
            self.session.add_all(batch_data)
            self.session.flush()
            
            inserted += len(batch_data)
            progress = (inserted / total_count) * 100
            print(f"    [{batch_num}/{total_batches}] {progress:.1f}% - {inserted:,}/{total_count:,} {entity_name}", end='\r')
            
            # Limpa memória
            del batch_data, sample
            gc.collect()
        
        print()
        return time.time() - inicio
    
    def commit_with_timing(self, label: str = "Commit") -> float:
        """
        Executa commit com medição de tempo.
        
        Args:
            label: Label para o log
            
        Returns:
            Tempo de execução do commit
        """
        print(f"    💾 Realizando {label}...")
        inicio = time.time()
        self.session.commit()
        tempo = time.time() - inicio
        print(f"    ✓ {label} concluído em {tempo:.2f}s")
        gc.collect()
        return tempo
