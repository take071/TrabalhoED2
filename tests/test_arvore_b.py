"""
Testes da Árvore B (unittest, sem dependências externas).
Execução: python -m unittest discover -s tests -v
"""

import random
import unittest

from estruturas.arvore_b import ArvoreB


def registro(i):
    return {"id": i, "nome": f"Cliente {i}"}


class TestArvoreB(unittest.TestCase):

    def test_grau_invalido(self):
        with self.assertRaises(ValueError):
            ArvoreB(grau_minimo=1)

    def test_arvore_vazia(self):
        a = ArvoreB()
        self.assertEqual(len(a), 0)
        self.assertEqual(a.altura(), 0)
        self.assertIsNone(a.buscar(1))
        self.assertEqual(a.listar_todos(), [])
        self.assertTrue(a.validar()[0])

    def test_insercao_busca_e_ordem(self):
        for t in (2, 3, 4, 5, 10):
            with self.subTest(grau=t):
                rnd = random.Random(t)
                ids = rnd.sample(range(10000, 100000), 1000)
                a = ArvoreB(grau_minimo=t)
                for i in ids:
                    self.assertTrue(a.inserir(i, registro(i)))
                ok, msg = a.validar()
                self.assertTrue(ok, msg)
                self.assertEqual(len(a), 1000)
                self.assertEqual([c["id"] for c in a.listar_todos()], sorted(ids))
                for i in rnd.sample(ids, 100):
                    self.assertEqual(a.buscar(i)["id"], i)
                self.assertIsNone(a.buscar(5))
                self.assertIsNone(a.buscar(100001))

    def test_insercao_sequencial_crescente_e_decrescente(self):
        for ordem in (range(1, 501), range(500, 0, -1)):
            a = ArvoreB(grau_minimo=3)
            for i in ordem:
                a.inserir(i, registro(i))
            ok, msg = a.validar()
            self.assertTrue(ok, msg)
            self.assertEqual([c["id"] for c in a.listar_todos()], list(range(1, 501)))

    def test_id_duplicado_e_rejeitado(self):
        a = ArvoreB()
        self.assertTrue(a.inserir(10, registro(10)))
        self.assertFalse(a.inserir(10, {"id": 10, "nome": "Outro"}))
        self.assertEqual(len(a), 1)
        self.assertEqual(a.buscar(10)["nome"], "Cliente 10")

    def test_atualizar(self):
        a = ArvoreB(grau_minimo=2)
        for i in range(1, 50):
            a.inserir(i, registro(i))
        nos_antes = a.obter_metricas()["total_nos"]
        self.assertTrue(a.atualizar(25, {"id": 25, "nome": "Alterado"}))
        self.assertEqual(a.buscar(25)["nome"], "Alterado")
        self.assertFalse(a.atualizar(999, registro(999)))
        self.assertEqual(len(a), 49)
        self.assertEqual(a.obter_metricas()["total_nos"], nos_antes)
        self.assertTrue(a.validar()[0])

    def test_chave_aceita_texto_numerico(self):
        a = ArvoreB()
        a.inserir("42", registro(42))
        self.assertIsNotNone(a.buscar(42))
        self.assertIsNotNone(a.buscar("42"))

    def test_primeira_divisao_e_altura(self):
        a = ArvoreB(grau_minimo=3)  # máximo de 5 chaves por nó
        for i in range(1, 6):
            a.inserir(i, registro(i))
        self.assertEqual(a.altura(), 1)
        self.assertEqual(a.total_divisoes, 0)
        a.inserir(6, registro(6))  # raiz cheia: divide e cresce
        self.assertEqual(a.altura(), 2)
        self.assertEqual(a.total_divisoes, 1)
        self.assertEqual(a.raiz.chaves, [3])
        self.assertEqual(a.historico_divisoes[-1]["chave_promovida"], 3)
        self.assertTrue(a.validar()[0])

    def test_altura_respeita_limite_teorico(self):
        import math
        for t in (2, 3, 5):
            a = ArvoreB(grau_minimo=t)
            ids = random.Random(1).sample(range(1, 100000), 1000)
            for i in ids:
                a.inserir(i, registro(i))
            limite = math.log((a.tamanho + 1) / 2, t)
            # altura em níveis = h + 1, onde h <= log_t((n + 1) / 2)
            self.assertLessEqual(a.altura() - 1, limite + 1e-9)

    def test_instrumentacao_de_busca(self):
        a = ArvoreB(grau_minimo=3)
        for i in range(1, 200):
            a.inserir(i, registro(i))
        a.buscar(100)
        ub = a.ultima_busca
        self.assertTrue(ub["encontrada"])
        self.assertEqual(ub["acessos"], len(ub["caminho"]))
        self.assertLessEqual(ub["acessos"], a.altura())
        self.assertGreater(ub["comparacoes"], 0)
        a.buscar(100000)
        self.assertFalse(a.ultima_busca["encontrada"])
        self.assertEqual(a.total_buscas, 2)

    def test_contem_nao_altera_instrumentacao(self):
        a = ArvoreB()
        a.inserir(1, registro(1))
        self.assertTrue(a.contem(1))
        self.assertEqual(a.total_buscas, 0)

    def test_reconstrucao_pela_ordem_de_insercao_e_identica(self):
        ids = random.Random(3).sample(range(1, 100000), 500)
        a = ArvoreB(grau_minimo=3)
        for i in ids:
            a.inserir(i, registro(i))
        a.atualizar(ids[10], {"id": ids[10], "nome": "Alterado"})  # não muda o formato

        b = ArvoreB(grau_minimo=3)
        for reg in a.listar_em_ordem_de_insercao():
            b.inserir(reg["id"], reg)

        self.assertEqual(a.niveis(), b.niveis())
        self.assertEqual(a.total_divisoes, b.total_divisoes)
        self.assertEqual(b.buscar(ids[10])["nome"], "Alterado")
        self.assertTrue(b.validar()[0])

    def test_ordem_de_insercao_ignora_duplicatas(self):
        a = ArvoreB()
        a.inserir(5, registro(5))
        a.inserir(5, registro(5))
        self.assertEqual(a.ordem_insercao, [5])

    def test_validar_detecta_corrupcao(self):
        a = ArvoreB(grau_minimo=2)
        for i in range(1, 30):
            a.inserir(i, registro(i))
        a.raiz.chaves[0] = 9999
        self.assertFalse(a.validar()[0])


if __name__ == "__main__":
    unittest.main()
