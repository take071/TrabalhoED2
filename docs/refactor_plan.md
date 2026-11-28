# Plano de Refatoração da Árvore B

## 1️⃣ Visão geral
Este documento descreve **o estado atual** da implementação da árvore B em `arvore_b.py` e **o que a implementação deverá fazer após a refatoração**, seguindo o padrão clássico de **índice apenas com IDs + ponteiro para o registro completo no armazenamento persistente**.

---

## 2️⃣ O que o código faz hoje (comportamento atual)
| Componente | Função atual |
|------------|--------------|
| `NoB.valores` | Armazena **o dicionário completo** de cada cliente (todas as propriedades lidas do JSON). |
| `ArvoreB.inserir(chave, valor)` | Insere na árvore a chave (ID) **e** o registro inteiro (`valor`). |
| `ArvoreB.buscar(chave)` | Usa `_localizar` para encontrar o nó e o índice e devolve `no.valores[i]`, ou seja, já tem o cliente em memória. |
| `ArvoreB.atualizar(chave, valor)` | Substitui o dicionário diretamente em `no.valores[i]`. |
| `ArvoreB.listar_todos()` / `listar_em_ordem_de_insercao()` | Percorre a árvore e retorna **todos os dicionários** armazenados. |

**Consequência:** Ao carregar o JSON (em outra parte do projeto) todos os registros são inseridos na árvore, fazendo com que **todo o conjunto de clientes resida na RAM**. Em cenários com milhares ou milhões de clientes isso pode consumir muita memória e tornar a inicialização lenta.

---

## 3️⃣ Problema identificado
1. **Alto consumo de memória** – cada cliente pode ter vários campos; armazenar tudo simultaneamente não escala.
2. **Redução de I/O** – se o usuário só quer saber se o ID existe, a leitura completa do registro é desnecessária.
3. **Inconsistência potencial** – alteração feita diretamente no dicionário em memória pode divergir do arquivo JSON se o arquivo for reescrito sem atualizar a árvore.

---

## 4️⃣ O padrão recomendado (índice + ponteiro)
1. **Árvore B contém apenas**
   - `chaves` → IDs dos clientes (ordenação normal).
   - `pontos` → ponteiro para o registro no JSON (byte‑offset, número da linha ou outro identificador).   
2. **O arquivo JSON continua como fonte única** dos registros completos.
3. **Operações**
   - **Existe?** – `buscar` (ou `existe`) verifica a presença da chave usando apenas a árvore.
   - **Obter registro** – novo método `obter_registro(chave)` usa o ponteiro armazenado para ler **somente** aquele registro do disco e devolvê‑lo ao chamador.
   - **Atualizar** – grava o novo registro no JSON (sobreescrevendo ou usando um mecanismo de log) e atualiza o ponteiro, sem tocar nos outros registros.
   - **Listar** – pode ainda percorrer a árvore, mas em vez de devolver os dicionários devolve **os ponteiros**; quem precisar dos dados pode carregá‑los sob demanda.

---

## 5️⃣ Passos detalhados da refatoração
| Etapa | Descrição | Arquivo(s) afetado(s) |
|------|-----------|----------------------|
| **5.1** | **Adicionar campo `pontos` ao nó** – substituir `valores` por `pontos`. | `arvore_b.py` (classe `NoB`). |
| **5.2** | **Atualizar assinatura de `inserir`** para receber `ponteiro` (ex.: `offset` ou `linha`). Ajustar chamadas nas rotinas de carregamento do JSON. | `arvore_b.py` (método `inserir`). |
| **5.3** | **Criar função de leitura do JSON sob demanda** – `def _ler_registro_por_ponteiro(self, ponteiro) -> dict`. Usa `open(..., 'rb')` + `seek` ou `linecache.getline` conforme o tipo de ponteiro. | Novo método em `ArvoreB`. |
| **5.4** | **Renomear/Dividir `buscar`** – criar `existe(chave) -> bool` que só verifica presença, e `obter_registro(chave) -> dict` que usa `_localizar` + `_ler_registro_por_ponteiro`. | `arvore_b.py` (métodos novos). |
| **5.5** | **Adaptar `atualizar`** – reescreve o registro no JSON (ex.: sobrescreve a linha ou usa um arquivo temporário) e mantém o mesmo ponteiro (ou gera novo se o tamanho mudar). |
| **5.6** | **Atualizar métodos de listagem** – `listar_todos` passa a devolver lista de ponteiros ou opcionalmente ler cada registro sob demanda (param `carregar=False`). |
| **5.7** | **Modificar a rotina de carga inicial** (provavelmente em outro módulo) para percorrer o JSON linha a linha, registrar o **offset/linha** e chamar `arvore.inserir(id, offset)`. |
| **5.8** | **Testes** – atualizar/ criar testes unitários que cobrem: existência, leitura sob demanda, atualização, persistência correta do ponteiro. |
| **5.9** | **Documentação** – atualizar docstrings e README explicando o novo fluxo (índice + ponteiro). |

---

## 6️⃣ Impactos esperados
- **Memória:** Redução significativa – a árvore guarda apenas duas listas de inteiros (IDs e ponteiros).
- **Tempo de inicialização:** Mais rápido, porque não há necessidade de deserializar todos os dicionários.
- **Latência de leitura de registro:** Um pequeno custo de I/O quando o registro for solicitado; pode ser mitigado com cache LRU opcional.
- **Consistência:** O JSON permanece a **fonte de verdade**; alterações são sempre refletidas nele antes de atualizar o índice.

---

## 7️⃣ Checklist de verificação pós‑refatoração
- [ ] `NoB` tem `pontos` (lista de inteiros) e **não** tem mais `valores`.
- [ ] `inserir` recebe `ponteiro` e armazena em `pontos`.
- [ ] `existe(chave)` retorna `True/False` sem ler o JSON.
- [ ] `obter_registro(chave)` devolve o dicionário correto lendo a partir do ponteiro.
- [ ] `atualizar(chave, novo_dict)` sobrescreve o registro no JSON e mantém o ponteiro válido.
- [ ] Todos os testes antigos passam **e** novos testes de leitura sob demanda passam.
- [ ] Documentação atualizada com exemplos de uso.

---

## 8️⃣ Próximos passos sugeridos
1. **Implementar** as etapas 5.1 → 5.4 em um branch separado.
2. **Executar** a suite de testes existente para garantir que nada quebrou.
3. **Adicionar** novos testes de cache opcional e de carga de grande volume (p.ex., 100 k clientes).
4. **Revisar** a rotina de persistência do JSON (pode ser substituída por um pequeno banco SQLite / TinyDB, caso o offset‑por‑linha se torne problemático).

---

*Este plano pode ser ajustado conforme necessidades específicas do projeto ou conforme outras dependências do código que ainda não foram analisadas.*
