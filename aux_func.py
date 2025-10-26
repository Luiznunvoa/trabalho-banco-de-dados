from faker import Faker
from models import Empresa

def generate_empresas(fake : Faker, count: int) -> list[Empresa]:
    empresas = [] 
    
    for _ in range(count):
        empresas.append(
            Empresa(
                nome=fake.unique.company(), 
                nome_fantasia=fake.company_suffix()
            )
        )

    return empresas 
