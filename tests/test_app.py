import unittest
from unittest.mock import patch

import app as globalsim_app
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


if __name__ == "__main__":
    unittest.main()