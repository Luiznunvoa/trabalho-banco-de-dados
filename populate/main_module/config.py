"""
Configurações de volume de dados para população do banco.

Este módulo define presets de configuração para diferentes cenários de teste,
desde desenvolvimento rápido até testes de stress extremos.
"""

import random
from dataclasses import dataclass
from typing import Dict, Any


def suggest(base_value, variation_percent=10):
    """
    Retorna um valor que varia em torno de um valor base.
    Para inteiros, retorna um inteiro. Para floats, retorna um float.
    A variação é de +/- variation_percent.
    """
    if base_value == 0:
        return 0
        
    variation = base_value * (variation_percent / 100.0)
    min_val = base_value - variation
    max_val = base_value + variation
    
    if isinstance(base_value, int):
        min_val = max(1, int(min_val))
        max_val = int(max_val)
        if min_val > max_val:
            return min_val
        return random.randint(min_val, max_val)
    else:  # float
        return random.uniform(min_val, max_val)


@dataclass
class BatchSizes:
    """Tamanhos de lote para diferentes tipos de entidades."""
    tiny: int = 1_000       # Para entidades muito pequenas
    small: int = 5_000      # Para entidades pequenas
    medium: int = 10_000    # Para entidades médias
    large: int = 25_000     # Para entidades grandes
    huge: int = 50_000      # Para relacionamentos simples


@dataclass
class DataConfig:
    """Configuração de volume de dados."""
    
    # Entidades principais (sem valor padrão)
    n_usuarios: int
    n_empresas: int
    n_plataformas: int
    
    # Proporções (sem valor padrão)
    pct_streamers: float
    videos_por_canal: int
    comentarios_por_video: int
    plataformas_por_usuario: float
    inscricoes_por_usuario: float
    participacoes_por_video: float
    niveis_por_canal: int
    patrocinios_por_empresa: int
    
    # Com valores padrão (devem vir por último)
    n_paises: int = 192  # Realista, fixo
    batch_sizes: BatchSizes = None
    preset_name: str = "CUSTOM"
    
    def __post_init__(self):
        """Calcula valores derivados após inicialização."""
        if self.batch_sizes is None:
            self.batch_sizes = BatchSizes()
        
        # Aplica variação aos valores
        self.n_usuarios = suggest(self.n_usuarios)
        self.n_empresas = suggest(self.n_empresas)
        self.n_plataformas = suggest(self.n_plataformas)
        
        self.pct_streamers = suggest(self.pct_streamers)
        self.n_streamers = int(self.n_usuarios * self.pct_streamers)
        
        self.n_canais = self.n_streamers  # 1 canal por streamer
        self.n_videos = self.n_canais * suggest(self.videos_por_canal)
        self.n_comentarios = self.n_videos * suggest(self.comentarios_por_video)
        
        self.n_plataforma_usuarios = int(self.n_usuarios * suggest(self.plataformas_por_usuario))
        self.n_inscricoes = int(self.n_usuarios * suggest(self.inscricoes_por_usuario))
        self.n_participacoes = int(self.n_videos * suggest(self.participacoes_por_video))
        
        self.n_conversoes = self.n_paises  # 1 tipo de moeda por país
        self.n_niveis_totais = self.n_canais * suggest(self.niveis_por_canal)
        self.n_patrocinios = self.n_empresas * suggest(self.patrocinios_por_empresa)
        self.n_streamer_paises = self.n_streamers  # 1 nacionalidade por streamer
        self.n_empresa_paises = self.n_empresas    # 1 país de registro por empresa
        
        # Estimativa de doações (10% dos comentários)
        self.n_doacoes_estimado = int(self.n_comentarios * 0.10)
    
    def get_total_records(self) -> int:
        """Retorna o total estimado de registros."""
        return (
            self.n_usuarios + self.n_empresas + self.n_plataformas + self.n_paises +
            self.n_canais + self.n_videos + self.n_comentarios + self.n_plataforma_usuarios +
            self.n_inscricoes + self.n_participacoes + self.n_patrocinios +
            self.n_niveis_totais + self.n_streamer_paises + self.n_empresa_paises +
            self.n_conversoes + self.n_doacoes_estimado
        )
    
    def get_disk_estimate_gb(self) -> float:
        """Retorna estimativa de espaço em disco em GB."""
        # ~200 bytes por registro em média
        bytes_total = self.get_total_records() * 200
        gb = bytes_total / (1024 ** 3)
        return gb
    
    def get_time_estimate_minutes(self) -> tuple[float, float]:
        """Retorna estimativa de tempo (mín, máx) em minutos."""
        total = self.get_total_records()
        # ~1000-5000 registros por segundo
        min_seconds = total / 5000
        max_seconds = total / 1000
        return (min_seconds / 60, max_seconds / 60)


