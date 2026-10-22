"""
Testes Unitários da Tabela Hash com Encadeamento Separado
Disciplina: Estruturas de Dados II - UNEB
"""

import unittest
from estruturas.tabela_hash import TabelaHash, NoHash


class TestTabelaHash(unittest.TestCase):

    def setUp(self):
        """Instancia uma nova Tabela Hash antes de cada teste com M=17."""
        self.tabela = TabelaHash(capacidade_inicial=17)

    def test_insercao_e_busca(self):
        """Testa inserção simples e busca O(1)."""
        dados_br = {"codigo": "BR", "pais": "Brasil", "operadora": "Vivo"}
        self.tabela.inserir("BR", dados_br)

        resultado = self.tabela.buscar("BR")
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["pais"], "Brasil")
        self.assertEqual(self.tabela.tamanho, 1)

    def test_busca_chave_inexistente(self):
        """Testa busca por chave que não existe na tabela."""
        resultado = self.tabela.buscar("ZZ")
        self.assertIsNone(resultado)

    def test_normalizacao_case_insensitive(self):
        """Testa se a chave em minúsculas é convertida e encontrada em maiúsculas."""
        self.tabela.inserir("fr", {"codigo": "FR", "pais": "França"})
        self.assertIsNotNone(self.tabela.buscar("FR"))
        self.assertIsNotNone(self.tabela.buscar("fr"))

    def test_atualizacao_sem_duplicata(self):
        """Testa atualização de registro existente sem contar colisão nem alterar tamanho."""
        self.tabela.inserir("BR", {"codigo": "BR", "pais": "Brasil", "operadora": "Vivo"})
        self.tabela.inserir("BR", {"codigo": "BR", "pais": "Brasil", "operadora": "Claro"})

        resultado = self.tabela.buscar("BR")
        self.assertEqual(resultado["operadora"], "Claro")
        self.assertEqual(self.tabela.tamanho, 1)
        self.assertEqual(self.tabela.total_colisoes, 0)

    def test_tratamento_de_colisao(self):
        """
        Testa colisão real no Bucket 01 entre 'IT' (Itália) e 'DE' (Alemanha).
        Ambas possuem hash 1 no módulo 17.
        """
        self.assertEqual(self.tabela._hash("IT"), 1)
        self.assertEqual(self.tabela._hash("DE"), 1)

        self.tabela.inserir("IT", {"codigo": "IT", "pais": "Itália"})
        self.assertEqual(self.tabela.total_colisoes, 0)

        # Inserção de chave com mesmo hash deve incrementar colisões e encadear
        self.tabela.inserir("DE", {"codigo": "DE", "pais": "Alemanha"})
        self.assertEqual(self.tabela.total_colisoes, 1)
        self.assertEqual(self.tabela.tamanho, 2)

        # Ambas devem ser recuperáveis independentemente
        res_it = self.tabela.buscar("IT")
        res_de = self.tabela.buscar("DE")
        self.assertIsNotNone(res_it)
        self.assertIsNotNone(res_de)
        self.assertEqual(res_it["pais"], "Itália")
        self.assertEqual(res_de["pais"], "Alemanha")

    def test_remocao_simples(self):
        """Testa remoção de chave isolada em um bucket."""
        self.tabela.inserir("CA", {"codigo": "CA", "pais": "Canadá"})
        removido = self.tabela.remover("CA")

        self.assertTrue(removido)
        self.assertEqual(self.tabela.tamanho, 0)
        self.assertIsNone(self.tabela.buscar("CA"))

    def test_remocao_com_religamento_de_ponteiros(self):
        """Testa remoção em bucket com colisão (preserva elementos encadeados)."""
        self.tabela.inserir("IT", {"codigo": "IT", "pais": "Itália"})
        self.tabela.inserir("DE", {"codigo": "DE", "pais": "Alemanha"})

        # Remove o primeiro nó do bucket (IT)
        removido = self.tabela.remover("IT")
        self.assertTrue(removido)
        self.assertEqual(self.tabela.tamanho, 1)

        # O segundo nó (DE) ainda deve ser encontrado
        self.assertIsNone(self.tabela.buscar("IT"))
        self.assertIsNotNone(self.tabela.buscar("DE"))

    def test_metricas_instrumentacao(self):
        """Testa geração de métricas para a interface."""
        self.tabela.inserir("BR", {"codigo": "BR", "pais": "Brasil"})
        metricas = self.tabela.obter_metricas()

        self.assertEqual(metricas["capacidade"], 17)
        self.assertEqual(metricas["tamanho"], 1)
        self.assertGreater(metricas["fator_carga"], 0)
        self.assertEqual(len(metricas["distribuicao_buckets"]), 17)


if __name__ == "__main__":
    unittest.main()

