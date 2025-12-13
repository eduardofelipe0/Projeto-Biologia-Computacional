# BioNexus Project: Simulação de Redes Ecológicas 🌿🦁

> Um simulador interativo de dinâmicas populacionais baseado em teoria dos grafos.

Este projeto foi desenvolvido como parte da avaliação da disciplina de **Biologia Computacional**. O software modela um ecossistema através de grafos direcionados, permitindo a visualização em tempo real de como perturbações (secas, doenças, espécies invasoras) se propagam através da teia alimentar.

---

## 📚 Informações Acadêmicas

| Campo | Detalhe |
| :--- | :--- |
| **Disciplina** | Biologia Computacional |
| **Instituição** | Universidade Federal Rural de Pernmabuco |
| **Docente** | Profa. Jeane Melo |
| **Estudantes** | • Bruno Rezende<br>• Eduardo Silva<br>• Rogério Júnior |

---

## 🚀 Funcionalidades

O **BioNexus** combina visualização gráfica com simulação matemática discreta:

* **Modelagem por Grafos (NetworkX):** Espécies são nós e interações são arestas ponderadas.
* **Interações Complexas:** Suporta Predação (-), Parasitismo (-), Mutualismo (+) e Competição.
* **Simulação Discreta:** Cálculo passo a passo da saúde/abundância de cada espécie.
* **Interface Interativa (PyGame):** Visualização da rede com suporte a **Zoom** e **Pan** (arrastar câmera).
* **Perturbações em Tempo Real:** O usuário pode inserir eventos catastróficos ou introduzir espécies invasoras durante a execução.
* **Análise de Dados:** Geração de gráficos de histórico (Matplotlib) para análise de tendências populacionais.

## 🧮 O Modelo Matemático

A simulação utiliza um modelo de atualização de estados discreto. A saúde (ou abundância) de uma espécie $n$ no tempo $t+1$ é dada por:

$$Estado_{t+1}(n) = Estado_t(n) + \alpha \cdot \sum (peso_{u \to n} \cdot Estado_t(u))$$

Onde:
* **$\alpha$ (Alpha):** Fator de escala para estabilidade do sistema.
* **$peso$:** Valor entre -1 (prejudicial) e +1 (benéfico) da interação.
* **Regulação:** O sistema possui uma leve tendência de retorno ao equilíbrio para evitar explosão numérica imediata.

---

## 🎮 Controles e Comandos

A interface gráfica permite interação total via teclado e mouse:

### Navegação e Simulação
* **Mouse Scroll:** Zoom In / Zoom Out.
* **Botão Direito (Segurar + Arrastar):** Move a câmera (Pan).
* **Espaço:** Avança **1 passo** de tempo.
* **Tecla R:** Avança **10 passos** rapidamente.
* **Tecla G:** Abre o gráfico de histórico (Matplotlib).

### Intervenção no Ecossistema
* **Clique Esquerdo:** Seleciona uma espécie (nó).
* **Tecla E:** Ativar/Extinguir a espécie selecionada.
* **Tecla X:** Ativar/Desativar interações que chegam na espécie selecionada (isola o nó).

### Eventos (Perturbações)
* **Tecla S:** Simula uma **Seca** (afeta Produtores).
* **Tecla D:** Simula **Doença** (afeta Herbívoros).
* **Tecla P:** Explosão populacional de **Parasitas**.
* **Tecla I:** Introduz espécie **Invasora** (Gato Doméstico).

---

## ⚙️ Funcionamento do Simulador

Esta seção detalha a arquitetura, o modelo matemático e a interação do usuário com o simulador **BioNexus**.

### 1. O Modelo de Simulação Discreta

O BioNexus é um simulador de dinâmica populacional baseado na **Teoria dos Grafos**, implementado utilizando a biblioteca `NetworkX` para a estrutura de dados e `PyGame` para a interface gráfica.

#### 1.1. Estrutura da Rede (Grafo)

*   **Vértices (Nós):** Representam as **Espécies** no ecossistema. Cada nó armazena atributos essenciais:
    *   `state`: O estado atual da espécie, variando de **0 a 100**, representando sua saúde ou abundância.
    *   `active`: Um booleano que indica se a espécie está ativa na simulação.
    *   `role`: O papel ecológico da espécie (e.g., Produtor, Carnívoro, Parasita).
    *   `history`: Uma lista que registra a evolução do `state` ao longo do tempo.
