from faker import Faker
from models import (
    Empresa, Conversao, Pais, Plataforma, Usuario, PlataformaUsuario, 
    StreamerPais, EmpresaPais, Canal, Patrocinio, NivelCanal, Inscricao, 
    Video, Participa, Comentario, Doacao, Bitcoin, CartaoCredito, Paypal, 
    MecPlat, TipoCanal, StatusPagamento
)
import random

def generate_empresas(fake: Faker, count: int) -> list[Empresa]:
    """Gera uma lista de empresas fictícias."""
    empresas: list[Empresa] = [] 
    for _ in range(count):
        empresas.append(
            Empresa(
                nome=fake.company(), 
                nome_fantasia=fake.company_suffix()
            )
        )
    return empresas 

def generate_conversoes(fake: Faker, count: int) -> list[Conversao]:
    """Gera uma lista de conversões de moeda fictícias."""
    conversoes: list[Conversao] = []
    for _ in range(count):
        conversoes.append(
            Conversao(
                moeda=fake.currency_code(),
                fator_conver=fake.pydecimal(left_digits=2, right_digits=8, positive=True)
            )
        )
    return conversoes

def generate_paises(fake: Faker, count: int, conversoes: list[Conversao]) -> list[Pais]:
    """Gera uma lista de países fictícios, associando a uma moeda."""
    paises: list[Pais] = []
    if not conversoes:
        raise ValueError("A lista de conversões não pode estar vazia para gerar países.")
    
    for _ in range(count):
        paises.append(
            Pais(
                ddi=int(fake.unique.country_calling_code().replace('+', '').replace(' ', '')),
                nome=fake.country(),
                id_moeda=random.choice(conversoes).id
            )
        )
    return paises

def generate_plataformas(fake: Faker, count: int, empresas: list[Empresa]) -> list[Plataforma]:
    """Gera uma lista de plataformas fictícias, associando a empresas fundadoras e responsáveis."""
    plataformas: list[Plataforma] = []
    if not empresas:
        raise ValueError("A lista de empresas não pode estar vazia para gerar plataformas.")

    for _ in range(count):
        plataformas.append(
            Plataforma(
                nome=fake.company(),
                data_fund=fake.date_object(),
                empresa_fund=random.choice(empresas).nro,
                empresa_respo=random.choice(empresas).nro
            )
        )
    return plataformas

def generate_usuarios(fake: Faker, count: int, paises: list[Pais]) -> list[Usuario]:
    """Gera uma lista de usuários fictícios."""
    usuarios: list[Usuario] = []
    for i in range(count):
        # Manually ensure uniqueness for nick and email to support large quantities,
        # as fake.unique can exhaust its pool of values.
        user_name_base = fake.user_name()
        unique_nick = f"{user_name_base}{i}"
        unique_email = f"{user_name_base.replace(' ', '_')}{i}@{fake.free_email_domain()}"

        usuarios.append(
            Usuario(
                nick=unique_nick,
                email=unique_email,
                data_nasc=fake.date_of_birth(minimum_age=13, maximum_age=80),
                telefone=fake.phone_number(),
                pais_residencia=random.choice(paises).ddi if paises else None,
                end_postal=fake.postcode()
            )
        )
    return usuarios

def generate_plataforma_usuarios(plataformas: list[Plataforma], usuarios: list[Usuario], count: int) -> list[PlataformaUsuario]:
    """Gera relações fictícias entre plataformas e usuários."""
    plataforma_usuarios: list[PlataformaUsuario] = []
    
    # Tracks the PK (platform_nro, user_id) to ensure we don't add the same user to the same platform twice.
    pk_pairs = set()
    
    # Tracks the UK (platform_nro, platform_user_number) to satisfy the unique constraint.
    uk_per_platform = {p.nro: set() for p in plataformas}

    max_possible_pk_pairs = len(plataformas) * len(usuarios)
    if count > max_possible_pk_pairs:
        count = max_possible_pk_pairs
        
    while len(plataforma_usuarios) < count:
        plataforma = random.choice(plataformas)
        usuario = random.choice(usuarios)

        # Check if this user is already on this platform (PK violation)
        if (plataforma.nro, usuario.id) in pk_pairs:
            continue

        # Generate a platform-specific user number that is unique for this platform (UK violation)
        platform_user_num = random.randint(10000000, 99999999)
        while platform_user_num in uk_per_platform[plataforma.nro]:
            platform_user_num = random.randint(10000000, 99999999)
        
        # Add the new keys to the tracking sets
        pk_pairs.add((plataforma.nro, usuario.id))
        uk_per_platform[plataforma.nro].add(platform_user_num)

        plataforma_usuarios.append(
            PlataformaUsuario(
                nro_plataforma=plataforma.nro,
                id_usuario=usuario.id,
                nro_usuario=platform_user_num
            )
        )
    return plataforma_usuarios

