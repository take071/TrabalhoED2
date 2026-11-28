"""
Testes do Cache LRU (diferencial) e da integração com o Grafo.
Execução: python -m unittest discover -s tests -v
"""

import random
import unittest

from estruturas.cache_lru import CacheLRU
from estruturas.servico_rotas import ServicoRotas, executar_benchmark, medir_escalabilidade
from tests.test_grafo import rede_do_enunciado


class RelogioFalso:
    def __init__(self):
        self.agora = 0.0

    def __call__(self):
        return self.agora


class TestCacheLRU(unittest.TestCase):
    def test_capacidade_invalida(self):
        with self.assertRaises(ValueError):
            CacheLRU(0)

    def test_hit_e_miss(self):
        c = CacheLRU(2)
        self.assertIsNone(c.obter("a"))
        c.colocar("a", 1)
        self.assertEqual(c.obter("a"), 1)
        self.assertEqual((c.hits, c.misses), (1, 1))
        self.assertEqual(c.obter_metricas()["taxa_acerto"], 50.0)

    def test_despeja_o_menos_recentemente_usado(self):
        c = CacheLRU(3)
        for k in "abc":
            c.colocar(k, k.upper())
        c.obter("a")                      # a vira o mais recente; b é o LRU
        despejada = c.colocar("d", "D")
        self.assertEqual(despejada, "b")
        self.assertNotIn("b", c)
        self.assertEqual([e["chave"] for e in c.entradas()], ["d", "a", "c"])
        self.assertEqual(c.evicoes, 1)

    def test_atualizar_nao_despeja_e_vira_mru(self):
        c = CacheLRU(2)
        c.colocar("a", 1)
        c.colocar("b", 2)
        self.assertIsNone(c.colocar("a", 10))
        self.assertEqual(c.obter("a"), 10)
        self.assertEqual(len(c), 2)
        self.assertEqual(c.entradas()[0]["chave"], "a")

    def test_espiar_nao_altera_ordem_nem_contadores(self):
        c = CacheLRU(2)
        c.colocar("a", 1)
        c.colocar("b", 2)
        self.assertEqual(c.espiar("a"), 1)
        self.assertEqual((c.hits, c.misses), (0, 0))
        self.assertEqual([e["chave"] for e in c.entradas()], ["b", "a"])

    def test_capacidade_um(self):
        c = CacheLRU(1)
        c.colocar("a", 1)
        self.assertEqual(c.colocar("b", 2), "a")
        self.assertIsNone(c.obter("a"))
        self.assertEqual(c.obter("b"), 2)
        self.assertTrue(c.validar()[0])

    def test_remover_e_invalidar_se(self):
        c = CacheLRU(5)
        for i in range(5):
            c.colocar(f"k{i}", i)
        self.assertTrue(c.remover("k2"))
        self.assertFalse(c.remover("k2"))
        self.assertEqual(c.invalidar_se(lambda k, v: v % 2 == 0), 2)   # k0 e k4
        self.assertEqual(sorted(e["chave"] for e in c.entradas()), ["k1", "k3"])
        self.assertEqual(c.invalidacoes, 3)
        self.assertTrue(c.validar()[0])

    def test_limpar(self):
        c = CacheLRU(3)
        c.colocar("a", 1)
        c.colocar("b", 2)
        self.assertEqual(c.limpar(), 2)
        self.assertEqual(len(c), 0)
        self.assertEqual(c.entradas(), [])
        self.assertTrue(c.validar()[0])

    def test_redimensionar(self):
        c = CacheLRU(4)
        for k in "abcd":
            c.colocar(k, k)
        self.assertEqual(c.redimensionar(2), ["a", "b"])   # saem as menos recentes
        self.assertEqual([e["chave"] for e in c.entradas()], ["d", "c"])
        c.redimensionar(10)
        self.assertEqual(c.capacidade, 10)

    def test_ttl(self):
        relogio = RelogioFalso()
        c = CacheLRU(3, ttl_segundos=10, relogio=relogio)
        c.colocar("a", 1)
        relogio.agora = 5
        self.assertEqual(c.obter("a"), 1)
        relogio.agora = 11
        self.assertIsNone(c.obter("a"))
        self.assertEqual(c.expiracoes, 1)
        self.assertEqual(len(c), 0)

    def test_eventos(self):
        c = CacheLRU(1)
        c.obter("a")
        c.colocar("a", 1)
        c.obter("a")
        c.colocar("b", 2)
        tipos = [e["tipo"] for e in reversed(c.obter_metricas()["eventos"])]
        self.assertEqual(tipos, ["MISS", "INSERE", "HIT", "DESPEJA", "INSERE"])

    def test_contra_modelo_de_referencia(self):
        """Compara com um modelo simples (lista) em milhares de operações aleatórias."""
        rng = random.Random(1)
        capacidade = 7
        c = CacheLRU(capacidade, registrar_eventos=False)
        modelo = []   # [(chave, valor)] do menos ao mais recente
        for _ in range(5000):
            chave = rng.randrange(20)
            if rng.random() < 0.5:
                esperado = next((v for k, v in modelo if k == chave), None)
                self.assertEqual(c.obter(chave), esperado)
                if esperado is not None:
                    modelo = [(k, v) for k, v in modelo if k != chave] + [(chave, esperado)]
            else:
                valor = rng.randrange(1000)
                modelo = [(k, v) for k, v in modelo if k != chave] + [(chave, valor)]
                if len(modelo) > capacidade:
                    modelo.pop(0)
                c.colocar(chave, valor)
            self.assertEqual([e["chave"] for e in c.entradas()], [k for k, _ in reversed(modelo)])
        self.assertTrue(c.validar()[0])


