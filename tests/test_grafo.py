"""
Testes do Grafo (BFS, DFS, Dijkstra).
Execução: python -m unittest discover -s tests -v
"""

import unittest

from estruturas.grafo import Grafo, FilaPrioridade


def rede_do_enunciado():
    g = Grafo()
    for v in ["BR", "US", "PT", "CA", "ES", "FR", "JP", "IT"]:
        g.adicionar_vertice(v)
    for u, v, p in [("BR", "US", 80), ("BR", "PT", 120), ("PT", "ES", 30), ("PT", "FR", 40),
                    ("FR", "IT", 25), ("US", "CA", 20), ("CA", "JP", 110)]:
        g.adicionar_aresta(u, v, p)
    return g


class TestFilaPrioridade(unittest.TestCase):
    def test_ordem_de_saida(self):
        f = FilaPrioridade()
        for p in [5, 1, 9, 3, 7, 2, 8]:
            f.inserir(p, f"v{p}")
        saida = [f.remover_minimo()[0] for _ in range(len(f))]
        self.assertEqual(saida, sorted(saida))


class TestGrafo(unittest.TestCase):
    def setUp(self):
        self.g = rede_do_enunciado()

    def test_estrutura_basica(self):
        self.assertEqual(len(self.g), 8)
        self.assertEqual(len(self.g.arestas()), 7)
        self.assertEqual(self.g.peso("BR", "PT"), 120)
        self.assertEqual(self.g.peso("PT", "BR"), 120)   # não-direcionado
        self.assertTrue(self.g.tem_aresta("it", "fr"))   # normaliza caixa

    def test_validacoes(self):
        with self.assertRaises(ValueError):
            self.g.adicionar_aresta("BR", "BR", 10)
        with self.assertRaises(ValueError):
            self.g.adicionar_aresta("BR", "XX", 10)
        for invalido in (0, -5, "abc", None, float("inf")):
            with self.assertRaises(ValueError):
                self.g.adicionar_aresta("BR", "IT", invalido)

    def test_atualizar_e_remover_aresta(self):
        self.assertEqual(self.g.adicionar_aresta("BR", "PT", 100), "atualizada")
        self.assertEqual(self.g.peso("PT", "BR"), 100)
        self.assertTrue(self.g.remover_aresta("PT", "BR"))
        self.assertFalse(self.g.remover_aresta("PT", "BR"))
        self.assertFalse(self.g.tem_aresta("BR", "PT"))

    def test_remover_vertice_remove_arestas(self):
        self.assertTrue(self.g.remover_vertice("PT"))
        self.assertFalse(self.g.tem_vertice("PT"))
        self.assertEqual(self.g.vizinhos("BR"), [("US", 80)])
        self.assertEqual(len(self.g.arestas()), 4)

    def test_dijkstra_exemplo_do_enunciado(self):
        r = self.g.dijkstra("BR", "IT")
        self.assertEqual(r["caminho"], ["BR", "PT", "FR", "IT"])
        self.assertEqual(r["latencia"], 185)

    def test_dijkstra_outras_rotas(self):
        self.assertEqual(self.g.dijkstra("BR", "JP")["latencia"], 210)
        self.assertEqual(self.g.dijkstra("ES", "JP")["caminho"],
                         ["ES", "PT", "BR", "US", "CA", "JP"])
        mesma = self.g.dijkstra("BR", "BR")
        self.assertEqual((mesma["caminho"], mesma["latencia"]), (["BR"], 0))

    def test_dijkstra_prefere_menor_latencia_a_menos_saltos(self):
        self.g.adicionar_aresta("BR", "FR", 500)   # atalho com 1 salto, mas lento
        self.assertEqual(self.g.caminho_menos_saltos("BR", "FR"), ["BR", "FR"])
        r = self.g.dijkstra("BR", "FR")
        self.assertEqual(r["caminho"], ["BR", "PT", "FR"])
        self.assertEqual(r["latencia"], 160)

    def test_dijkstra_sem_destino_calcula_todas_as_distancias(self):
        r = self.g.dijkstra("BR")
        self.assertEqual(r["distancias"], {"BR": 0, "US": 80, "PT": 120, "CA": 100,
                                           "ES": 150, "FR": 160, "JP": 210, "IT": 185})

    def test_dijkstra_confere_com_forca_bruta(self):
        # soma de latências de todos os caminhos simples; o menor deve ser igual ao Dijkstra
        def todos(u, destino, visitados, total):
            if u == destino:
                yield total
                return
            for v, p in self.g.vizinhos(u):
                if v not in visitados:
                    yield from todos(v, destino, visitados | {v}, total + p)
        self.g.adicionar_aresta("ES", "IT", 90)
        self.g.adicionar_aresta("CA", "FR", 70)
        for origem in self.g.vertices():
            for destino in self.g.vertices():
                esperado = min(todos(origem, destino, {origem}, 0))
                self.assertEqual(self.g.dijkstra(origem, destino)["latencia"], esperado, (origem, destino))

    def test_destino_inalcancavel(self):
        self.g.adicionar_vertice("AR")
        r = self.g.dijkstra("BR", "AR")
        self.assertFalse(r["encontrada"])
        self.assertEqual(r["caminho"], [])
        self.assertIsNone(r["latencia"])
        self.assertEqual(self.g.bfs("BR")["nao_alcancados"], ["AR"])

    def test_vertice_inexistente(self):
        with self.assertRaises(ValueError):
            self.g.dijkstra("XX", "BR")
        with self.assertRaises(ValueError):
            self.g.bfs("XX")
        with self.assertRaises(ValueError):
            self.g.dfs("XX")

    def test_bfs(self):
        r = self.g.bfs("BR")
        self.assertEqual(r["ordem"], ["BR", "PT", "US", "ES", "FR", "CA", "IT", "JP"])
        self.assertEqual(r["niveis"]["IT"], 3)
        self.assertEqual(r["por_nivel"][1], ["PT", "US"])
        self.assertEqual(r["alcancados"], 8)

    def test_dfs(self):
        r = self.g.dfs("BR")
        self.assertEqual(r["ordem"], ["BR", "PT", "ES", "FR", "IT", "US", "CA", "JP"])
        self.assertEqual(r["profundidade"]["IT"], 3)
        self.assertEqual(r["profundidade_maxima"], 3)
        # propriedade dos tempos: o ancestral é descoberto antes e finalizado depois
        for v, p in r["pai"].items():
            if p is not None:
                self.assertLess(r["descoberta"][p], r["descoberta"][v])
                self.assertGreater(r["finalizacao"][p], r["finalizacao"][v])

    def test_dfs_iterativo_igual_ao_recursivo(self):
        self.g.adicionar_aresta("ES", "IT", 90)
        self.g.adicionar_aresta("CA", "FR", 70)
        visitados, ordem = set(), []

        def rec(u):
            visitados.add(u)
            ordem.append(u)
            for v, _ in self.g.vizinhos(u):
                if v not in visitados:
                    rec(v)
        rec("BR")
        self.assertEqual(self.g.dfs("BR")["ordem"], ordem)

    def test_componentes_e_metricas(self):
        self.assertTrue(self.g.obter_metricas()["conexo"])
        self.g.remover_aresta("BR", "US")
        m = self.g.obter_metricas()
        self.assertFalse(m["conexo"])
        self.assertEqual(sorted(len(c) for c in m["componentes"]), [3, 5])
        self.assertEqual(m["vertices"], 8)
        self.assertEqual(m["arestas"], 6)

    def test_para_dict(self):
        d = self.g.para_dict()
        self.assertEqual(len(d["arestas"]), 7)
        self.assertIn({"origem": "BR", "destino": "PT", "latencia": 120}, d["arestas"])


if __name__ == "__main__":
    unittest.main()
