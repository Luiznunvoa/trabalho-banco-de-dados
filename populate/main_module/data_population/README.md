# Módulo Data Population

Este módulo organiza a lógica de população de dados do banco de dados em uma estrutura modular e hierárquica.

## Estrutura

```
data_population/
├── __init__.py           # Exporta populate_all_data
├── coordinator.py        # Coordena a execução de todos os níveis
└── levels/               # Módulos de cada nível de inserção
    ├── __init__.py
    ├── level_1.py        # Empresas e Conversões (sem dependências)
    ├── level_2.py        # Países e Plataformas
    ├── level_3.py        # Usuários
    ├── level_4.py        # Relacionamentos de usuários e Canais
    ├── level_5.py        # Patrocínios e Níveis de Canal
    ├── level_6.py        # Inscrições e Vídeos
    ├── level_7.py        # Participações e Comentários
    ├── level_8.py        # Doações
    └── level_9.py        # Detalhes de Pagamento
```

## Hierarquia de Dependências

```
Nível 1 (sem dependências)
├── Empresa
└── Conversao

Nível 2
├── Pais (← Conversao)
└── Plataforma (← Empresa)

Nível 3
└── Usuario (← Pais)

Nível 4
├── PlataformaUsuario (← Plataforma, Usuario)
├── StreamerPais (← Usuario[streamer], Pais)
├── EmpresaPais (← Empresa, Pais)
└── Canal (← Plataforma, Usuario[streamer])

Nível 5
├── Patrocinio (← Empresa, Canal)
└── NivelCanal (← Canal)

Nível 6
├── Inscricao (← NivelCanal, Usuario)
└── Video (← Canal)

Nível 7
├── Participacao (← Video, Usuario[streamer])
└── Comentario (← Video, Usuario)

Nível 8
└── Doacao (← Comentario)

Nível 9 (detalhes de pagamento)
├── Bitcoin (← Doacao)
├── Cartao (← Doacao)
├── PayPal (← Doacao)
└── MecanismoPlataforma (← Doacao)
```

## Uso

```python
from main_module.data_population import populate_all_data

# Popula o banco de dados
timings = populate_all_data(session, fake, config)

# Retorna um dicionário com tempos de execução:
# {
#     'nivel_1': 1.23,
#     'nivel_2': 2.45,
#     ...
#     'total': 150.67
# }
```

## Vantagens da Estrutura Modular

1. **Organização**: Cada nível de inserção está em seu próprio arquivo
2. **Manutenibilidade**: Fácil localizar e modificar lógica específica
3. **Testabilidade**: Possível testar cada nível independentemente
4. **Clareza**: A hierarquia de dependências fica explícita
5. **Escalabilidade**: Adicionar novos níveis é simples e direto

## Commits Intermediários

O coordenador realiza commits intermediários estratégicos:
- Após Nível 3 (usuários)
- Após Nível 4 (canais)
- Após Nível 6 (vídeos)
- Após Nível 7 (comentários)
- Commit final após Nível 9

## Performance

Cada módulo de nível:
- Usa o `BatchInserter` para inserções eficientes
- Gerencia memória com `del` após grandes inserções
- Retorna o tempo de execução para métricas
- Exibe progresso com mensagens informativas
