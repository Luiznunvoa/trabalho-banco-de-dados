"""Geração de conversões de moeda fictícias."""

from faker import Faker
from models import Conversao


def generate_conversoes(fake: Faker, count: int) -> list[Conversao]:
    """Gera uma lista de conversões de moeda fictícias."""
    conversoes: list[Conversao] = []
    for _ in range(count):
        conversoes.append(
            Conversao(
                moeda=fake.currency_code(),
                fator_conver=fake.pydecimal(left_digits=2, right_digits=8, positive=True)
            )
        )
    return conversoes