*   **Arestas (Interações):** Representam as **Interações Ecológicas** (e.g., predação, mutualismo). São direcionadas (de $u$ para $v$) e possuem um atributo crucial:
    *   `weight`: Um valor real entre **-1.0 e +1.0**, que quantifica o impacto da espécie de origem ($u$) na espécie de destino ($v$). Valores negativos indicam relações prejudiciais (predação, parasitismo), e positivos indicam relações benéficas (mutualismo, cooperação).

#### 1.2. Comportamento das Espécies (Regra de Atualização)

O comportamento de cada espécie é regido por uma regra de atualização de estado discreta, executada a cada "passo de tempo" (função `simulate_step`). O novo estado de uma espécie $n$ no tempo $t+1$ é calculado com base em seu estado atual e na soma das influências de todas as espécies que interagem com ela (arestas entrantes).

A fórmula completa, incluindo o fator de regulação, é:

$$Estado_{t+1}(n) = Estado_t(n) + \alpha \cdot \sum_{u \to n} \left(peso_{u \to n} \cdot \frac{Estado_t(u)}{100}\right) \cdot 100 + Regulação$$

Onde:
*   **$\alpha$ (Alpha):** É o fator de escala (`ALPHA = 0.10` no código), que modera a velocidade de mudança do sistema, garantindo estabilidade.
*   **$\sum_{u \to n}$:** O somatório de todas as influências recebidas pela espécie $n$.
*   **Regulação:** Um termo de estabilização (`-0.03 * (current\_state - 50.0)`) que aplica uma leve pressão para que o estado da espécie retorne ao valor de equilíbrio (50.0), prevenindo a explosão ou o colapso numérico imediato.

**Extinção:** Se o `state` de uma espécie cair abaixo de **5.0**, ela é automaticamente marcada como inativa (`active=False`) e seu estado é fixado em 0.0.

### 2. Interface e Interação do Usuário

#### 2.1. O que são os números ao lado dos vértices?

Os números entre parênteses ao lado do nome de cada espécie (e.g., `Coelho (50)`) representam o valor do atributo `state` da espécie, ou seja, sua **Saúde/Abundância** atual na escala de 0 a 100.

A cor do nó também é um indicador visual direto desse estado:
*   **Verde:** Estado alto (saudável/abundante).
*   **Vermelho/Marrom:** Estado baixo (crítico/em declínio).
*   **Cinza:** Espécie inativa (extinta).

#### 2.2. Seleção de Espécie e Controles

Para interagir com uma espécie específica, o usuário deve **selecioná-la** clicando com o **Botão Esquerdo** do mouse sobre o nó. O nó selecionado é destacado com um contorno amarelo.

| Ação | Tecla | Detalhamento do Efeito |
| :--- | :--- | :--- |
| **Ativar/Inativar Espécie** | `[E]` | Alterna o atributo `active` da espécie selecionada. Inativar simula a **extinção** (estado = 0, sem influência). Ativar simula a **reintrodução** (o estado volta a ser calculado). |
| **Ativar/Inativar Interações** | `[X]` | Alterna o atributo `enabled` de **todas as arestas que chegam** na espécie selecionada. Isso simula o **isolamento** da espécie, impedindo que ela receba influência de outras espécies, mas permitindo que ela continue a influenciar as espécies das quais é predadora, parasita ou mutualista. |

#### 2.3. O que acontece ao rodar dez passos?

Ao pressionar a tecla `[R]`, o simulador executa a função `simulate_step` **dez vezes** consecutivas. Isso permite que o usuário observe a evolução do ecossistema em um período de tempo maior de forma rápida, acelerando a propagação dos efeitos de uma perturbação ou evento.

### 3. Eventos e Perturbações

Os eventos são perturbações globais que alteram o estado inicial de um grupo específico de espécies, simulando desastres naturais ou introduções.

| Evento | Tecla | Espécies Afetadas | Efeito no Estado |
| :--- | :--- | :--- | :--- |
| **Seca** | `[S]` | Produtores (e.g., Capim, Flores) | Redução de 40% no estado (`state *= 0.6`). |
| **Doença** | `[D]` | Herbívoros (e.g., Coelho, Rato) | Redução de 50% no estado (`state *= 0.5`). |
| **Explosão de Parasitas** | `[P]` | Parasitas (e.g., Carrapato) | Aumento de 50% no estado, limitado a 100 (`state *= 1.5`). |
| **Espécie Invasora** | `[I]` | Criação de um novo nó (e.g., "Gato_domestico") | Adiciona a espécie ao grafo com interações predatórias definidas via código. |

### 4. Histórico e Análise de Dados

O simulador registra o estado de cada espécie a cada passo de tempo no atributo `history` do nó.

#### 4.1. Geração do Histórico

