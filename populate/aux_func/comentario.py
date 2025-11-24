"""Geração de comentários em vídeos."""

from faker import Faker
from models import Comentario, Video, Usuario
import random


def generate_comentarios(fake: Faker, count: int, videos: list[Video], usuarios: list[Usuario], num_seq_state: dict = None) -> list[Comentario]:
    """Gera uma lista de comentários fictícios.
    
    Args:
        num_seq_state: Dicionário compartilhado entre lotes para rastrear num_seq por vídeo
    """
    comentarios: list[Comentario] = []
    # Rastreia (id_video, num_seq, id_usuario) para evitar duplicatas
    comentarios_set = set()
    # Rastreia o próximo num_seq disponível por vídeo
    if num_seq_state is None:
        num_seq_por_video = {}
    else:
        num_seq_por_video = num_seq_state
    
    for _ in range(count):
        video = random.choice(videos)
        usuario = random.choice(usuarios)
        
        # Inicializa o contador de num_seq para este vídeo se não existir
        if video.id not in num_seq_por_video:
            num_seq_por_video[video.id] = 1
        
        # Obtém o próximo num_seq para este vídeo
        num_seq = num_seq_por_video[video.id]
        
        # Verifica se esta combinação já existe
        if (video.id, num_seq, usuario.id) not in comentarios_set:
            comentarios_set.add((video.id, num_seq, usuario.id))
            comentarios.append(
                Comentario(
                    id_video=video.id,
                    num_seq=num_seq,
                    id_usuario=usuario.id,
                    texto=fake.text(),
                    data_h=fake.date_time_this_year(),
                    coment_on=fake.boolean()
                )
            )
            # Incrementa o num_seq para o próximo comentário deste vídeo
            num_seq_por_video[video.id] += 1
    
    return comentarios
