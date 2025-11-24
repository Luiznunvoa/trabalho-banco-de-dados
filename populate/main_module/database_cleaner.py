"""
Módulo responsável pela limpeza e reset do banco de dados.
"""

from sqlalchemy import text
from sqlalchemy.engine import Engine


def clean_database(engine: Engine) -> None:
    """
    Limpa todos os dados das tabelas do schema 'core' mantendo a estrutura.
    Usa TRUNCATE com RESTART IDENTITY CASCADE para garantir que:
    - Todos os dados sejam removidos
    - Sequências de autoincremento sejam resetadas
    - Foreign keys sejam respeitadas pela ordem de CASCADE
    
    Args:
        engine: Engine do SQLAlchemy conectada ao banco
        
    Raises:
        Exception: Se houver erro durante a limpeza
    """
    print("\n🧹 Limpando dados existentes nas tabelas...")
    
    truncate_script = """
    SET SEARCH_PATH TO core;
    
    TRUNCATE TABLE 
        MecPlat, 
        Paypal, 
        CartaoCredito, 
        Bitcoin, 
        Doacao, 
        Comentario, 
        Participa, 
        Video, 
        Inscricao, 
        NivelCanal, 
        Patrocinio, 
        Canal, 
        EmpresaPais, 
        StreamerPais, 
        PlataformaUsuario, 
        Usuario, 
        Plataforma, 
        Pais, 
        Conversao, 
        Empresa 
    RESTART IDENTITY CASCADE;
    """
    
    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text(truncate_script))
        
        print("✅ Dados removidos com sucesso. Schema mantido.\n")
        
    except Exception as e:
        print(f"❌ Erro ao limpar dados: {e}")
        raise