Ao pressionar a tecla `[G]`, o simulador utiliza a biblioteca `Matplotlib` para gerar um gráfico de linhas que exibe a evolução do estado (`state`) de todas as espécies ativas ao longo do tempo (eixo X: Passo de tempo, eixo Y: Estado/Abundância).

Este recurso é essencial para a **Análise de Tendências**, permitindo que o usuário visualize o impacto a longo prazo de um evento ou intervenção no ecossistema.

A imagem a seguir ilustra um exemplo de histórico gerado, mostrando a dinâmica de extinção do Coelho e do Rato sob a pressão da Raposa e do Carrapato, enquanto as Flores e a Abelha prosperam devido ao mutualismo:

<img width="1000" height="600" alt="Figure_1" src="https://github.com/user-attachments/assets/580b1828-ac1d-412e-b636-998f4e45eb4a" />

### 5. Configuração Inicial e Adição de Novas Espécies

#### 5.1. Escolha do Grafo Inicial

O grafo inicial é **pré-carregado** diretamente no código-fonte, dentro da função `create_ecosystem_graph`. Esta abordagem garante que o simulador inicie com um ecossistema funcional e complexo, com espécies e interações definidas.

O grafo padrão inclui:
*   **Espécies:** Capim, Flores, Abelha, Coelho, Rato, Raposa, Carrapato.
*   **Interações:** Predação, Parasitismo, Mutualismo e Competição, cada uma com um `weight` específico.

#### 5.2. Adição de uma Nova Espécie (Diretamente no Código)

Sim, a adição de novas espécies é feita **diretamente no código-fonte** (`bionexus_sim.py`). Para adicionar uma nova espécie, o desenvolvedor deve:

1.  **Adicionar o Nó:** Chamar a função auxiliar `add_species` dentro de `create_ecosystem_graph` (linhas 63-70), definindo o nome, estado inicial e papel ecológico.
    ```python
    add_species("Nova_Especie", 50, "Novo Papel")
    ```
2.  **Definir Interações:** Chamar a função auxiliar `add_interaction` (linhas 82-83) para criar as arestas de entrada e saída, definindo o `weight` de cada interação.
    ```python
    # Nova_Especie preda Coelho
    add_interaction("Nova_Especie", "Coelho", -0.7)
    # Nova_Especie é predada pela Raposa
    add_interaction("Raposa", "Nova_Especie", -0.5)
    ```
3.  **Definir Posição (Opcional):** Embora o layout inicial seja gerado automaticamente, para garantir a posição de espécies adicionadas dinamicamente (como a invasora), é necessário adicionar uma entrada no dicionário `positions`.

### 6. Principais Funções do Código (`bionexus_sim.py`)

O código é estruturado em blocos lógicos, com as seguintes funções principais:

| Função | Linhas | Descrição |
| :--- | :--- | :--- |
| `create_ecosystem_graph()` | 54-108 | **Inicialização do Grafo.** Define as espécies (nós) e suas interações (arestas) com pesos e papéis ecológicos. |
| `simulate_step(G)` | 125-175 | **Motor da Simulação.** Aplica a regra de atualização de estado discreta a todos os nós do grafo e registra o novo estado no histórico. |
| `apply_event(G, event_name)` | 179-221 | **Gerenciador de Perturbações.** Aplica os efeitos de eventos (Seca, Doença, etc.) alterando o estado de grupos específicos de espécies. |
| `draw_graph(G, selected)` | 267-366 | **Renderização Gráfica.** Utiliza `PyGame` para desenhar os nós, as arestas (com cores indicando o peso) e a seta de direção, aplicando zoom e deslocamento da câmera. |
| `show_history(G)` | 369-391 | **Análise de Dados.** Utiliza `Matplotlib` para gerar e exibir o gráfico de histórico de estados. |
| `get_node_at_pos(pos)` | 394-405 | **Interação do Usuário.** Detecta qual nó foi clicado pelo mouse, permitindo a seleção de espécies. |

### 7. Imagem da Interface

A imagem a seguir mostra a interface do simulador no passo de tempo 0, destacando a visualização do grafo e o painel de controles na parte inferior.

<img width="1097" height="726" alt="Captura de tela 2025-12-12 212317" src="https://github.com/user-attachments/assets/9c2de7c6-3108-4337-bf0b-422108a46b43" />

## 🛠️ Instalação e Execução

### Pré-requisitos
Você precisará de Python instalado e das bibliotecas listadas.

1. Clone o repositório:
   ```bash
   git clone [https://github.com/eduardofelipe0/Projeto-Biologia-Computacional.git](https://github.com/eduardofelipe0/Projeto-Biologia-Computacional.git)
   cd Projeto-Biologia-Computacional
