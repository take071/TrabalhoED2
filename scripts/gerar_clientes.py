"""
Gerador de clientes do GlobalSIM (Etapa 2).

Gera automaticamente o arquivo arquivos/clientes.json com IDs únicos e eSIMs únicos,
em ordem embaralhada (assim, a carga na Árvore B provoca divisões em vários pontos
da árvore, em vez de apenas na borda direita).

Uso:
    python3 scripts/gerar_clientes.py              # 1000 clientes, semente 2026
    python3 scripts/gerar_clientes.py 5000 7       # 5000 clientes, semente 7

Atenção: sobrescreve arquivos/clientes.json.
"""

import json
import os
import random
import sys
import unicodedata

RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_SAIDA = os.path.join(RAIZ_PROJETO, "arquivos", "clientes.json")

PRIMEIROS_NOMES = [
    "Maria", "José", "Ana", "João", "Antônio", "Francisca", "Carlos", "Paulo", "Pedro",
    "Lucas", "Luiz", "Marcos", "Luís", "Gabriel", "Rafael", "Daniel", "Marcelo", "Bruno",
    "Eduardo", "Felipe", "Raimundo", "Rodrigo", "Juliana", "Fernanda", "Patrícia",
    "Aline", "Sandra", "Camila", "Amanda", "Bruna", "Jéssica", "Letícia", "Júlia",
    "Luciana", "Vanessa", "Mariana", "Beatriz", "Larissa", "Rita", "Cláudia", "Renata",
    "Tatiane", "Débora", "Thiago", "Vinícius", "Leonardo", "Gustavo", "Diego", "Matheus",
    "Caio", "Isabela", "Helena", "Valentina", "Heitor", "Miguel", "Arthur", "Davi",
]

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira",
    "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes",
    "Soares", "Fernandes", "Vieira", "Barbosa", "Rocha", "Dias", "Nascimento", "Andrade",
    "Moreira", "Nunes", "Marques", "Machado", "Mendes", "Freitas", "Cardoso", "Ramos",
    "Gonçalves", "Santana", "Teixeira", "Araújo", "Pinto", "Correia", "Cavalcanti",
]

DOMINIOS = ["email.com", "mail.com", "correio.com.br", "globalmail.net"]

PACOTES = [101, 102, 201, 202, 301]


def sem_acentos(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in base if not unicodedata.combining(c))


def gerar(quantidade: int, semente: int) -> list:
    rnd = random.Random(semente)

    # Faixa de IDs de 5 dígitos; amostragem sem reposição garante unicidade
    ids = rnd.sample(range(10000, 100000), quantidade)
    codigos_esim = rnd.sample(range(10000, 100000), quantidade)

    clientes = []
    for cid, cod_esim in zip(ids, codigos_esim):
        nome = f"{rnd.choice(PRIMEIROS_NOMES)} {rnd.choice(SOBRENOMES)}"
        email = f"{sem_acentos(nome).lower().replace(' ', '.')}{cid}@{rnd.choice(DOMINIOS)}"

        sorteio = rnd.random()
        if sorteio < 0.06:
            # Cliente cadastrado, ainda sem eSIM e sem pacote associados
            esim, pacote, status = None, None, "pendente"
        else:
            esim = f"ESIM-{cod_esim}"
            pacote = rnd.choice(PACOTES)
            status = "ativo" if sorteio < 0.84 else ("inativo" if sorteio < 0.94 else "suspenso")

        clientes.append({
            "id": cid,
            "nome": nome,
            "email": email,
            "esim": esim,
            "pacote": pacote,
            "status": status,
        })

    # Registro do exemplo do enunciado (garante um caso de demonstração conhecido)
    clientes[0] = {
        "id": 58372,
        "nome": "Maria Silva",
        "email": "maria@email.com",
        "esim": "ESIM-83921",
        "pacote": 102,
        "status": "ativo",
    }
    # Evita colisão do ID/eSIM de demonstração com os demais registros gerados
    clientes = [clientes[0]] + [
        c for c in clientes[1:] if c["id"] != 58372 and c["esim"] != "ESIM-83921"
    ]
    return clientes


if __name__ == "__main__":
    quantidade = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    semente = int(sys.argv[2]) if len(sys.argv) > 2 else 2026

    dados = gerar(quantidade, semente)
    with open(CAMINHO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    print(f"{len(dados)} clientes gerados em {CAMINHO_SAIDA}")