class TestServicoRotas(unittest.TestCase):
    def setUp(self):
        self.grafo = rede_do_enunciado()
        self.cache = CacheLRU(4)
        self.servico = ServicoRotas(self.grafo, self.cache)

    def test_primeiro_miss_depois_hit_com_mesmo_resultado(self):
        r1 = self.servico.consultar("BR", "IT")
        r2 = self.servico.consultar("br", " it ")
        self.assertEqual((r1["cache"], r2["cache"]), ("MISS", "HIT"))
        self.assertEqual(r1["caminho"], r2["caminho"])
        self.assertEqual(r2["latencia"], 185)
        self.assertEqual(self.servico.execucoes_dijkstra, 1)
        self.assertEqual(self.servico.nos_economizados, r1["nos_expandidos"])

    def test_sem_cache_sempre_executa_dijkstra(self):
        self.servico.consultar("BR", "IT", usar_cache=False)
        r = self.servico.consultar("BR", "IT", usar_cache=False)
        self.assertEqual(r["cache"], "SEM_CACHE")
        self.assertEqual(self.servico.execucoes_dijkstra, 2)
        self.assertEqual(len(self.cache), 0)

    def test_rota_inexistente_tambem_e_guardada(self):
        self.grafo.adicionar_vertice("AR")
        self.assertFalse(self.servico.consultar("BR", "AR")["encontrada"])
        r = self.servico.consultar("BR", "AR")
        self.assertEqual(r["cache"], "HIT")
        self.assertFalse(r["encontrada"])

    def test_invalidar_tudo_apos_mudar_aresta(self):
        self.servico.consultar("BR", "IT")
        self.servico.consultar("BR", "JP")
        self.grafo.adicionar_aresta("BR", "FR", 10)     # nova rota mais curta
        self.assertEqual(self.servico.invalidar_tudo(), 2)
        r = self.servico.consultar("BR", "IT")
        self.assertEqual(r["cache"], "MISS")
        self.assertEqual(r["caminho"], ["BR", "FR", "IT"])
        self.assertEqual(r["latencia"], 35)

    def test_invalidar_pais_remove_so_rotas_que_o_usam(self):
        self.servico.consultar("BR", "IT")   # passa por PT e FR
        self.servico.consultar("BR", "JP")   # passa por US e CA
        self.servico.consultar("ES", "PT")   # origem ES
        self.assertEqual(self.servico.invalidar_pais("fr"), 1)
        chaves = {e["chave"] for e in self.cache.entradas()}
        self.assertEqual(chaves, {"BR->JP", "ES->PT"})
        self.assertEqual(self.servico.invalidar_pais("PT"), 1)    # ES->PT; BR->JP não usa PT
        self.assertEqual({e["chave"] for e in self.cache.entradas()}, {"BR->JP"})

    def test_resposta_do_cache_igual_ao_dijkstra_sob_carga(self):
        rng = random.Random(3)
        vertices = self.grafo.vertices()
        for _ in range(500):
            u, v = rng.choice(vertices), rng.choice(vertices)
            via_cache = self.servico.consultar(u, v)
            direto = self.grafo.dijkstra(u, v)
            self.assertEqual(via_cache["caminho"], direto["caminho"])
            self.assertEqual(via_cache["latencia"], direto["latencia"])
        self.assertTrue(self.cache.validar()[0])


class TestBenchmark(unittest.TestCase):
    def test_cache_maior_reduz_trabalho(self):
        r = executar_benchmark(rede_do_enunciado(), quantidade=500, semente=1, capacidades=(1, 8, 64))
        reducoes = [l["reducao_nos"] for l in r["linhas"]]
        self.assertEqual(reducoes, sorted(reducoes))
        ultima = r["linhas"][-1]
        self.assertEqual(ultima["misses"], ultima["execucoes_dijkstra"])
        self.assertEqual(ultima["evicoes"], 0)       # 64 >= 56 pares possíveis

    def test_benchmark_reproduzivel(self):
        g = rede_do_enunciado()
        a = executar_benchmark(g, 300, 5, capacidades=(4,))["linhas"][0]
        b = executar_benchmark(g, 300, 5, capacidades=(4,))["linhas"][0]
        for campo in ("hits", "misses", "nos_expandidos", "evicoes"):
            self.assertEqual(a[campo], b[campo])

    def test_escalabilidade_retorna_todas_as_capacidades(self):
        r = medir_escalabilidade(tamanhos=(10, 100), iteracoes=500)
        self.assertEqual([x["capacidade"] for x in r], [10, 100])


if __name__ == "__main__":
    unittest.main()