# ========================================
# PRESETS DE CONFIGURAÇÃO
# ========================================

PRESETS: Dict[str, DataConfig] = {
    "DESENVOLVIMENTO_RAPIDO": DataConfig(
        preset_name="DESENVOLVIMENTO_RAPIDO",
        n_usuarios=10_000,
        n_empresas=500,
        n_plataformas=10,
        pct_streamers=0.15,
        videos_por_canal=10,
        comentarios_por_video=5,
        plataformas_por_usuario=1.5,
        inscricoes_por_usuario=3.0,
        participacoes_por_video=1.2,
        niveis_por_canal=3,
        patrocinios_por_empresa=5,
        batch_sizes=BatchSizes(tiny=500, small=1000, medium=2000, large=5000, huge=10000)
    ),
    
    "TESTE_FUNCIONAL": DataConfig(
        preset_name="TESTE_FUNCIONAL",
        n_usuarios=50_000,
        n_empresas=1_000,
        n_plataformas=12,
        pct_streamers=0.15,
        videos_por_canal=20,
        comentarios_por_video=8,
        plataformas_por_usuario=1.8,
        inscricoes_por_usuario=4.0,
        participacoes_por_video=1.5,
        niveis_por_canal=4,
        patrocinios_por_empresa=8,
        batch_sizes=BatchSizes(tiny=1000, small=2500, medium=5000, large=10000, huge=20000)
    ),
    
    "TESTE_PERFORMANCE": DataConfig(
        preset_name="TESTE_PERFORMANCE",
        n_usuarios=500_000,
        n_empresas=5_000,
        n_plataformas=15,
        pct_streamers=0.15,
        videos_por_canal=50,
        comentarios_por_video=15,
        plataformas_por_usuario=2.0,
        inscricoes_por_usuario=5.0,
        participacoes_por_video=1.8,
        niveis_por_canal=4,
        patrocinios_por_empresa=15,
        batch_sizes=BatchSizes()  # Usa valores padrão
    ),
    
    "TESTE_INDICES": DataConfig(
        preset_name="TESTE_INDICES",
        n_usuarios=800_000,
        n_empresas=8_000,
        n_plataformas=18,
        pct_streamers=0.15,
        videos_por_canal=60,
        comentarios_por_video=20,
        plataformas_por_usuario=2.2,
        inscricoes_por_usuario=6.0,
        participacoes_por_video=2.0,
        niveis_por_canal=5,
        patrocinios_por_empresa=20,
        batch_sizes=BatchSizes()
    ),
    
    "STRESS_TEST_EXTREMO": DataConfig(
        preset_name="STRESS_TEST_EXTREMO",
        n_usuarios=1_000_000,
        n_empresas=10_000,
        n_plataformas=20,
        pct_streamers=0.15,
        videos_por_canal=75,
        comentarios_por_video=25,
        plataformas_por_usuario=2.5,
        inscricoes_por_usuario=7.0,
        participacoes_por_video=2.2,
        niveis_por_canal=6,
        patrocinios_por_empresa=25,
        batch_sizes=BatchSizes()
    )
}


def get_preset(name: str = "TESTE_PERFORMANCE") -> DataConfig:
    """
    Retorna um preset de configuração.
    
    Args:
        name: Nome do preset (padrão: TESTE_PERFORMANCE)
    
    Returns:
        DataConfig com as configurações do preset
    
    Raises:
        KeyError: Se o preset não existir
    """
    if name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise KeyError(f"Preset '{name}' não encontrado. Disponíveis: {available}")
    
    return PRESETS[name]


def list_presets() -> None:
    """Lista todos os presets disponíveis com informações resumidas."""
    print("\n" + "="*80)
    print("PRESETS DE CONFIGURAÇÃO DISPONÍVEIS")
    print("="*80 + "\n")
    
    for name, config in PRESETS.items():
        total = config.get_total_records()
        disk_gb = config.get_disk_estimate_gb()
        time_min, time_max = config.get_time_estimate_minutes()
        
        print(f"📋 {name}")
        print(f"   • Usuários: {config.n_usuarios:,}")
        print(f"   • Total de registros: {total:,}")
        print(f"   • Espaço em disco: ~{disk_gb:.2f} GB (com índices: ~{disk_gb * 1.5:.2f} GB)")
        print(f"   • Tempo estimado: {time_min:.1f}-{time_max:.1f} minutos")
        print()
