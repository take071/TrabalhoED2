import unittest
from unittest.mock import patch

import app as globalsim_app
from estruturas.arvore_b import ArvoreB
from estruturas.tabela_hash import TabelaHash


class TestCadastroPais(unittest.TestCase):

    def setUp(self):
        globalsim_app.app.config["TESTING"] = True
        self.client = globalsim_app.app.test_client()
        self.tabela_original = globalsim_app.tabela_paises
        globalsim_app.tabela_paises = TabelaHash(capacidade_inicial=17)

    def tearDown(self):
        globalsim_app.tabela_paises = self.tabela_original

    def test_pagina_de_paises_abre_sem_dados_de_formulario(self):
        resposta = self.client.get("/paises")

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Cadastrar Pa\xc3\xads na Rede", resposta.data)

    @patch.object(globalsim_app.geolocator, "geocode", return_value=None)
    def test_pais_nao_encontrado_nao_e_cadastrado(self, geocode):
        resposta = self.client.post(
            "/paises/cadastrar",
            data={
                "codigo": "XY",
                "pais": "Welington",
                "regiao": "Europa",
                "operadora": "Operadora teste",
                "tecnologia": "4G/LTE",
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Pa\xc3\xads inexistente", resposta.data)
        self.assertIn(b"is-invalid", resposta.data)
        self.assertIn(b'value="Welington"', resposta.data)
        self.assertIn(b"modalCadastrar')).show()", resposta.data)
        self.assertIsNone(globalsim_app.tabela_paises.buscar("XY"))
        geocode.assert_called_once_with("Welington", featuretype="country")


class TestEtapa2IntegracaoFlask(unittest.TestCase):

    def setUp(self):
        globalsim_app.app.config["TESTING"] = True
        self.client = globalsim_app.app.test_client()
        self.tabela_original = globalsim_app.tabela_paises
        self.arvore_original = globalsim_app.arvore_clientes

        globalsim_app.tabela_paises = TabelaHash(capacidade_inicial=17)
        for p in [
            {
                "codigo": "IT",
                "pais": "Itália",
                "regiao": "Europa",
                "operadora": "TIM / Vodafone IT",
                "tecnologia": "5G",
                "lat": 41.8719,
                "lon": 12.5674,
            },
            {
                "codigo": "US",
                "pais": "Estados Unidos",
                "regiao": "Américas",
                "operadora": "T-Mobile / AT&T",
                "tecnologia": "5G",
                "lat": 37.0902,
                "lon": -95.7129,
            },
            {
                "codigo": "JP",
                "pais": "Japão",
                "regiao": "Ásia",
                "operadora": "NTT Docomo",
                "tecnologia": "5G",
                "lat": 36.2048,
                "lon": 138.2529,
            },
        ]:
            globalsim_app.tabela_paises.inserir(p["codigo"], p)

        globalsim_app.arvore_clientes = ArvoreB(grau_minimo=3)
        globalsim_app.arvore_clientes.inserir(58372, {
            "id": 58372,
            "nome": "Maria Silva",
            "email": "maria@email.com",
            "esim": "ESIM-83921",
            "pacote": 102,
            "status": "ativo",
        })

    def tearDown(self):
        globalsim_app.tabela_paises = self.tabela_original
        globalsim_app.arvore_clientes = self.arvore_original

    def test_rotas_principais_retornam_200(self):
        for rota in ("/", "/cobertura", "/paises", "/instrumentacao", "/clientes", "/consulta", "/arvore-b"):
            with self.subTest(rota=rota):
                resp = self.client.get(rota)
                self.assertEqual(resp.status_code, 200)

    def test_normalizacao_regiao_pacotes(self):
        pacote_america = {"codigo": 201, "nome": "América Basic", "regiao": "América"}
        pacote_global = {"codigo": 301, "nome": "Global", "regiao": "Global"}
        self.assertTrue(globalsim_app.pacote_cobre_regiao(pacote_america, "Américas"))
        self.assertTrue(globalsim_app.pacote_cobre_regiao(pacote_america, "america"))
        self.assertTrue(globalsim_app.pacote_cobre_regiao(pacote_global, "Ásia"))
        self.assertFalse(globalsim_app.pacote_cobre_regiao(pacote_america, "Europa"))

    def test_busca_cliente_na_rota_clientes(self):
        resp = self.client.get("/clientes?id=58372")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Maria Silva", resp.data)
        self.assertIn(b"ESIM-83921", resp.data)

    def test_filtro_seletivo_por_id_parcial_sem_vazar_esim(self):
        # 10332 tem '9' apenas no eSIM (ESIM-79456); 58372 tem '9' apenas no eSIM (ESIM-83921);
        # 10991 tem '9' no próprio ID.
        globalsim_app.arvore_clientes.inserir(10332, {
            "id": 10332,
            "nome": "Ana Santos",
            "email": "ana.santos10332@mail.com",
            "esim": "ESIM-79456",
            "pacote": 301,
            "status": "ativo",
        })
        globalsim_app.arvore_clientes.inserir(10991, {
            "id": 10991,
            "nome": "Daniel Dias",
            "email": "daniel.dias10991@mail.com",
            "esim": "ESIM-19111",
            "pacote": 301,
            "status": "ativo",
        })

        resp = self.client.get("/clientes?campo=id&q=9")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'data-id="10991"', resp.data)
        self.assertNotIn(b'data-id="10332"', resp.data)
        self.assertNotIn(b'data-id="58372"', resp.data)
        self.assertNotIn(b"ESIM-79456", resp.data)

    def test_filtro_seletivo_por_nome_email_e_esim_isolados(self):
        globalsim_app.arvore_clientes.inserir(10991, {
            "id": 10991,
            "nome": "Daniel Dias",
            "email": "daniel.dias10991@mail.com",
            "esim": "ESIM-19111",
            "pacote": 301,
            "status": "ativo",
        })

        # Nome não casa com ID ou eSIM
        r_nome = self.client.get("/clientes?campo=nome&q=Maria")
        self.assertEqual(r_nome.status_code, 200)
        self.assertIn(b'data-id="58372"', r_nome.data)
        self.assertNotIn(b'data-id="10991"', r_nome.data)

        r_nome_id = self.client.get("/clientes?campo=nome&q=58372")
        self.assertEqual(r_nome_id.status_code, 200)
        self.assertIn(b"Nenhum cliente encontrado com esses filtros.", r_nome_id.data)
        self.assertNotIn(b'data-id="58372"', r_nome_id.data)

        # eSIM casa só com eSIM
        r_esim = self.client.get("/clientes?campo=esim&q=19111")
        self.assertEqual(r_esim.status_code, 200)
        self.assertIn(b'data-id="10991"', r_esim.data)
        self.assertNotIn(b'data-id="58372"', r_esim.data)

        # E-mail casa só com e-mail
        r_email = self.client.get("/clientes?campo=email&q=maria@email.com")
        self.assertEqual(r_email.status_code, 200)
        self.assertIn(b'data-id="58372"', r_email.data)
        self.assertNotIn(b'data-id="10991"', r_email.data)

    @patch.object(globalsim_app, "persistir_clientes")
    def test_cadastro_edicao_e_associacao_cliente(self, mock_persistir):
        # Cadastro (POST + PRG -> 302)
        resp_cad = self.client.post(
            "/clientes/cadastrar",
            data={"id": "77777", "nome": "Carlos Lima", "email": "carlos@email.com", "pacote": ""},
        )
        self.assertEqual(resp_cad.status_code, 302)
        cliente = globalsim_app.arvore_clientes.buscar(77777)
        self.assertIsNotNone(cliente)
        self.assertEqual(cliente["status"], "pendente")

        # Associação de eSIM e pacote
        resp_assoc = self.client.post(
            "/clientes/77777/associar",
            data={"pacote": "301", "esim": "ESIM-77777"},
        )
        self.assertEqual(resp_assoc.status_code, 302)
        cliente = globalsim_app.arvore_clientes.buscar(77777)
        self.assertEqual(cliente["pacote"], 301)
        self.assertEqual(cliente["esim"], "ESIM-77777")
        self.assertEqual(cliente["status"], "ativo")

        # Edição de dados
        resp_edit = self.client.post(
            "/clientes/77777/editar",
            data={"nome": "Carlos Eduardo Lima", "email": "carlos.edu@email.com", "status": "suspenso"},
        )
        self.assertEqual(resp_edit.status_code, 302)
        cliente = globalsim_app.arvore_clientes.buscar(77777)
        self.assertEqual(cliente["nome"], "Carlos Eduardo Lima")
        self.assertEqual(cliente["status"], "suspenso")
        self.assertEqual(mock_persistir.call_count, 3)

    def test_consulta_integrada_compativel_e_incompativel(self):
        # 58372 (Europa Plus) -> IT (Europa): conectividade disponível
        resp_ok = self.client.get("/consulta?cliente=58372&destino=IT")
        self.assertEqual(resp_ok.status_code, 200)
        self.assertIn(b"Conectividade dispon", resp_ok.data)
        self.assertIn(b"Maria Silva", resp_ok.data)

        # 58372 (Europa Plus) -> US (Américas): incompatível
        resp_inc = self.client.get("/consulta?cliente=58372&destino=US")
        self.assertEqual(resp_inc.status_code, 200)
        self.assertIn(b"Conectividade indispon", resp_inc.data)

        # Também aceita POST
        resp_post = self.client.post("/consulta", data={"cliente": "58372", "destino": "IT"})
        self.assertEqual(resp_post.status_code, 200)
        self.assertIn(b"Conectividade dispon", resp_post.data)


if __name__ == "__main__":
    unittest.main()
