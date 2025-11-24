"""Geração de vídeos e participações de streamers."""

from faker import Faker
from models import Video, Participa, Canal, Usuario
import random


def generate_videos(fake: Faker, count: int, canais: list[Canal], offset: int = 0) -> list[Video]:
    """Gera uma lista de vídeos fictícios.
    
    Args:
        offset: Offset para garantir unicidade de títulos entre lotes
    """
    videos: list[Video] = []
    for i in range(count):
        # Adiciona offset + i ao título para garantir unicidade entre lotes
        unique_id = offset + i
        videos.append(
            Video(
                id_canal=random.choice(canais).id,
                titulo=f"{fake.sentence(nb_words=4)} {unique_id}",
                data_h=fake.date_object(),
                tema=fake.word(),
                duracao=fake.time_object(),
                visu_simult=random.randint(0, 10000),
                visu_total=random.randint(10000, 1000000)
            )
        )
    return videos


def generate_participacoes(videos: list[Video], streamers: list[Usuario], count: int) -> list[Participa]:
    """Gera participações de streamers em vídeos."""
    participacoes: list[Participa] = []
    pairs = set()
    max_possible = len(videos) * len(streamers)
    if count > max_possible:
        count = max_possible

    while len(participacoes) < count:
        video = random.choice(videos)
        streamer = random.choice(streamers)
        if (video.id, streamer.id) not in pairs:
            pairs.add((video.id, streamer.id))
            participacoes.append(
                Participa(
                    id_video=video.id,
                    id_streamer=streamer.id
                )
            )
    return participacoes
