"""
Testes de integração das rotas Flask da Etapa 3 (rede, cache e consulta integrada).
Os arquivos JSON são copiados para uma pasta temporária: os dados reais não são alterados.
Execução: python -m unittest discover -s tests -v
"""

import json
import os
import shutil
import tempfile
import unittest

import app as globalsim


class TestRotasEtapa3(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.mkdtemp()
        origem = os.path.dirname(globalsim.PAISES_JSON_PATH)
        for nome in ("paises.json", "clientes.json", "pacotes.json", "rede.json"):
            shutil.copy(os.path.join(origem, nome), cls.pasta)
        cls.originais = (globalsim.PAISES_JSON_PATH, globalsim.CLIENTES_JSON_PATH,
                         globalsim.REDE_JSON_PATH)
        globalsim.PAISES_JSON_PATH = os.path.join(cls.pasta, "paises.json")
        globalsim.CLIENTES_JSON_PATH = os.path.join(cls.pasta, "clientes.json")
        globalsim.REDE_JSON_PATH = os.path.join(cls.pasta, "rede.json")

    @classmethod
    def tearDownClass(cls):
        (globalsim.PAISES_JSON_PATH, globalsim.CLIENTES_JSON_PATH,
         globalsim.REDE_JSON_PATH) = cls.originais
        shutil.rmtree(cls.pasta, ignore_errors=True)

    def setUp(self):
        self.client = globalsim.app.test_client()
        globalsim.cache_rotas.limpar()

    def test_paginas_carregam(self):
        for url in ("/", "/rede", "/cache", "/consulta", "/rede?bfs=BR", "/rede?dfs=PT",
                    "/rede?de=BR&para=IT", "/cobertura", "/paises", "/clientes", "/arvore-b"):
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_vertices_sao_os_paises_da_tabela_hash(self):
        paises = sorted(p["codigo"] for p in globalsim.tabela_paises.listar_todos())
        self.assertEqual(globalsim.grafo_rede.vertices(), paises)

    def test_consulta_integrada_exemplo_do_enunciado(self):
        html = self.client.get("/consulta?cliente=58372&origem=BR&destino=IT").data.decode()
        self.assertIn("Maria Silva", html)
        self.assertIn("185 ms", html)
        self.assertIn("Conectividade disponível", html)
        self.assertIn("CACHE MISS", html)
        html = self.client.get("/consulta?cliente=58372&origem=BR&destino=IT").data.decode()
        self.assertIn("CACHE HIT", html)

    def test_consulta_integrada_pendencias(self):
        html = self.client.get("/consulta?cliente=58372&origem=BR&destino=US").data.decode()
        self.assertIn("não cobre", html)                       # pacote europeu x América
        html = self.client.get("/consulta?cliente=58372&origem=BR&destino=ZZ").data.decode()
        self.assertIn("não é atendido", html)
        html = self.client.get("/consulta?cliente=58372&origem=ZZ&destino=IT").data.decode()
        self.assertIn("A origem &#39;ZZ&#39; não é atendida", html)

    def test_alterar_aresta_invalida_cache_e_persiste(self):
        self.client.get("/rede?de=BR&para=IT")
        self.assertEqual(len(globalsim.cache_rotas), 1)
        r = self.client.post("/rede/arestas/salvar", data={"origem": "BR", "destino": "FR", "latencia": "10"})
        self.assertEqual(r.status_code, 302)                   # Post/Redirect/Get
        self.assertEqual(len(globalsim.cache_rotas), 0)
        with open(globalsim.REDE_JSON_PATH, encoding="utf-8") as f:
            arestas = json.load(f)["arestas"]
        self.assertIn({"origem": "BR", "destino": "FR", "latencia": 10}, arestas)
        res = globalsim.servico_rotas.consultar("BR", "IT")
        self.assertEqual((res["latencia"], res["caminho"]), (35, ["BR", "FR", "IT"]))
        # desfaz
        self.client.post("/rede/arestas/remover", data={"origem": "BR", "destino": "FR"})
        self.assertEqual(globalsim.servico_rotas.consultar("BR", "IT")["latencia"], 185)

    def test_aresta_invalida_e_rejeitada(self):
        antes = len(globalsim.grafo_rede.arestas())
        for dados in ({"origem": "BR", "destino": "BR", "latencia": "5"},
                      {"origem": "BR", "destino": "IT", "latencia": "-3"},
                      {"origem": "BR", "destino": "XX", "latencia": "5"},
                      {"origem": "BR", "destino": "IT", "latencia": "abc"}):
            self.assertEqual(self.client.post("/rede/arestas/salvar", data=dados).status_code, 302)
        self.assertEqual(len(globalsim.grafo_rede.arestas()), antes)

    def test_get_nao_altera_dados(self):
        self.assertEqual(self.client.get("/rede/arestas/salvar").status_code, 405)
        self.assertEqual(self.client.get("/cache/limpar").status_code, 405)

    def test_pais_novo_vira_vertice_e_remocao_invalida_rotas(self):
        self.client.post("/paises/cadastrar", data={
            "codigo": "AR", "pais": "Argentina", "regiao": "América",
            "operadora": "Claro AR", "tecnologia": "5G"})
        self.assertTrue(globalsim.grafo_rede.tem_vertice("AR"))
        self.client.post("/rede/arestas/salvar", data={"origem": "AR", "destino": "BR", "latencia": "40"})
        self.assertEqual(globalsim.servico_rotas.consultar("AR", "IT")["latencia"], 225)
        self.client.get("/rede?de=BR&para=JP")
        self.assertEqual(len(globalsim.cache_rotas), 2)

        self.client.post("/paises/AR/excluir")
        self.assertFalse(globalsim.grafo_rede.tem_vertice("AR"))
        self.assertEqual({e["chave"] for e in globalsim.cache_rotas.entradas()}, {"BR->JP"})
        with open(globalsim.REDE_JSON_PATH, encoding="utf-8") as f:
            arestas = json.load(f)["arestas"]
        self.assertFalse(any("AR" in (a["origem"], a["destino"]) for a in arestas))

    def test_configurar_limpar_e_benchmark(self):
        for rota in ("BR-IT", "BR-JP", "ES-PT"):
            u, v = rota.split("-")
            globalsim.servico_rotas.consultar(u, v)
        self.client.post("/cache/configurar", data={"capacidade": "2", "ttl": "0"})
        self.assertEqual((globalsim.cache_rotas.capacidade, len(globalsim.cache_rotas)), (2, 2))
        self.client.post("/cache/configurar", data={"capacidade": "0", "ttl": "0"})
        self.assertEqual(globalsim.cache_rotas.capacidade, 2)  # valor inválido ignorado
        self.client.post("/cache/configurar", data={"capacidade": "8", "ttl": "0"})
        self.client.post("/cache/limpar")
        self.assertEqual(len(globalsim.cache_rotas), 0)
        r = self.client.post("/cache/benchmark", data={"quantidade": "200", "semente": "3"})
        self.assertEqual(r.status_code, 302)
        self.assertIn("Resultado: sem cache", self.client.get("/cache").data.decode())
        self.assertEqual(len(globalsim.cache_rotas), 0)        # benchmark não toca no cache real


if __name__ == "__main__":
    unittest.main()
