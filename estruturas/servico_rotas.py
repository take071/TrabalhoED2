"""
Integração Grafo + Cache LRU (diferencial da equipe).

ServicoRotas é a "porta de entrada" para consultar rotas de menor latência:
  1. Procura a rota no Cache LRU (chave "ORIGEM->DESTINO").        -> HIT: responde em O(1)
  2. Se não estiver (MISS), executa o Dijkstra no Grafo.            -> fonte da verdade
  3. Grava o resultado no cache para as próximas consultas iguais.

Também invalida o cache quando a rede muda:
  - aresta criada/alterada/removida  -> qualquer rota pode ter mudado: limpa tudo;
  - país removido                    -> só as rotas que o usam (origem, destino ou escala).

Este módulo não depende do Flask.
"""

import random
import time

from .cache_lru import CacheLRU
from .grafo import Grafo


class ServicoRotas:

    def __init__(self, grafo: Grafo, cache: CacheLRU):
        self.grafo = grafo
        self.cache = cache
        # Instrumentação acumulada do serviço
        self.total_consultas = 0
        self.execucoes_dijkstra = 0
        self.nos_expandidos_dijkstra = 0   # trabalho realmente feito pelo Dijkstra
        self.nos_economizados = 0          # trabalho evitado graças aos HITs

    @staticmethod
    def chave(origem, destino) -> str:
        return f"{str(origem).strip().upper()}->{str(destino).strip().upper()}"

    def consultar(self, origem, destino, usar_cache: bool = True) -> dict:
        """
        Devolve a rota de menor latência entre dois países.
        O campo 'cache' informa HIT, MISS ou SEM_CACHE. Levanta ValueError se
        origem/destino não forem vértices do grafo.
        """
        origem = str(origem).strip().upper()
        destino = str(destino).strip().upper()
        inicio = time.perf_counter_ns()
        chave = self.chave(origem, destino)
        self.total_consultas += 1

        if usar_cache:
            dados = self.cache.obter(chave)
            if dados is not None:
                self.nos_economizados += dados["nos_expandidos"]
                return self._montar(dados, "HIT", chave, time.perf_counter_ns() - inicio)

        resultado = self.grafo.dijkstra(origem, destino)
        self.execucoes_dijkstra += 1
        self.nos_expandidos_dijkstra += resultado["nos_expandidos"]

        dados = {
            "origem": origem,
            "destino": destino,
            "encontrada": resultado["encontrada"],
            "caminho": resultado["caminho"],
            "latencia": resultado["latencia"],
            "ordem_expansao": resultado["ordem_expansao"],
            "nos_expandidos": resultado["nos_expandidos"],
            "relaxamentos": resultado["relaxamentos"],
            "arestas_examinadas": resultado["arestas_examinadas"],
            "tempo_dijkstra_ns": resultado["tempo_ns"],
        }
        status = "SEM_CACHE"
        if usar_cache:
            self.cache.colocar(chave, dados)
            status = "MISS"
        return self._montar(dados, status, chave, time.perf_counter_ns() - inicio)

    @staticmethod
    def _montar(dados: dict, status: str, chave: str, tempo_ns: int) -> dict:
        return dict(dados, cache=status, chave=chave, tempo_ns=tempo_ns)

    # ------------------------------------------------------------------
    # Invalidação (gatilhos acionados pelas rotas Flask)
    # ------------------------------------------------------------------
    def invalidar_tudo(self) -> int:
        """Mudou a topologia (aresta criada/alterada/removida): nenhuma rota é confiável."""
        return self.cache.limpar()

    def invalidar_pais(self, codigo) -> int:
        """País removido: descarta as rotas que partem, chegam ou passam por ele."""
        codigo = str(codigo).strip().upper()
        return self.cache.invalidar_se(
            lambda chave, v: codigo == v["origem"] or codigo == v["destino"] or codigo in v["caminho"]
        )

    def obter_metricas(self) -> dict:
        return {
            "consultas": self.total_consultas,
            "execucoes_dijkstra": self.execucoes_dijkstra,
            "nos_expandidos": self.nos_expandidos_dijkstra,
            "nos_economizados": self.nos_economizados,
        }


