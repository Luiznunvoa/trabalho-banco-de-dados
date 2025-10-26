from faker import Faker
from models import Empresa
from sqlalchemy.orm import Session 

def insert_empresa(fake : Faker, session : Session):
    empresas_a_inserir = [] 
    
    for i in range(10000):
        nome_empresa = fake.unique.company() 
        nome_fantasia_empresa = fake.company_suffix()
        
        empresa = Empresa(
            nome=nome_empresa, 
            nome_fantasia=nome_fantasia_empresa
        )
        
        empresas_a_inserir.append(empresa)

    session.add_all(empresas_a_inserir)
    session.commit()
    print("-> 10.000 empresas inseridas e transação commitada.")
