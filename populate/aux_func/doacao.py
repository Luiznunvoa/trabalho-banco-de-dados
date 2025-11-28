"""Geração de doações e métodos de pagamento."""

from faker import Faker
from models import Doacao, Comentario, Bitcoin, CartaoCredito, Paypal, MecPlat, StatusPagamento
import random


def generate_doacoes(fake: Faker, comentarios: list[Comentario]) -> list[Doacao]:
    """Gera doações para um subconjunto de comentários."""
    doacoes: list[Doacao] = []
    comentarios_doacao = random.sample(comentarios, k=len(comentarios) // 2)
    for comentario in comentarios_doacao:
        doacoes.append(
            Doacao(
                id_video=comentario.id_video,
                num_seq=comentario.num_seq,
                id_usuario=comentario.id_usuario,
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
        bitcoins.append(Bitcoin(
            id_video_doacao=doacao.id_video,
            seq_doacao=doacao.num_seq,
            id_usuario=doacao.id_usuario,
            tx_id=fake.sha256()
        ))

    used_card_nums = set()
    for doacao in doacoes_shuffled[split1:split2]:
        card_num_raw = fake.credit_card_number()
        # Limpa não-dígitos e trunca para 16 caracteres para caber no esquema quebrado
        card_num_clean = "".join(filter(str.isdigit, card_num_raw))[:16]

        while card_num_clean in used_card_nums:
            card_num_raw = fake.credit_card_number()
            card_num_clean = "".join(filter(str.isdigit, card_num_raw))[:16]

        used_card_nums.add(card_num_clean)
        cartoes.append(
            CartaoCredito(
                id_video_doacao=doacao.id_video,
                seq_doacao=doacao.num_seq,
                id_usuario=doacao.id_usuario,
                num=card_num_clean,
                bandeira=fake.credit_card_provider()
            )
        )
    
    for i, doacao in enumerate(doacoes_shuffled[split2:split3]):
        paypals.append(Paypal(
            id_video_doacao=doacao.id_video,
            seq_doacao=doacao.num_seq,
            id_usuario=doacao.id_usuario,
            id=i
        ))

    for i, doacao in enumerate(doacoes_shuffled[split3:]):
        mec_plats.append(MecPlat(
            id_video_doacao=doacao.id_video,
            seq_doacao=doacao.num_seq,
            id_usuario=doacao.id_usuario,
            seq=i
        ))

    return bitcoins, cartoes, paypals, mec_plats
