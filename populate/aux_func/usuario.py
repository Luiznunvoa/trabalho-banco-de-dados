"""Geração de usuários fictícios."""

from faker import Faker
from models import Usuario, Pais
import random


def generate_usuarios(fake: Faker, count: int, paises: list[Pais], offset: int = 0) -> list[Usuario]:
    """Gera uma lista de usuários fictícios.
    
    Args:
        fake: Instância do Faker
        count: Quantidade de usuários a gerar
        paises: Lista de países disponíveis
        offset: Offset para garantir unicidade de nick/email entre lotes
    """
    usuarios: list[Usuario] = []
    for i in range(count):
        # Manually ensure uniqueness for nick and email to support large quantities,
        # as fake.unique can exhaust its pool of values.
        # Usa offset + i para garantir unicidade entre lotes
        unique_id = offset + i
        user_name_base = fake.user_name()
        unique_nick = f"{user_name_base}{unique_id}"
        unique_email = f"{user_name_base.replace(' ', '_')}{unique_id}@{fake.free_email_domain()}"

        usuarios.append(
            Usuario(
                nick=unique_nick,
                email=unique_email,
                data_nasc=fake.date_of_birth(minimum_age=13, maximum_age=80),
                telefone=fake.phone_number(),
                pais_residencia=random.choice(paises).ddi if paises else None,
                end_postal=fake.postcode()
            )
        )
    return usuarios