# ======================================================================
# Benchmark do diferencial (não altera o cache real da aplicação)
# ======================================================================

def _gerar_carga(grafo: Grafo, quantidade: int, semente: int) -> tuple[list, list]:
    """
    Gera consultas com popularidade desigual (poucos destinos muito pedidos, como num
    serviço real): os pares são embaralhados e sorteados com peso 1/posição^1.2.
    """
    rng = random.Random(semente)
    vertices = grafo.vertices()
    pares = [(u, v) for u in vertices for v in vertices if u != v]
    if not pares:
        return [], []
    rng.shuffle(pares)
    pesos = [1 / (i + 1) ** 1.2 for i in range(len(pares))]
    return rng.choices(pares, weights=pesos, k=quantidade), pares


def executar_benchmark(grafo: Grafo, quantidade: int = 2000, semente: int = 42,
                       capacidades=(1, 2, 4, 8, 16, 32, 64)) -> dict:
    """
    Compara o cálculo SEM cache (Dijkstra em toda consulta) com o ServicoRotas usando
    caches LRU de várias capacidades, sobre a mesma carga de consultas.
    A métrica mais confiável é 'nós expandidos' (determinística); o tempo depende da máquina.
    """
    carga, pares = _gerar_carga(grafo, quantidade, semente)
    if not carga:
        return {"erro": "O grafo precisa de pelo menos 2 países."}

    # Base: sem cache
    inicio = time.perf_counter_ns()
    nos_base = 0
    for origem, destino in carga:
        nos_base += grafo.dijkstra(origem, destino)["nos_expandidos"]
    tempo_base = time.perf_counter_ns() - inicio

    linhas = []
    for capacidade in capacidades:
        cache = CacheLRU(capacidade, registrar_eventos=False)
        servico = ServicoRotas(grafo, cache)
        inicio = time.perf_counter_ns()
        for origem, destino in carga:
            servico.consultar(origem, destino)
        tempo = time.perf_counter_ns() - inicio
        linhas.append({
            "capacidade": capacidade,
            "hits": cache.hits,
            "misses": cache.misses,
            "taxa_acerto": round(100 * cache.hits / len(carga), 1),
            "evicoes": cache.evicoes,
            "execucoes_dijkstra": servico.execucoes_dijkstra,
            "nos_expandidos": servico.nos_expandidos_dijkstra,
            "reducao_nos": round(100 * (1 - servico.nos_expandidos_dijkstra / nos_base), 1) if nos_base else 0.0,
            "tempo_ms": round(tempo / 1e6, 2),
            "ganho": round(tempo_base / tempo, 2) if tempo else 0.0,
        })

    return {
        "consultas": len(carga),
        "semente": semente,
        "pares_distintos": len(pares),
        "base_tempo_ms": round(tempo_base / 1e6, 2),
        "base_nos": nos_base,
        "linhas": linhas,
        "escalabilidade": medir_escalabilidade(),
    }


def medir_escalabilidade(tamanhos=(100, 1_000, 10_000, 100_000), iteracoes: int = 20_000) -> list:
    """
    Evidência empírica do O(1): o custo médio por operação (obter/colocar) deve ficar
    praticamente constante mesmo quando a capacidade cresce 1000 vezes.
    """
    resultados = []
    for capacidade in tamanhos:
        cache = CacheLRU(capacidade, registrar_eventos=False)
        for i in range(capacidade):
            cache.colocar(f"k{i}", i)
        rng = random.Random(7)
        proxima = capacidade
        inicio = time.perf_counter_ns()
        for _ in range(iteracoes):
            cache.obter(f"k{rng.randrange(max(0, proxima - capacidade), proxima)}")  # quase sempre HIT
            cache.colocar(f"k{proxima}", proxima)                                     # força despejo do LRU
            cache.obter(f"x{proxima}")                                                # sempre MISS
            proxima += 1
        total = time.perf_counter_ns() - inicio
        resultados.append({
            "capacidade": capacidade,
            "operacoes": 3 * iteracoes,
            "ns_por_operacao": round(total / (3 * iteracoes)),
        })
    return resultados
