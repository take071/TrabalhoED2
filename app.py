"""
Aplicação Principal - GlobalSIM (Etapa 1)
Disciplina: Estruturas de Dados II - UNEB
Docente: Profa. Maria Inés Restovic
Equipe: Arthur Felipe, Lucas Vinicius, Raphael Lopes

Escopo da Etapa 1:
- Tabela Hash própria para gerenciamento dos países atendidos.
- Consulta rápida de cobertura por código do país (ex: "BR", "IT").
- CRUD completo de países atendidos com persistência em arquivos/paises.json.
- Painel de instrumentação básica da estrutura (capacidade, colisões, fator de carga).
- Rotas de alteração de dados utilizando método POST (padrão Post/Redirect/Get).
"""

import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash

from estruturas.tabela_hash import TabelaHash

app = Flask(__name__)
app.secret_key = "globalsim-ed2-secret-key"

# Caminho para o arquivo de persistência dos países (Etapa 1)
PAISES_JSON_PATH = os.path.join(os.path.dirname(__file__), "arquivos", "paises.json")

# Instância da Tabela Hash em memória
tabela_paises = TabelaHash(capacidade_inicial=17)


def carregar_dados():
    """
    Carrega os dados de arquivos/paises.json para a Tabela Hash em memória.
    Executado na inicialização da aplicação.
    """
    # TODO: Ler arquivos/paises.json e inserir cada registro na Tabela Hash
    pass


def persistir_dados():
    """
    Persiste o estado atual da Tabela Hash de volta no arquivo arquivos/paises.json.
    Executado após operações de cadastro, alteração ou remoção.
    """
    # TODO: Extrair registros da Tabela Hash e salvar em arquivos/paises.json
    pass


# Carga inicial dos dados
carregar_dados()


# ==============================================================================
# ROTAS DA ETAPA 1
# ==============================================================================

@app.route("/")
def index():
    """Página inicial do GlobalSIM."""
    return render_template("index.html")


@app.route("/cobertura", methods=["GET", "POST"])
def cobertura():
    """
    Consulta de cobertura por código de país (ex: "BR", "IT").
    A verificação deve ser feita diretamente na Tabela Hash em tempo O(1).
    """
    resultado = None
    codigo_buscado = ""
    consultado = False

    if request.method == "POST":
        consultado = True
        codigo_buscado = request.form.get("codigo", "").strip().upper()
        # TODO: Buscar na Tabela Hash: resultado = tabela_paises.buscar(codigo_buscado)

    return render_template(
        "cobertura.html",
        resultado=resultado,
        codigo=codigo_buscado,
        consultado=consultado
    )


@app.route("/paises")
def paises():
    """Listagem de todos os países atendidos cadastrados na Tabela Hash."""
    # TODO: Obter lista de países da Tabela Hash: lista_paises = tabela_paises.listar_todos()
    lista_paises = []
    return render_template("paises.html", paises=lista_paises)


@app.route("/paises/cadastrar", methods=["POST"])
def cadastrar_pais():
    """
    Cadastra um novo país na Tabela Hash e persiste no JSON.
    Padrão Post/Redirect/Get.
    """
    # TODO: Obter dados do formulário (codigo, pais, regiao, operadora, tecnologia)
    # TODO: Inserir na Tabela Hash e chamar persistir_dados()
    flash("País cadastrado com sucesso!", "success")
    return redirect(url_for("paises"))


@app.route("/paises/<codigo>/editar", methods=["POST"])
def editar_pais(codigo):
    """
    Atualiza os dados de um país existente na Tabela Hash e persiste no JSON.
    """
    # TODO: Atualizar registro na Tabela Hash e chamar persistir_dados()
    flash(f"Dados do país {codigo} atualizados com sucesso!", "success")
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
    Exibe as métricas de instrumentação interna da Tabela Hash
    (fator de carga, colisões, capacidade e distribuição dos buckets).
    """
    # TODO: Obter métricas da estrutura: metricas = tabela_paises.obter_metricas()
    metricas = {}
    return render_template("instrumentacao.html", metricas=metricas)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
