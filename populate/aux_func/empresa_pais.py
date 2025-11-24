"""Geração de relações entre empresas e países."""

from faker import Faker
from models import EmpresaPais, Empresa, Pais
import random


def generate_empresa_paises(fake: Faker, empresas: list[Empresa], paises: list[Pais], count: int) -> list[EmpresaPais]:
    """Gera relações fictícias entre empresas e países."""
    empresa_paises: list[EmpresaPais] = []
    pairs = set()
    max_possible = len(empresas) * len(paises)
    if count > max_possible:
        count = max_possible
    
    while len(empresa_paises) < count:
        empresa = random.choice(empresas)
        pais = random.choice(paises)
        if (empresa.nro, pais.ddi) not in pairs:
            pairs.add((empresa.nro, pais.ddi))
            empresa_paises.append(
                EmpresaPais(
                    nro_empresa=empresa.nro,
                    ddi_pais=pais.ddi,
                    id_nacional=fake.unique.bban()
                )
            )
    return empresa_paises
