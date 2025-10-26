from db import conn_db, select_db, insert_db
from faker import Faker
from models import Empresa, Base 
from sqlalchemy.orm import Session 
from aux_func import generate_empresas

def main():
    engine = conn_db()
    fake = Faker('pt_BR') 
    
    try:
        print("Criando tabelas no banco de dados...")

        Base.metadata.create_all(engine)

        print("Tabelas verificadas/criadas com sucesso.")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        return
        
    print("⏳ Inserindo 10.000 registros na tabela 'empresa' (Bulk Insert)...")
    
    with Session(engine) as session:
        insert_db(session, generate_empresas(fake, 10000))

    print("Inserção concluída!")
    
    df = select_db(schema = "teste_parrini", tabela = "empresa", engine = engine)

    print("\nPrimeiras 5 linhas inseridas:")
    print(len(df))

if __name__ == "__main__":
    main()
