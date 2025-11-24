"""
Configurações Preset para Diferentes Cenários de Teste

Copie e cole as configurações desejadas no arquivo main.py
para substituir as constantes SUGGEST_* existentes.
"""

# ============================================================================
# PRESET 1: DESENVOLVIMENTO RÁPIDO
# Tempo: ~1-2 minutos | Tamanho: ~50MB | Registros: ~100k
# ============================================================================
DESENVOLVIMENTO_RAPIDO = {
    'SUGGEST_N_USUARIOS': 10_000,
    'SUGGEST_N_EMPRESAS': 500,
    'SUGGEST_N_PLATAFORMAS': 5,
    'SUGGEST_PCT_STREAMERS': 0.10,
    'SUGGEST_VIDEOS_POR_CANAL': 3,
    'SUGGEST_COMENTARIOS_POR_VIDEO': 2,
    'SUGGEST_PLATAFORMAS_POR_USUARIO': 1.2,
    'SUGGEST_INSCRICOES_POR_USUARIO': 2.0,
    'SUGGEST_PARTICIPACOES_POR_VIDEO': 1.5,
    'SUGGEST_NIVEIS_POR_CANAL': 2,
    'SUGGEST_PATROCINIOS_POR_EMPRESA': 5
}

# ============================================================================
# PRESET 2: TESTE FUNCIONAL
# Tempo: ~5-10 minutos | Tamanho: ~500MB | Registros: ~1M
# ============================================================================
TESTE_FUNCIONAL = {
    'SUGGEST_N_USUARIOS': 50_000,
    'SUGGEST_N_EMPRESAS': 1_000,
    'SUGGEST_N_PLATAFORMAS': 8,
    'SUGGEST_PCT_STREAMERS': 0.12,
    'SUGGEST_VIDEOS_POR_CANAL': 10,
    'SUGGEST_COMENTARIOS_POR_VIDEO': 5,
    'SUGGEST_PLATAFORMAS_POR_USUARIO': 1.5,
    'SUGGEST_INSCRICOES_POR_USUARIO': 3.0,
    'SUGGEST_PARTICIPACOES_POR_VIDEO': 1.6,
    'SUGGEST_NIVEIS_POR_CANAL': 3,
    'SUGGEST_PATROCINIOS_POR_EMPRESA': 8
}

# ============================================================================
# PRESET 3: TESTE DE PERFORMANCE (ATUAL)
# Tempo: ~15-45 minutos | Tamanho: ~8-12GB | Registros: ~60-70M
# ============================================================================
TESTE_PERFORMANCE = {
    'SUGGEST_N_USUARIOS': 500_000,
    'SUGGEST_N_EMPRESAS': 5_000,
    'SUGGEST_N_PLATAFORMAS': 15,
    'SUGGEST_PCT_STREAMERS': 0.15,
    'SUGGEST_VIDEOS_POR_CANAL': 50,
    'SUGGEST_COMENTARIOS_POR_VIDEO': 15,
    'SUGGEST_PLATAFORMAS_POR_USUARIO': 2.0,
    'SUGGEST_INSCRICOES_POR_USUARIO': 5.0,
    'SUGGEST_PARTICIPACOES_POR_VIDEO': 1.8,
    'SUGGEST_NIVEIS_POR_CANAL': 4,
    'SUGGEST_PATROCINIOS_POR_EMPRESA': 15
}

# ============================================================================
# PRESET 4: STRESS TEST EXTREMO
# Tempo: ~1-3 horas | Tamanho: ~30-50GB | Registros: ~200-300M
# ============================================================================
STRESS_TEST_EXTREMO = {
    'SUGGEST_N_USUARIOS': 1_000_000,
    'SUGGEST_N_EMPRESAS': 10_000,
    'SUGGEST_N_PLATAFORMAS': 20,
    'SUGGEST_PCT_STREAMERS': 0.15,
    'SUGGEST_VIDEOS_POR_CANAL': 100,
    'SUGGEST_COMENTARIOS_POR_VIDEO': 25,
    'SUGGEST_PLATAFORMAS_POR_USUARIO': 2.5,
    'SUGGEST_INSCRICOES_POR_USUARIO': 8.0,
    'SUGGEST_PARTICIPACOES_POR_VIDEO': 2.0,
    'SUGGEST_NIVEIS_POR_CANAL': 5,
    'SUGGEST_PATROCINIOS_POR_EMPRESA': 20
}

