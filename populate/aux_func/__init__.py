"""
Pacote de funções auxiliares para geração de dados fictícios.

Organizado por domínio/entidade do sistema de streaming.
"""

from .empresa import generate_empresas
from .conversao import generate_conversoes
from .pais import generate_paises
from .plataforma import generate_plataformas, generate_plataforma_usuarios
from .usuario import generate_usuarios
from .streamer import generate_streamer_paises
from .empresa_pais import generate_empresa_paises
from .canal import generate_canais, generate_nivel_canais
from .patrocinio import generate_patrocinios
from .inscricao import generate_inscricoes
from .video import generate_videos, generate_participacoes
from .comentario import generate_comentarios
from .doacao import generate_doacoes, generate_pagamentos

__all__ = [
    'generate_empresas',
    'generate_conversoes',
    'generate_paises',
    'generate_plataformas',
    'generate_plataforma_usuarios',
    'generate_usuarios',
    'generate_streamer_paises',
    'generate_empresa_paises',
    'generate_canais',
    'generate_nivel_canais',
    'generate_patrocinios',
    'generate_inscricoes',
    'generate_videos',
    'generate_participacoes',
    'generate_comentarios',
    'generate_doacoes',
    'generate_pagamentos',
]
