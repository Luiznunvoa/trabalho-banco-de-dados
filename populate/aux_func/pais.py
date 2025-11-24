"""Geração de países fictícios."""

from faker import Faker
from models import Pais, Conversao
import random


def generate_paises(fake: Faker, count: int, conversoes: list[Conversao]) -> list[Pais]:
    """Gera uma lista de países fictícios, garantindo DDIs únicos."""
    paises: list[Pais] = []
    ddis_gerados = set()
    if not conversoes:
        raise ValueError("A lista de conversões não pode estar vazia para gerar países.")

    while len(paises) < count:
        try:
            ddi = int(fake.country_calling_code().replace('+', '').replace(' ', ''))
            if ddi not in ddis_gerados:
                ddis_gerados.add(ddi)
                paises.append(
                    Pais(
                        ddi=ddi,
                        nome=fake.country(),
                        id_moeda=random.choice(conversoes).id
                    )
                )
        except ValueError:
            # Ignora códigos que não podem ser convertidos para int, se houver algum.
            continue
    return paises
