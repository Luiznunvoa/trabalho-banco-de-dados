"""Geração de patrocínios entre empresas e canais."""

from faker import Faker
from models import Patrocinio, Empresa, Canal
import random


def generate_patrocinios(fake: Faker, empresas: list[Empresa], canais: list[Canal], count: int) -> list[Patrocinio]:
    """Gera patrocínios fictícios entre empresas e canais."""
    patrocinios: list[Patrocinio] = []
    pairs = set()
    max_possible = len(empresas) * len(canais)
    if count > max_possible:
        count = max_possible

    while len(patrocinios) < count:
        empresa = random.choice(empresas)
        canal = random.choice(canais)
        if (empresa.nro, canal.id) not in pairs:
            pairs.add((empresa.nro, canal.id))
            patrocinios.append(
                Patrocinio(
                    nro_empresa=empresa.nro,
                    id_canal=canal.id,
                    valor=fake.pydecimal(left_digits=8, right_digits=2, positive=True)
                )
            )
    return patrocinios
