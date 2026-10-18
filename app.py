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
    if os.path.exists(PAISES_JSON_PATH):
        try:
            with open(PAISES_JSON_PATH, "r", encoding="utf-8") as f:
                dados = json.load(f)
                for item in dados:
                    if "codigo" in item:
                        tabela_paises.inserir(item["codigo"], item)
        except Exception as e:
            print(f"Erro ao carregar dados de {PAISES_JSON_PATH}: {e}")


def persistir_dados():
    """
    Persiste o estado atual da Tabela Hash de volta no arquivo arquivos/paises.json.
    Executado após operações de cadastro, alteração ou remoção.
    """
    try:
        lista_paises = tabela_paises.listar_todos()
        with open(PAISES_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(lista_paises, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao persistir dados em {PAISES_JSON_PATH}: {e}")


# Carga inicial dos dados
carregar_dados()


# ==============================================================================
# ROTAS DA ETAPA 1
# ==============================================================================

@app.route("/")
def index():
    """Página inicial do GlobalSIM com visão geral e atalhos rápidos."""
    metricas = tabela_paises.obter_metricas()
    return render_template("index.html", metricas=metricas)


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
        if codigo_buscado:
            resultado = tabela_paises.buscar(codigo_buscado)

    return render_template(
        "cobertura.html",
        resultado=resultado,
        codigo=codigo_buscado,
        consultado=consultado
    )


@app.route("/paises")
def paises():
    """Listagem de todos os países atendidos cadastrados na Tabela Hash."""
    lista_paises = tabela_paises.listar_todos()
    return render_template("paises.html", paises=lista_paises)


@app.route("/paises/cadastrar", methods=["POST"])
def cadastrar_pais():
    """
    Cadastra um novo país na Tabela Hash e persiste no JSON.
    Padrão Post/Redirect/Get.
    """
    codigo = request.form.get("codigo", "").strip().upper()
    pais = request.form.get("pais", "").strip()
    regiao = request.form.get("regiao", "").strip()
    operadora = request.form.get("operadora", "").strip()
    tecnologia = request.form.get("tecnologia", "5G").strip().upper()

    if not codigo or not pais or not regiao or not operadora or not tecnologia:
        flash("Todos os campos são obrigatórios para o cadastro!", "danger")
        return redirect(url_for("paises"))

    existente = tabela_paises.buscar(codigo)
    novo_pais = {
        "codigo": codigo,
        "pais": pais,
        "regiao": regiao,
        "operadora": operadora,
        "tecnologia": tecnologia
    }

    tabela_paises.inserir(codigo, novo_pais)
    persistir_dados()

    if existente:
        flash(f"O país com código '{codigo}' já existia e foi atualizado com sucesso!", "info")
    else:
        flash(f"País '{pais}' ({codigo}) cadastrado com sucesso!", "success")

    return redirect(url_for("paises"))


@app.route("/paises/<codigo>/editar", methods=["POST"])
def editar_pais(codigo):
    """
    Atualiza os dados de um país existente na Tabela Hash e persiste no JSON.
    """
    codigo = codigo.strip().upper()
    pais = request.form.get("pais", "").strip()
    regiao = request.form.get("regiao", "").strip()
    operadora = request.form.get("operadora", "").strip()
    tecnologia = request.form.get("tecnologia", "5G").strip().upper()

    if not pais or not regiao or not operadora or not tecnologia:
        flash("Todos os campos são obrigatórios para a edição!", "danger")
        return redirect(url_for("paises"))

    dados_atualizados = {
        "codigo": codigo,
        "pais": pais,
        "regiao": regiao,
        "operadora": operadora,
        "tecnologia": tecnologia
    }

    tabela_paises.inserir(codigo, dados_atualizados)
    persistir_dados()
    flash(f"Dados do país {codigo} ({pais}) atualizados com sucesso!", "success")
    return redirect(url_for("paises"))


@app.route("/paises/<codigo>/excluir", methods=["POST"])
def excluir_pais(codigo):
    """
    Remove um país da Tabela Hash e atualiza o arquivo JSON.
    """
    codigo = codigo.strip().upper()
    removido = tabela_paises.remover(codigo)

    if removido:
        persistir_dados()
        flash(f"País '{codigo}' removido com sucesso!", "warning")
    else:
        flash(f"País com código '{codigo}' não encontrado para remoção.", "danger")

    return redirect(url_for("paises"))


@app.route("/instrumentacao")
def instrumentacao():
    """
    Exibe as métricas de instrumentação interna da Tabela Hash
    (fator de carga, colisões, capacidade e distribuição dos buckets).
    """
    metricas = tabela_paises.obter_metricas()
    return render_template("instrumentacao.html", metricas=metricas)


@app.route("/design-system")
def design_system():
    """Exibe o catálogo visual de tokens, cores e componentes do GlobalSIM."""
    return render_template("design_system.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
