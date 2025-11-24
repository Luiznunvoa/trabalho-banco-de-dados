"""Geração de relações entre streamers e países (nacionalidades)."""

from faker import Faker
from models import StreamerPais, Usuario, Pais
import random


def generate_streamer_paises(fake: Faker, streamers: list[Usuario], paises: list[Pais], count: int) -> list[StreamerPais]:
    """Gera relações fictícias de nacionalidade para streamers."""
    streamer_paises: list[StreamerPais] = []
    pairs = set()
    max_possible_pairs = len(streamers) * len(paises)
    if count > max_possible_pairs:
        count = max_possible_pairs

    while len(streamer_paises) < count:
        streamer = random.choice(streamers)
        pais = random.choice(paises)
        if (streamer.id, pais.ddi) not in pairs:
            pairs.add((streamer.id, pais.ddi))
            streamer_paises.append(
                StreamerPais(
                    id_usuario=streamer.id,
                    ddi_pais=pais.ddi,
                    nro_passaporte=fake.unique.ssn()
                )
            )
    return streamer_paises