def generate_streamer_paises(fake: Faker, streamers: list[Usuario], paises: list[Pais], count: int) -> list[StreamerPais]:
    """Gera relações fictícias de nacionalidade para streamers."""
    streamer_paises: list[StreamerPais] = []
    pairs = set()
    max_possible_pairs = len(streamers) * len(paises)
    if count > max_possible_pairs:
        count = max_possible_pairs

    while len(streamer_paises) < count:
        streamer = random.choice(streamers)
        pais = random.choice(paises)
        if (streamer.id, pais.ddi) not in pairs:
            pairs.add((streamer.id, pais.ddi))
            streamer_paises.append(
                StreamerPais(
                    id_usuario=streamer.id,
                    ddi_pais=pais.ddi,
                    nro_passaporte=fake.unique.ssn()
                )
            )
    return streamer_paises

def generate_empresa_paises(fake: Faker, empresas: list[Empresa], paises: list[Pais], count: int) -> list[EmpresaPais]:
    """Gera relações fictícias entre empresas e países."""
    empresa_paises: list[EmpresaPais] = []
    pairs = set()
    max_possible = len(empresas) * len(paises)
    if count > max_possible:
        count = max_possible
    
    while len(empresa_paises) < count:
        empresa = random.choice(empresas)
        pais = random.choice(paises)
        if (empresa.nro, pais.ddi) not in pairs:
            pairs.add((empresa.nro, pais.ddi))
            empresa_paises.append(
                EmpresaPais(
                    nro_empresa=empresa.nro,
                    ddi_pais=pais.ddi,
                    id_nacional=fake.unique.bban()
                )
            )
    return empresa_paises

def generate_canais(fake: Faker, plataformas: list[Plataforma], streamers: list[Usuario]) -> list[Canal]:
    """Gera um canal para cada streamer, garantindo nomes de canal únicos por plataforma."""
    canais: list[Canal] = []
    for streamer in streamers:
        # Create a unique channel name from the streamer's unique nick
        channel_name = f"{streamer.nick}_canal"

        canais.append(
            Canal(
                nro_plataforma=random.choice(plataformas).nro,
                nick_streamer=streamer.nick,
                nome=channel_name,
                tipo=random.choice(list(TipoCanal)),
                data=fake.date_object(),
                descricao=fake.sentence(),
                qtd_visualizacoes=random.randint(0, 1000000)
            )
        )
    return canais

def generate_patrocinios(fake: Faker, empresas: list[Empresa], canais: list[Canal], count: int) -> list[Patrocinio]:
    """Gera patrocínios fictícios entre empresas e canais."""
    patrocinios: list[Patrocinio] = []
    pairs = set()
    max_possible = len(empresas) * len(canais)
    if count > max_possible:
        count = max_possible

    while len(patrocinios) < count:
        empresa = random.choice(empresas)
        canal = random.choice(canais)
        if (empresa.nro, canal.id) not in pairs:
            pairs.add((empresa.nro, canal.id))
            patrocinios.append(
                Patrocinio(
                    nro_empresa=empresa.nro,
                    id_canal=canal.id,
                    valor=fake.pydecimal(left_digits=8, right_digits=2, positive=True)
                )
            )
    return patrocinios

def generate_nivel_canais(fake: Faker, canais: list[Canal], niveis_por_canal: int) -> list[NivelCanal]:
    """Gera níveis de inscrição para canais."""
    nivel_canais: list[NivelCanal] = []
    for canal in canais:
        for i in range(niveis_por_canal):
            nivel_canais.append(
                NivelCanal(
                    id_canal=canal.id,
                    nivel=f"Nivel {i+1}",
                    valor=fake.pydecimal(left_digits=3, right_digits=2, positive=True),
                    gif=fake.image_url()
                )
            )
    return nivel_canais

