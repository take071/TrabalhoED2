"""
Módulo: Grafo da Rede Internacional (Etapa 3)
Disciplina: Estruturas de Dados II - UNEB
Equipe: Arthur Felipe, Lucas Vinicius, Raphael Lopes

Objetivo:
Representar a rede internacional de conexões da GlobalSIM através de um Grafo Ponderado,
onde:
- Vértices: países atendidos (identificados por código, ex: "BR", "US", "PT").
- Arestas: conexões de rede entre países.
- Pesos: latência da conexão em milissegundos (ms).

Requisitos e Orientações:
1. Representação do grafo (lista de adjacência recomendada).
2. Algoritmo Breadth-First Search (BFS - Busca em Largura).
3. Algoritmo Depth-First Search (DFS - Busca em Profundidade).
4. Algoritmo de Dijkstra para cálculo da rota de menor latência total.
"""


class GrafoRede:
    """
    Grafo ponderado para modelagem de rede internacional de telecomunicações.
    """
    def __init__(self):
        # Mapeamento: vertice -> [(vizinho, latencia_ms), ...]
        self.adjacencias = {}

    def adicionar_vertice(self, vertice: str):
        """Adiciona um novo país à rede."""
        # TODO: Adicionar vértice na estrutura de adjacência
        pass

    def adicionar_aresta(self, origem: str, destino: str, latencia_ms: int):
        """
        Adiciona uma conexão bidirecional entre dois países com seu peso de latência.
        """
        # TODO: Adicionar aresta bidirecional com peso
        pass

    def bfs(self, origem: str) -> list:
        """
        Busca em Largura (BFS).
        Retorna a ordem de visitação dos vértices a partir da origem.
        """
        # TODO: Implementar BFS utilizando fila (FIFO)
        return []

    def dfs(self, origem: str) -> list:
        """
        Busca em Profundidade (DFS).
        Retorna a ordem de visitação dos vértices a partir da origem.
        """
        # TODO: Implementar DFS utilizando pilha ou recursão
        return []

    def dijkstra(self, origem: str, destino: str) -> tuple:
        """
        Algoritmo de Dijkstra para menor caminho ponderado.
        Retorna:
          (caminho_como_lista, latencia_total_em_ms)
        Exemplo:
          (["BR", "PT", "FR", "IT"], 185)
        """
        # TODO: Implementar Dijkstra com fila de prioridades (heapq)
        return ([], 0)
