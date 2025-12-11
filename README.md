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

## 📸 Interface do Sistema

Abaixo, uma visualização da simulação em execução, demonstrando a interação entre os nós (espécies) e o painel de controle.

<img width="1098" height="724" alt="BioNexus-Simulator" src="https://github.com/user-attachments/assets/7f442b84-c3c4-4154-80a4-99a78d02a88a" /><br>

*Visualização gráfica gerada via PyGame com layout de força (spring layout) do NetworkX.*

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

## 🛠️ Instalação e Execução

### Pré-requisitos
Você precisará de Python instalado e das bibliotecas listadas.

1. Clone o repositório:
   ```bash
   git clone [https://github.com/eduardofelipe0/Projeto-Biologia-Computacional.git](https://github.com/eduardofelipe0/Projeto-Biologia-Computacional.git)
   cd Projeto-Biologia-Computacional
