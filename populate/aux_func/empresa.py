"""Geração de empresas fictícias."""

from faker import Faker
from models import Empresa


def generate_empresas(fake: Faker, count: int) -> list[Empresa]:
    """Gera uma lista de empresas fictícias."""
    empresas: list[Empresa] = [] 
    for _ in range(count):
        empresas.append(
            Empresa(
                nome=fake.company(), 
                nome_fantasia=fake.company_suffix()
            )
        )
    return empresas