def generate_inscricoes(niveis: list[NivelCanal], usuarios: list[Usuario], count: int) -> list[Inscricao]:
    """Gera inscrições de usuários em níveis de canal."""
    inscricoes: list[Inscricao] = []
    pairs = set()
    max_possible = len(niveis) * len(usuarios)
    if count > max_possible:
        count = max_possible

    while len(inscricoes) < count:
        nivel = random.choice(niveis)
        usuario = random.choice(usuarios)
        if (nivel.id, usuario.id) not in pairs:
            pairs.add((nivel.id, usuario.id))
            inscricoes.append(
                Inscricao(
                    id_nivel=nivel.id,
                    id_membro=usuario.id
                )
            )
    return inscricoes

def generate_videos(fake: Faker, count: int, canais: list[Canal]) -> list[Video]:
    """Gera uma lista de vídeos fictícios."""
    videos: list[Video] = []
    for _ in range(count):
        videos.append(
            Video(
                id_canal=random.choice(canais).id,
                titulo=fake.sentence(nb_words=4),
                data_h=fake.date_object(),
                tema=fake.word(),
                duracao=fake.time_object(),
                visu_simult=random.randint(0, 10000),
                visu_total=random.randint(10000, 1000000)
            )
        )
    return videos

def generate_participacoes(videos: list[Video], streamers: list[Usuario], count: int) -> list[Participa]:
    """Gera participações de streamers em vídeos."""
    participacoes: list[Participa] = []
    pairs = set()
    max_possible = len(videos) * len(streamers)
    if count > max_possible:
        count = max_possible

    while len(participacoes) < count:
        video = random.choice(videos)
        streamer = random.choice(streamers)
        if (video.id, streamer.id) not in pairs:
            pairs.add((video.id, streamer.id))
            participacoes.append(
                Participa(
                    id_video=video.id,
                    id_streamer=streamer.id
                )
            )
    return participacoes

def generate_comentarios(fake: Faker, count: int, videos: list[Video], usuarios: list[Usuario]) -> list[Comentario]:
    """Gera uma lista de comentários fictícios."""
    comentarios: list[Comentario] = []
    for _ in range(count):
        comentarios.append(
            Comentario(
                id_video=random.choice(videos).id,
                id_usuario=random.choice(usuarios).id,
                texto=fake.text(),
                data_h=fake.date_time_this_year(),
                coment_on=fake.boolean()
            )
        )
    return comentarios

def generate_doacoes(fake: Faker, comentarios: list[Comentario]) -> list[Doacao]:
    """Gera doações para um subconjunto de comentários."""
    doacoes: list[Doacao] = []
    comentarios_doacao = random.sample(comentarios, k=len(comentarios) // 2)
    for comentario in comentarios_doacao:
        doacoes.append(
            Doacao(
                id_comentario=comentario.num_seq,
                valor=fake.pydecimal(left_digits=4, right_digits=2, positive=True),
                status_pagamento=random.choice(list(StatusPagamento))
            )
        )
    return doacoes

def generate_pagamentos(fake: Faker, doacoes: list[Doacao]) -> tuple[list[Bitcoin], list[CartaoCredito], list[Paypal], list[MecPlat]]:
    """Distribui as doações entre diferentes métodos de pagamento."""
    bitcoins: list[Bitcoin] = []
    cartoes: list[CartaoCredito] = []
    paypals: list[Paypal] = []
    mec_plats: list[MecPlat] = []

    doacoes_shuffled = random.sample(doacoes, len(doacoes))
    
    num_doacoes = len(doacoes_shuffled)
    split1 = num_doacoes // 4
    split2 = num_doacoes // 2
    split3 = 3 * num_doacoes // 4

    for doacao in doacoes_shuffled[:split1]:
        bitcoins.append(Bitcoin(id_doacao=doacao.id_comentario, tx_id=fake.sha256()))

    used_card_nums = set()
    for doacao in doacoes_shuffled[split1:split2]:
        card_num = fake.credit_card_number()
        while card_num in used_card_nums:
            card_num = fake.credit_card_number()
        used_card_nums.add(card_num)
        cartoes.append(
            CartaoCredito(
                id_doacao=doacao.id_comentario,
                num=card_num,
                bandeira=fake.credit_card_provider()
            )
        )
    
    for i, doacao in enumerate(doacoes_shuffled[split2:split3]):
        paypals.append(Paypal(id_doacao=doacao.id_comentario, id=i))

    for i, doacao in enumerate(doacoes_shuffled[split3:]):
        mec_plats.append(MecPlat(id_doacao=doacao.id_comentario, seq=i))

    return bitcoins, cartoes, paypals, mec_plats
