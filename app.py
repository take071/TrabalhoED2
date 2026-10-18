"""
Aplicação Principal - GlobalSIM
Disciplina: Estruturas de Dados II - UNEB
Docente: Profa. Maria Inés Restovic
Equipe: Arthur Felipe, Lucas Vinicius, Raphael Lopes

Descrição:
Controlador Web utilizando Flask. Gerencia as rotas, renderização de templates Jinja
e integração com as estruturas de dados puras implementadas no diretório 'estruturas/'.

Regras do Trabalho:
- Não utilizar listas ou dicionários em substituição às estruturas de dados principais.
- Rotas que modificam dados devem utilizar o método POST (padrão Post/Redirect/Get).
- Carregar dados dos arquivos JSON nas estruturas em memória na inicialização.
- Persistir alterações de volta aos arquivos JSON.
"""

import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash

from estruturas.tabela_hash import TabelaHash
# Imports das próximas etapas:
# from estruturas.arvore_b import ArvoreB
# from estruturas.grafo import GrafoRede
# from estruturas.recomendador import recomendar_pacote

app = Flask(__name__)
app.secret_key = "globalsim-ed2-secret-key"

# Caminhos dos arquivos de persistência JSON
PAISES_JSON_PATH = os.path.join(os.path.dirname(__file__), "arquivos", "paises.json")
PACOTES_JSON_PATH = os.path.join(os.path.dirname(__file__), "arquivos", "pacotes.json")
CLIENTES_JSON_PATH = os.path.join(os.path.dirname(__file__), "arquivos", "clientes.json")
REDE_JSON_PATH = os.path.join(os.path.dirname(__file__), "arquivos", "rede.json")

# Instância da Tabela Hash em memória (Etapa 1)
tabela_paises = TabelaHash(capacidade_inicial=17)


def carregar_dados():
    """
    Carrega os dados persistidos nos arquivos JSON diretamente para as estruturas em memória.
    Executado na inicialização da aplicação.
    """
    # TODO: Ler arquivos/paises.json e inserir cada registro na Tabela Hash (tabela_paises.inserir)
    pass


def persistir_dados():
    """
    Extrai os dados da Tabela Hash em memória e salva no arquivo JSON correspondente.
    Executado após operações de inserção, alteração ou exclusão.
    """
    # TODO: Obter registros da Tabela Hash (tabela_paises.listar_todos) e salvar em arquivos/paises.json
    pass


# Carga inicial na inicialização
carregar_dados()


# ==============================================================================
# ROTAS - PÁGINA INICIAL E CONSULTA DE COBERTURA
# ==============================================================================

@app.route("/")
def index():
    """Página inicial com dashboard de apresentação do sistema GlobalSIM."""
    return render_template("index.html")


@app.route("/cobertura", methods=["GET", "POST"])
def cobertura():
    """
    Consulta de cobertura por código internacional do país (ex: "IT", "BR").
    A busca deve ser realizada diretamente na Tabela Hash em tempo O(1).
    """
    resultado = None
    codigo_buscado = ""
    consultado = False

    if request.method == "POST":
        consultado = True
        codigo_buscado = request.form.get("codigo", "").strip().upper()
        # TODO: Realizar a busca na Tabela Hash: resultado = tabela_paises.buscar(codigo_buscado)

    return render_template("cobertura.html", resultado=resultado, codigo=codigo_buscado, consultado=consultado)


# ==============================================================================
# ROTAS - GERENCIAMENTO DE PAÍSES (ETAPA 1)
# ==============================================================================

@app.route("/paises")
def paises():
    """Listagem de todos os países atendidos cadastrados na Tabela Hash."""
    # TODO: Obter lista completa de países da Tabela Hash
    lista_paises = []
    return render_template("paises.html", paises=lista_paises)


@app.route("/paises/cadastrar", methods=["POST"])
def cadastrar_pais():
    """
    Cadastra um novo país atendido na Tabela Hash e persiste no JSON.
    Segue o padrão Post/Redirect/Get.
    """
    # TODO: Coletar dados do formulário (codigo, nome, regiao, operadora, tecnologia)
    # TODO: Inserir na Tabela Hash e chamar persistir_dados()
    flash("País cadastrado com sucesso!", "success")
    return redirect(url_for("paises"))


@app.route("/paises/<codigo>/editar", methods=["POST"])
def editar_pais(codigo):
    """
    Atualiza os dados de um país existente na Tabela Hash e persiste no JSON.
    """
    # TODO: Atualizar registro na Tabela Hash e chamar persistir_dados()
    flash(f"País {codigo} atualizado com sucesso!", "success")
    return redirect(url_for("paises"))


@app.route("/paises/<codigo>/excluir", methods=["POST"])
def excluir_pais(codigo):
    """
    Remove um país da Tabela Hash e atualiza o arquivo JSON.
    """
    # TODO: Remover país da Tabela Hash e chamar persistir_dados()
    flash(f"País {codigo} removido com sucesso!", "info")
    return redirect(url_for("paises"))


@app.route("/instrumentacao")
def instrumentacao():
    """
    Painel de instrumentação para inspeção das estruturas de dados.
    Permite observar o estado interno da Tabela Hash (buckets, colisões, fator de carga).
    """
    # TODO: Obter métricas da estrutura: metricas = tabela_paises.obter_metricas()
    metricas = {}
    return render_template("instrumentacao.html", metricas=metricas)


# ==============================================================================
# ROTAS - DIFERENCIAL (RECOMENDAÇÃO DE PACOTES POR ROTEIRO)
# ==============================================================================

@app.route("/recomendador", methods=["GET", "POST"])
def recomendador():
    """
    Interface para montagem de roteiro de viagem e recomendação de pacote.
    Integra a Tabela Hash, Grafo e regras de pacotes de dados.
    """
    # TODO: Implementar fluxo de recomendação com base no roteiro selecionado
    return render_template("recomendador.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
