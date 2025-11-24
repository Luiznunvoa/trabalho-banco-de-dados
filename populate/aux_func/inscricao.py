"""Geração de inscrições de usuários em níveis de canal."""

from faker import Faker
from models import Inscricao, NivelCanal, Usuario
import random


def generate_inscricoes(niveis: list[NivelCanal], usuarios: list[Usuario], count: int, pairs_state: set = None) -> list[Inscricao]:
    """Gera inscrições de usuários em níveis de canal.
    
    Args:
        pairs_state: Estado compartilhado para rastrear pares (nivel, usuario) entre lotes
    """
    inscricoes: list[Inscricao] = []
    if pairs_state is None:
        pairs = set()
    else:
        pairs = pairs_state
        
    max_possible = len(niveis) * len(usuarios)
    if count > max_possible:
        count = max_possible

    attempts = 0
    max_attempts = count * 10  # Evita loop infinito
    
    while len(inscricoes) < count and attempts < max_attempts:
        attempts += 1
        nivel = random.choice(niveis)
        usuario = random.choice(usuarios)
        if (nivel.id, usuario.id) not in pairs:
            pairs.add((nivel.id, usuario.id))
            inscricoes.append(
                Inscricao(
                    id_nivel=nivel.id,
                    id_membro=usuario.id
                )
            )
    return inscricoes
