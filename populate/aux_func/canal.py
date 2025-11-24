"""Geração de canais e níveis de canal."""

from faker import Faker
from models import Canal, NivelCanal, Plataforma, Usuario, TipoCanal
import random


def generate_canais(fake: Faker, plataformas: list[Plataforma], streamers: list[Usuario]) -> list[Canal]:
    """Gera um canal para cada streamer, garantindo nomes de canal únicos por plataforma."""
    canais: list[Canal] = []
    for streamer in streamers:
        # Create a unique channel name from the streamer's unique nick
        channel_name = f"{streamer.nick}_canal"

        canais.append(
            Canal(
                nro_plataforma=random.choice(plataformas).nro,
                id_streamer=streamer.id,
                nome=channel_name,
                tipo=random.choice(list(TipoCanal)),
                data_criacao=fake.date_object(),
                descricao=fake.sentence(),
                qtd_visualizacoes=random.randint(0, 1000000)
            )
        )
    return canais


def generate_nivel_canais(fake: Faker, canais: list[Canal], niveis_por_canal: int) -> list[NivelCanal]:
    """Gera níveis de inscrição para canais."""
    nivel_canais: list[NivelCanal] = []
    for canal in canais:
        for i in range(niveis_por_canal):
            nivel_canais.append(
                NivelCanal(
                    id_canal=canal.id,
                    nivel=f"Nivel {i+1}",
                    valor=fake.pydecimal(left_digits=3, right_digits=2, positive=True),
                    gif=fake.image_url()
                )
            )
    return nivel_canais