# ============================================================================
# PRESET 5: DEMONSTRAÇÃO/APRESENTAÇÃO
# Tempo: ~30 segundos | Tamanho: ~10MB | Registros: ~20k
# ============================================================================
DEMONSTRACAO = {
    'SUGGEST_N_USUARIOS': 2_000,
    'SUGGEST_N_EMPRESAS': 100,
    'SUGGEST_N_PLATAFORMAS': 3,
    'SUGGEST_PCT_STREAMERS': 0.10,
    'SUGGEST_VIDEOS_POR_CANAL': 2,
    'SUGGEST_COMENTARIOS_POR_VIDEO': 3,
    'SUGGEST_PLATAFORMAS_POR_USUARIO': 1.1,
    'SUGGEST_INSCRICOES_POR_USUARIO': 1.5,
    'SUGGEST_PARTICIPACOES_POR_VIDEO': 1.2,
    'SUGGEST_NIVEIS_POR_CANAL': 2,
    'SUGGEST_PATROCINIOS_POR_EMPRESA': 3
}

# ============================================================================
# PRESET 6: TESTE DE ÍNDICES
# Tempo: ~30-60 minutos | Tamanho: ~15-20GB | Registros: ~100-150M
# Foco em volume alto de registros para testar eficiência de índices
# ============================================================================
TESTE_INDICES = {
    'SUGGEST_N_USUARIOS': 800_000,
    'SUGGEST_N_EMPRESAS': 8_000,
    'SUGGEST_N_PLATAFORMAS': 18,
    'SUGGEST_PCT_STREAMERS': 0.12,
    'SUGGEST_VIDEOS_POR_CANAL': 80,
    'SUGGEST_COMENTARIOS_POR_VIDEO': 20,
    'SUGGEST_PLATAFORMAS_POR_USUARIO': 2.2,
    'SUGGEST_INSCRICOES_POR_USUARIO': 6.0,
    'SUGGEST_PARTICIPACOES_POR_VIDEO': 1.9,
    'SUGGEST_NIVEIS_POR_CANAL': 4,
    'SUGGEST_PATROCINIOS_POR_EMPRESA': 18
}

# ============================================================================
# COMO USAR:
# ============================================================================
"""
1. Escolha o preset adequado ao seu cenário
2. Abra o arquivo main.py
3. Localize a seção "CONTROLE DE QUANTIDADE DE DADOS"
4. Substitua os valores das constantes SUGGEST_* pelos valores do preset

Exemplo para usar DESENVOLVIMENTO_RAPIDO:

SUGGEST_N_USUARIOS = 10_000
SUGGEST_N_EMPRESAS = 500
SUGGEST_N_PLATAFORMAS = 5
SUGGEST_PCT_STREAMERS = 0.10
SUGGEST_VIDEOS_POR_CANAL = 3
SUGGEST_COMENTARIOS_POR_VIDEO = 2
SUGGEST_PLATAFORMAS_POR_USUARIO = 1.2
SUGGEST_INSCRICOES_POR_USUARIO = 2.0
SUGGEST_PARTICIPACOES_POR_VIDEO = 1.5
SUGGEST_NIVEIS_POR_CANAL = 2
SUGGEST_PATROCINIOS_POR_EMPRESA = 5
"""

# ============================================================================
# COMPARAÇÃO DE PRESETS
# ============================================================================
"""
Preset                  | Tempo     | Espaço | Registros  | Uso
------------------------|-----------|--------|------------|------------------
DEMONSTRACAO           | 30s       | 10MB   | ~20k       | Apresentações
DESENVOLVIMENTO_RAPIDO | 1-2min    | 50MB   | ~100k      | Dev/Debug
TESTE_FUNCIONAL        | 5-10min   | 500MB  | ~1M        | Testes funcionais
TESTE_PERFORMANCE      | 15-45min  | 8-12GB | ~60-70M    | Performance básica
TESTE_INDICES          | 30-60min  | 15-20GB| ~100-150M  | Otimização índices
STRESS_TEST_EXTREMO    | 1-3h      | 30-50GB| ~200-300M  | Limites do sistema

Recomendações de Hardware:
- DEMONSTRACAO/DEV_RAPIDO: 4GB RAM, qualquer HD
- TESTE_FUNCIONAL: 8GB RAM, SSD recomendado
- TESTE_PERFORMANCE: 16GB RAM, SSD obrigatório
- TESTE_INDICES: 32GB RAM, SSD NVMe
- STRESS_TEST_EXTREMO: 64GB RAM, SSD NVMe, PostgreSQL tunado
"""
