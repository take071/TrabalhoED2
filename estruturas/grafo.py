"""
Módulo de Grafos - Etapa 3
Representação da rede internacional de conexões da GlobalSIM.
Inclui algoritmos de busca (BFS, DFS) e caminho mínimo com menor latência (Dijkstra).
"""

import heapq

class GrafoRede:
    """Grafo ponderado para roteamento entre países."""
    def __init__(self):
        self.adjacencias = {}  # vertice -> [(vizinho, latencia_ms)]

    def adicionar_vertice(self, vertice: str):
        if vertice not in self.adjacencias:
            self.adjacencias[vertice] = []

    def adicionar_aresta(self, origem: str, destino: str, latencia_ms: int):
        self.adicionar_vertice(origem)
        self.adicionar_vertice(destino)
        self.adjacencias[origem].append((destino, latencia_ms))
        self.adjacencias[destino].append((origem, latencia_ms))

    def dijkstra(self, origem: str, destino: str):
        """Calcula a rota de menor latência entre origem e destino."""
        if origem not in self.adjacencias or destino not in self.adjacencias:
            return None, float('inf')

        distancias = {v: float('inf') for v in self.adjacencias}
        anteriores = {v: None for v in self.adjacencias}
        distancias[origem] = 0

        fila = [(0, origem)]

        while fila:
            dist_atual, u = heapq.heappop(fila)
            if dist_atual > distancias[u]:
                continue
            if u == destino:
                break

            for vizinho, peso in self.adjacencias[u]:
                nova_dist = dist_atual + peso
                if nova_dist < distancias[vizinho]:
                    distancias[vizinho] = nova_dist
                    anteriores[vizinho] = u
                    heapq.heappush(fila, (nova_dist, vizinho))

        if distancias[destino] == float('inf'):
            return None, float('inf')

        caminho = []
        passo = destino
        while passo is not None:
            caminho.append(passo)
            passo = anteriores[passo]
        caminho.reverse()

        return caminho, distancias[destino]
