"""
Módulo de Recomendação de Pacote por Roteiro de Viagem
Diferencial da Equipe (Arthur Felipe, Lucas Vinicius, Raphael Lopes).
Integra Tabela Hash, Grafo e Pacotes para sugerir a opção mais econômica e adequada.
"""

def recomendar_pacote(roteiro_paises: list, dias_viagem: int, perfil_uso: str, tabela_hash, pacotes: list):
    """
    Avalia o roteiro de viagem com base na Tabela Hash e pacotes disponíveis.
    Retorna o melhor pacote sugerido e justificativa técnica.
    """
    regioes = set()
    coberturas = []

    for codigo in roteiro_paises:
        pais = tabela_hash.buscar(codigo)
        if pais:
            regioes.add(pais.get("regiao"))
            coberturas.append({"codigo": codigo, "pais": pais.get("pais"), "coberto": True})
        else:
            coberturas.append({"codigo": codigo, "pais": "Desconhecido", "coberto": False})

    # Regra simples de recomendação inicial
    if len(regioes) == 1 and "Europa" in regioes:
        pacote_sugerido = next((p for p in pacotes if p["codigo"] == 102), pacotes[0])
    elif len(regioes) == 1 and "América" in regioes:
        pacote_sugerido = next((p for p in pacotes if p["codigo"] == 202), pacotes[0])
    else:
        pacote_sugerido = next((p for p in pacotes if p["codigo"] == 301), pacotes[-1])

    return {
        "pacote_recomendado": pacote_sugerido,
        "regioes": list(regioes),
        "coberturas": coberturas,
        "dias_viagem": dias_viagem,
        "perfil_uso": perfil_uso
    }
