"""Geração de plataformas e relações plataforma-usuário."""

from faker import Faker
from models import Plataforma, Empresa, Usuario, PlataformaUsuario
import random


def generate_plataformas(fake: Faker, count: int, empresas: list[Empresa]) -> list[Plataforma]:
    """Gera uma lista de plataformas fictícias, associando a empresas fundadoras e responsáveis."""
    plataformas: list[Plataforma] = []
    if not empresas:
        raise ValueError("A lista de empresas não pode estar vazia para gerar plataformas.")

    for _ in range(count):
        plataformas.append(
            Plataforma(
                nome=fake.company(),
                data_fund=fake.date_object(),
                empresa_fund=random.choice(empresas).nro,
                empresa_respo=random.choice(empresas).nro
            )
        )
    return plataformas


def generate_plataforma_usuarios(plataformas: list[Plataforma], usuarios: list[Usuario], count: int, 
                                pk_pairs_state: set = None, uk_state: dict = None) -> list[PlataformaUsuario]:
    """Gera relações fictícias entre plataformas e usuários.
    
    Args:
        pk_pairs_state: Estado compartilhado para rastrear pares (plataforma, usuario) entre lotes
        uk_state: Estado compartilhado para rastrear números únicos por plataforma entre lotes
    """
    plataforma_usuarios: list[PlataformaUsuario] = []
    
    # Tracks the PK (platform_nro, user_id) to ensure we don't add the same user to the same platform twice.
    if pk_pairs_state is None:
        pk_pairs = set()
    else:
        pk_pairs = pk_pairs_state
    
    # Tracks the UK (platform_nro, platform_user_number) to satisfy the unique constraint.
    if uk_state is None:
        uk_per_platform = {p.nro: set() for p in plataformas}
    else:
        uk_per_platform = uk_state
        # Garante que todas as plataformas existam no dict
        for p in plataformas:
            if p.nro not in uk_per_platform:
                uk_per_platform[p.nro] = set()

    max_possible_pk_pairs = len(plataformas) * len(usuarios)
    if count > max_possible_pk_pairs:
        count = max_possible_pk_pairs
    
    attempts = 0
    max_attempts = count * 10  # Evita loop infinito
        
    while len(plataforma_usuarios) < count and attempts < max_attempts:
        attempts += 1
        plataforma = random.choice(plataformas)
        usuario = random.choice(usuarios)

        # Check if this user is already on this platform (PK violation)
        if (plataforma.nro, usuario.id) in pk_pairs:
            continue

        # Generate a platform-specific user number that is unique for this platform (UK violation)
        platform_user_num = random.randint(10000000, 99999999)
        max_uk_attempts = 100
        uk_attempts = 0
        while platform_user_num in uk_per_platform[plataforma.nro] and uk_attempts < max_uk_attempts:
            platform_user_num = random.randint(10000000, 99999999)
            uk_attempts += 1
        
        if uk_attempts >= max_uk_attempts:
            continue  # Pula se não conseguir gerar número único
        
        # Add the new keys to the tracking sets
        pk_pairs.add((plataforma.nro, usuario.id))
        uk_per_platform[plataforma.nro].add(platform_user_num)

        plataforma_usuarios.append(
            PlataformaUsuario(
                nro_plataforma=plataforma.nro,
                id_usuario=usuario.id,
                nro_usuario=platform_user_num
            )
        )
    return plataforma_usuarios
