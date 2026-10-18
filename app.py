import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash

from estruturas.tabela_hash import TabelaHash
from estruturas.recomendador import recomendar_pacote

app = Flask(__name__)
app.secret_key = "globalsim-ed2-secret-key"

PAISES_JSON_PATH = os.path.join(os.path.dirname(__file__), "arquivos", "paises.json")
PACOTES_JSON_PATH = os.path.join(os.path.dirname(__file__), "arquivos", "pacotes.json")

# Inicialização da Tabela Hash em memória
tabela_paises = TabelaHash(capacidade_inicial=17)
pacotes_cadastrados = []


def carregar_dados_iniciais():
    """Carrega os dados persistidos em JSON para a Tabela Hash e estruturas em memória."""
    global pacotes_cadastrados

    if os.path.exists(PAISES_JSON_PATH):
        try:
            with open(PAISES_JSON_PATH, "r", encoding="utf-8") as f:
                paises = json.load(f)
                for p in paises:
                    tabela_paises.inserir(p["codigo"], p)
        except Exception as e:
            print(f"Erro ao carregar paises.json: {e}")

    if os.path.exists(PACOTES_JSON_PATH):
        try:
            with open(PACOTES_JSON_PATH, "r", encoding="utf-8") as f:
                pacotes_cadastrados = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar pacotes.json: {e}")


def persistir_paises():
    """Salva o estado atual da Tabela Hash de volta no arquivo JSON."""
    dados = tabela_paises.listar_todos()
    try:
        with open(PAISES_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao persistir paises.json: {e}")


# Executa a carga inicial na subida da aplicação
carregar_dados_iniciais()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cobertura", methods=["GET", "POST"])
def consulta_cobertura():
    codigo = None
    resultado = None
    consultado = False

    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip().upper()
        if codigo:
            consultado = True
            resultado = tabela_paises.buscar(codigo)

    return render_template(
        "cobertura.html",
        consultado=consultado,
        codigo_consultado=codigo,
        resultado=resultado,
    )


@app.route("/paises")
def listar_paises():
    paises = tabela_paises.listar_todos()
    # Ordenação simples para apresentação visual
    paises.sort(key=lambda x: x.get("pais", ""))
    return render_template("paises.html", paises=paises)


@app.route("/paises/cadastrar", methods=["POST"])
def cadastrar_pais():
    codigo = request.form.get("codigo", "").strip().upper()
    nome = request.form.get("pais", "").strip()
    regiao = request.form.get("regiao", "").strip()
    operadora = request.form.get("operadora", "").strip()
    tecnologia = request.form.get("tecnologia", "5G").strip()

    if not codigo or not nome:
        flash("Código e Nome do país são obrigatórios.", "danger")
        return redirect(url_for("listar_paises"))

    if tabela_paises.buscar(codigo) is not None:
        flash(f"O país com código {codigo} já está cadastrado.", "warning")
        return redirect(url_for("listar_paises"))

    novo_pais = {
        "codigo": codigo,
        "pais": nome,
        "regiao": regiao,
        "operadora": operadora,
        "tecnologia": tecnologia,
    }

    tabela_paises.inserir(codigo, novo_pais)
    persistir_paises()
    flash(f"País {nome} ({codigo}) cadastrado com sucesso!", "success")
    return redirect(url_for("listar_paises"))


@app.route("/paises/<codigo>/editar", methods=["POST"])
def editar_pais(codigo):
    codigo = codigo.strip().upper()
    pais_existente = tabela_paises.buscar(codigo)

    if not pais_existente:
        flash(f"País {codigo} não encontrado.", "danger")
        return redirect(url_for("listar_paises"))

    nome = request.form.get("pais", "").strip()
    regiao = request.form.get("regiao", "").strip()
    operadora = request.form.get("operadora", "").strip()
    tecnologia = request.form.get("tecnologia", "").strip()

    dados_atualizados = {
        "codigo": codigo,
        "pais": nome or pais_existente.get("pais"),
        "regiao": regiao or pais_existente.get("regiao"),
        "operadora": operadora or pais_existente.get("operadora"),
        "tecnologia": tecnologia or pais_existente.get("tecnologia"),
    }

    tabela_paises.inserir(codigo, dados_atualizados)
    persistir_paises()
    flash(f"Dados do país {codigo} atualizados com sucesso!", "success")
    return redirect(url_for("listar_paises"))


@app.route("/paises/<codigo>/excluir", methods=["POST"])
def excluir_pais(codigo):
    codigo = codigo.strip().upper()
    sucesso = tabela_paises.remover(codigo)
    if sucesso:
        persistir_paises()
        flash(f"País {codigo} removido com sucesso.", "info")
    else:
        flash(f"Não foi possível remover o país {codigo}.", "warning")
    return redirect(url_for("listar_paises"))


@app.route("/instrumentacao")
def instrumentacao():
    metricas = tabela_paises.obter_metricas()
    return render_template("instrumentacao.html", metricas=metricas)


@app.route("/recomendador", methods=["GET", "POST"])
def tela_recomendador():
    todos_paises = sorted(tabela_paises.listar_todos(), key=lambda x: x.get("pais", ""))
    recomendacao = None
    selecionados = []
    dias = 15
    perfil = "Moderado"

    if request.method == "POST":
        selecionados = request.form.getlist("paises_selecionados")
        dias = int(request.form.get("dias", 15))
        perfil = request.form.get("perfil", "Moderado")

        if not selecionados:
            flash("Selecione pelo menos um país para analisar o roteiro.", "warning")
        else:
            recomendacao = recomendar_pacote(
                roteiro_paises=selecionados,
                dias_viagem=dias,
                perfil_uso=perfil,
                tabela_hash=tabela_paises,
                pacotes=pacotes_cadastrados,
            )

    return render_template(
        "recomendador.html",
        todos_paises=todos_paises,
        recomendacao=recomendacao,
        selecionados=selecionados,
        dias=dias,
        perfil=perfil,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
