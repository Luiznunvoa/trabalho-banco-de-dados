"""
Módulo de estatísticas e relatórios sobre o volume de dados.
"""

from .config import DataConfig


def print_data_statistics(config: DataConfig) -> None:
    """
    Exibe estatísticas detalhadas sobre o volume de dados que será gerado.
    
    Args:
        config: Configuração de dados a ser usada
    """
    print("\n" + "="*80)
    print(f"ESTATÍSTICAS DE VOLUME DE DADOS - {config.preset_name}")
    print("="*80)
    
    print("\n📊 ENTIDADES PRINCIPAIS:")
    print(f"  • Usuários:           {config.n_usuarios:>12,} registros")
    print(f"  • Empresas:           {config.n_empresas:>12,} registros")
    print(f"  • Plataformas:        {config.n_plataformas:>12,} registros")
    print(f"  • Países:             {config.n_paises:>12,} registros")
    print(f"  • Streamers:          {config.n_streamers:>12,} registros ({config.pct_streamers*100:.1f}% dos usuários)")
    
    print("\n📹 CONTEÚDO:")
    print(f"  • Canais:             {config.n_canais:>12,} registros")
    print(f"  • Vídeos:             {config.n_videos:>12,} registros (~{config.n_videos/config.n_canais:.1f} por canal)")
    print(f"  • Comentários:        {config.n_comentarios:>12,} registros (~{config.n_comentarios/config.n_videos:.1f} por vídeo)")
    
    print("\n🔗 RELACIONAMENTOS:")
    print(f"  • Plataforma-Usuário: {config.n_plataforma_usuarios:>12,} registros")
    print(f"  • Inscrições:         {config.n_inscricoes:>12,} registros")
    print(f"  • Participações:      {config.n_participacoes:>12,} registros")
    print(f"  • Patrocínios:        {config.n_patrocinios:>12,} registros")
    print(f"  • Níveis de Canal:    {config.n_niveis_totais:>12,} registros")
    print(f"  • Doações (estimado): {config.n_doacoes_estimado:>12,} registros")
    
    total_registros = config.get_total_records()
    print(f"\n📈 TOTAL ESTIMADO:     {total_registros:>12,} registros")
    
    print("\n💾 ESTIMATIVA DE ESPAÇO EM DISCO:")
    disk_gb = config.get_disk_estimate_gb()
    if disk_gb > 1:
        print(f"  • Tamanho aproximado:  ~{disk_gb:.2f} GB (sem índices)")
        print(f"  • Com índices:         ~{disk_gb * 1.5:.2f} GB")
    else:
        disk_mb = disk_gb * 1024
        print(f"  • Tamanho aproximado:  ~{disk_mb:.0f} MB (sem índices)")
        print(f"  • Com índices:         ~{disk_mb * 1.5:.0f} MB")
    
    print("\n⏱️  TEMPO ESTIMADO DE INSERÇÃO:")
    time_min, time_max = config.get_time_estimate_minutes()
    print(f"  • Mínimo (máquina rápida): ~{time_min:.1f} minutos")
    print(f"  • Máximo (máquina lenta):  ~{time_max:.1f} minutos")
    
    print("\n🚀 OTIMIZAÇÕES ATIVADAS:")
    print("  ✓ Geração em lotes (batch processing)")
    print("  ✓ Liberação agressiva de memória (garbage collection)")
    print("  ✓ Commits intermediários para evitar rollback massivo")
    print("  ✓ Estados compartilhados para garantir unicidade")
    print("  ✓ Amostragem inteligente para reduzir colisões")
    
    print("\n📦 TAMANHOS DE LOTE CONFIGURADOS:")
    bs = config.batch_sizes
    print(f"  • TINY:   {bs.tiny:>8,} (entidades muito pequenas)")
    print(f"  • SMALL:  {bs.small:>8,} (entidades pequenas)")
    print(f"  • MEDIUM: {bs.medium:>8,} (entidades médias)")
    print(f"  • LARGE:  {bs.large:>8,} (entidades grandes)")
    print(f"  • HUGE:   {bs.huge:>8,} (relacionamentos simples)")
    
    if config.preset_name == "TESTE_PERFORMANCE":
        print("\n🎯 OBJETIVOS DE TESTE DE PERFORMANCE:")
        print("  ✓ Testar índices com volume massivo")
        print("  ✓ Avaliar performance de JOINs complexos")
        print("  ✓ Medir tempo de agregações e GROUP BY")
        print("  ✓ Validar planos de execução de queries")
        print("  ✓ Estressar foreign keys e constraints")
    
    print("="*80 + "\n")
