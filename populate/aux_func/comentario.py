"""Geração de comentários em vídeos."""

from faker import Faker
from models import Comentario, Video, Usuario
import random


def generate_comentarios(fake: Faker, count: int, videos: list[Video] | list[int], usuarios: list[Usuario] | list[int], num_seq_state: dict = None) -> list[Comentario]:
    """Gera uma lista de comentários fictícios.
    
    Args:
        fake: Instância do Faker para gerar dados fictícios
        count: Número de comentários a gerar
        videos: Lista de objetos Video OU lista de IDs de vídeos (mais eficiente)
        usuarios: Lista de objetos Usuario OU lista de IDs de usuários (mais eficiente)
        num_seq_state: Dicionário compartilhado entre lotes para rastrear num_seq por vídeo
    
    Returns:
        Lista de objetos Comentario
    """
    comentarios: list[Comentario] = []
    # Rastreia (id_video, num_seq, id_usuario) para evitar duplicatas
    comentarios_set = set()
    # Rastreia o próximo num_seq disponível por vídeo
    if num_seq_state is None:
        num_seq_por_video = {}
    else:
        num_seq_por_video = num_seq_state
    
    # Suporta tanto objetos quanto IDs (otimização de memória)
    for _ in range(count):
        video_item = random.choice(videos)
        usuario_item = random.choice(usuarios)
        
        # Extrai IDs (funciona tanto para objetos quanto para IDs diretos)
        video_id = video_item.id if hasattr(video_item, 'id') else video_item
        usuario_id = usuario_item.id if hasattr(usuario_item, 'id') else usuario_item
        
        # Inicializa o contador de num_seq para este vídeo se não existir
        if video_id not in num_seq_por_video:
            num_seq_por_video[video_id] = 1
        
        # Obtém o próximo num_seq para este vídeo
        num_seq = num_seq_por_video[video_id]
        
        # Verifica se esta combinação já existe
        if (video_id, num_seq, usuario_id) not in comentarios_set:
            comentarios_set.add((video_id, num_seq, usuario_id))
            comentarios.append(
                Comentario(
                    id_video=video_id,
                    num_seq=num_seq,
                    id_usuario=usuario_id,
                    texto=fake.text(),
                    data_h=fake.date_time_this_year(),
                    coment_on=fake.boolean()
                )
            )
            # Incrementa o num_seq para o próximo comentário deste vídeo
            num_seq_por_video[video_id] += 1
    
    return comentarios
