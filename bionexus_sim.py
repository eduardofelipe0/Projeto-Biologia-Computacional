"""
BioNexus – Simulador de Redes Biológicas

Requisitos atendidos:
- Modelagem por grafos direcionados (NetworkX)
- Arestas com pesos entre -1 e +1 (efeito benéfico ou prejudicial)
- Simulação discreta baseada em estados:
    Novo_Estado(n) = Estado_Atual(n) + α * Σ (peso(u->n) * Estado(u))
- Interface gráfica interativa (PyGame)
- Gráfico de histórico de estados (Matplotlib)
- Jogador pode:
    * Ativar/inativar espécies (extinção / reintrodução)
    * Ativar/inativar interações de um nó
    * Aplicar perturbações (seca, doença, parasitas, invasora)
    * Simular passo a passo e observar cascatas na rede
"""

import math
import random
import sys

import matplotlib.pyplot as plt
import networkx as nx
import pygame

# ---------------- CONFIGURAÇÕES BÁSICAS ---------------- #

WIDTH, HEIGHT = 1100, 700
NODE_RADIUS = 28
FPS = 60

# Controle de câmera
camera_offset_x = 0
camera_offset_y = 0
zoom = 1.0
dragging = False
last_mouse_pos = (0, 0)


# fator de escala da equação (para o sistema não explodir):
# Novo = Atual + ALPHA * Σ( peso * estado_origem )
ALPHA = 0.10

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BioNexus – Redes Biológicas")
FONT_SMALL = pygame.font.SysFont("arial", 14)
FONT_MED = pygame.font.SysFont("arial", 18)
FONT_BIG = pygame.font.SysFont("arial", 22, bold=True)


# ---------------- 1. CRIAÇÃO DO GRAFO ---------------- #

def create_ecosystem_graph() -> nx.DiGraph:
    G = nx.DiGraph()

    # Cada nó possui:
    # - state: 0 a 100 (saúde/abundância)
    # - active: espécie está ativa na rede?
    # - role: papel ecológico
    # - history: lista com a evolução do estado ao longo do tempo

    def add_species(name, state, role):
        G.add_node(
            name,
            state=float(state),
            active=True,
            role=role,
            history=[float(state)]
        )

    # Espécies iniciais (pode ajustar para o bioma que quiser)
    add_species("Capim", 80, "Produtor")
    add_species("Flores", 70, "Produtor")
    add_species("Abelha", 60, "Polinizador / Mutualista")
    add_species("Coelho", 50, "Herbívoro")
    add_species("Rato", 45, "Herbívoro")
    add_species("Raposa", 40, "Carnívoro")
    add_species("Carrapato", 30, "Parasita")

    # Arestas direcionadas: source -> target com peso entre -1 e +1
    def add_interaction(src, tgt, weight):
        G.add_edge(src, tgt, weight=float(weight), enabled=True)

    # Herbivoria (efeito negativo sobre produtor, leve positivo indireto no herbívoro)
    add_interaction("Coelho", "Capim", -0.6)
    add_interaction("Rato", "Capim", -0.4)

    # Predação forte
    add_interaction("Raposa", "Coelho", -0.9)
    add_interaction("Raposa", "Rato", -0.8)

    # Parasitismo
    add_interaction("Carrapato", "Raposa", -0.7)
    add_interaction("Carrapato", "Coelho", -0.5)

    # Mutualismo (Abelha <-> Flores)
    add_interaction("Abelha", "Flores", +0.6)
    add_interaction("Flores", "Abelha", +0.4)

    # Cooperação / dispersão de sementes (Coelho ajudando a espalhar sementes de Flores)
    add_interaction("Coelho", "Flores", +0.2)

    # Competição leve entre Coelho e Rato
    add_interaction("Coelho", "Rato", -0.3)
    add_interaction("Rato", "Coelho", -0.3)

    return G


G = create_ecosystem_graph()
time_step = 0

# Layout inicial do grafo (posições normalizadas)
raw_pos = nx.spring_layout(G, seed=42)
positions = {}
for node, (x, y) in raw_pos.items():
    px = int(150 + x * (WIDTH - 300))
    py = int(120 + y * (HEIGHT - 250))
    positions[node] = (px, py)


# ---------------- 2. SIMULAÇÃO DISCRETA ---------------- #

def simulate_step(G: nx.DiGraph):
    """Atualiza o estado de cada nó usando a regra discreta baseada em estados."""
    global time_step
    time_step += 1

    new_states = {}

    for node in G.nodes:
        data = G.nodes[node]

        if not data["active"]:
            new_states[node] = 0.0
            continue

        current_state = data["state"]
        influence_sum = 0.0

        # Somatório das arestas ENTRANTES (pais -> node)
        for parent, _, attrs in G.in_edges(node, data=True):
            if not G.nodes[parent]["active"]:
                continue
            if not attrs.get("enabled", True):
                continue

            parent_state = G.nodes[parent]["state"]
            weight = attrs["weight"]
            influence_sum += weight * (parent_state / 100.0)

        # Equação principal (com ALPHA para estabilizar):
        # Novo = Atual + ALPHA * Σ( peso * estado_origem )
        new_state = current_state + ALPHA * influence_sum * 100.0

        # tendência leve a retornar para 50 (estabilidade)
        regulacao = -0.03 * (current_state - 50.0)
        new_state += regulacao

        # Limites
        new_state = max(0.0, min(100.0, new_state))

        # Extinção se cair abaixo de 5
        if new_state <= 5.0:
            new_state = 0.0
            data["active"] = False

        new_states[node] = new_state

    # Aplica e salva no histórico
    for node, st in new_states.items():
        G.nodes[node]["state"] = st
        G.nodes[node]["history"].append(st)


# ---------------- 3. PERTURBAÇÕES / EVENTOS ---------------- #

def apply_event(G: nx.DiGraph, event_name: str):
    """Aplica uma perturbação global na rede."""
    print(f"Aplicando evento: {event_name}")

    if event_name == "seca":
        # Secas afetam principalmente produtores
        for n, data in G.nodes(data=True):
            if "Produtor" in data["role"]:
                data["state"] *= 0.6

    elif event_name == "doenca_herbivoros":
        for n, data in G.nodes(data=True):
            if "Herbívoro" in data["role"]:
                data["state"] *= 0.5

    elif event_name == "explosao_parasitas":
        for n, data in G.nodes(data=True):
            if "Parasita" in data["role"]:
                data["state"] = min(100.0, data["state"] * 1.5)

    elif event_name == "invasora_gato":
        if "Gato_domestico" not in G.nodes:
            G.add_node(
                "Gato_domestico",
                state=65.0,
                active=True,
                role="Carnívoro invasor",
                history=[65.0],
            )
            # predando pequenos vertebrados
            for tgt in ["Coelho", "Rato", "Passaro"]:
                if tgt in G.nodes:
                    G.add_edge("Gato_domestico", tgt, weight=-0.8, enabled=True)

            # posição aproximada à direita
            positions["Gato_domestico"] = (WIDTH - 150, HEIGHT // 2)
        else:
            print("Espécie invasora já está presente.")

    # atualiza histórico pós-perturbação
    for node in G.nodes:
        G.nodes[node]["history"].append(G.nodes[node]["state"])


# ---------------- 4. FERRAMENTAS GRÁFICAS ---------------- #

def draw_text(surface, text, x, y, color=(255, 255, 255), font=FONT_SMALL):
    img = font.render(text, True, color)
    surface.blit(img, (x, y))


def draw_panel():
    """Desenha um painel lateral com informações do sistema."""
    pygame.draw.rect(screen, (15, 15, 15), (0, 0, WIDTH, 60))
    pygame.draw.rect(screen, (20, 20, 20), (0, HEIGHT - 120, WIDTH, 120))

    draw_text(screen, "BioNexus – Redes Biológicas (NetworkX + PyGame + Matplotlib)", 15, 10, (255, 255, 0), FONT_BIG)
    draw_text(screen, f"Passo de tempo: {time_step}", 15, 40, (200, 200, 200), FONT_MED)

    controls = [
        "[ESPACO] 1 passo de simulação",
        "[R]      Rodar 10 passos",
        "[Clique] Seleciona espécie",
        "[E]      Ativar/Inativar espécie",
        "[X]      Ativar/Inativar interações que chegam na espécie",
        "[S]      Evento: SECA (produtores)",
        "[D]      Evento: doença herbívoros",
        "[P]      Evento: explosão de PARASITAS",
        "[I]      Evento: espécie invasora (Gato doméstico)",
        "[G]      Mostrar gráfico de histórico (Matplotlib)",
        "[ESC]    Sair",
    ]
    y = HEIGHT - 110
    for c in controls:
        draw_text(screen, c, 15, y)
        y += 18


def state_color(state: float, active: bool):
    """Cor do nó em função do estado."""
    if not active:
        return (90, 90, 90)
    # verde = saudável, vermelho = crítico
    g = int(min(255, max(0, state * 2.3)))
    r = int(min(255, max(0, 255 - state * 2.0)))
    return (r, g, 60)


def draw_graph(G: nx.DiGraph, selected: str | None):
    screen.fill((25, 25, 25))

    # área do grafo
    pygame.draw.rect(screen, (30, 30, 30), (0, 60, WIDTH, HEIGHT - 180))

    # --- Funções internas auxiliares --- #
    def transform_point(x, y):
        """Aplica zoom + deslocamento da câmera."""
        x = (x * zoom) + camera_offset_x
        y = (y * zoom) + camera_offset_y
        return int(x), int(y)

    # --- Desenhar arestas --- #
    for u, v, data in G.edges(data=True):
        x1, y1 = positions.get(u, (0, 0))
        x2, y2 = positions.get(v, (0, 0))

        x1, y1 = transform_point(x1, y1)
        x2, y2 = transform_point(x2, y2)

        color = (220, 70, 70) if data.get("weight", 0) < 0 else (70, 210, 100)
        if not data.get("enabled", True):
            color = (90, 90, 90)

        pygame.draw.line(screen, color, (x1, y1), (x2, y2), 2)

        # seta da direção
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist > 0:
            ux, uy = dx/dist, dy/dist
            ax = x2 - ux * 18
            ay = y2 - uy * 18
            left = (ax + -uy * 7, ay + ux * 7)
            right = (ax - -uy * 7, ay - ux * 7)
            pygame.draw.polygon(screen, color, [(ax, ay), left, right])

    # --- Desenhar nós --- #
    for node, (x, y) in positions.items():
        if node not in G.nodes:
            continue

        nx, ny = transform_point(x, y)
        data = G.nodes[node]
        state = data["state"]
        active = data["active"]

        col = state_color(state, active)
        pygame.draw.circle(screen, col, (nx, ny), int(NODE_RADIUS * zoom))
        border = (255, 255, 0) if node == selected else (0, 0, 0)
        pygame.draw.circle(screen, border, (nx, ny), int(NODE_RADIUS * zoom), 3)

        label = f"{node} ({int(state)})"
        text_img = FONT_SMALL.render(label, True, (255, 255, 255))
        rect = text_img.get_rect(center=(nx, ny - int(40 * zoom)))
        screen.blit(text_img, rect)

    draw_panel()


    # Mostrar info detalhada do nó selecionado
    if selected and selected in G.nodes:
        data = G.nodes[selected]
        info_lines = [
            f"Espécie selecionada: {selected}",
            f"Estado (0-100): {data['state']:.1f}",
            f"Ativa: {data['active']}",
            f"Papel ecológico: {data['role']}",
        ]
        y = 70
        for line in info_lines:
            draw_text(screen, line, WIDTH - 400, y, (230, 230, 230), FONT_MED)
            y += 22


def get_node_at_position(pos) -> str | None:
    mx, my = pos

    # Converter o clique da tela para coordenadas do grafo (inverso)
    gx = (mx - camera_offset_x) / zoom
    gy = (my - camera_offset_y) / zoom

    for node, (x, y) in positions.items():
        if math.hypot(gx - x, gy - y) <= NODE_RADIUS:
            return node

    return None



# ---------------- 5. FUNÇÕES AUXILIARES DE JOGO ---------------- #

def toggle_species(G: nx.DiGraph, node: str):
    if node not in G.nodes:
        return
    G.nodes[node]["active"] = not G.nodes[node]["active"]
    if not G.nodes[node]["active"]:
        G.nodes[node]["state"] = 0.0
    else:
        # reativa com estado mínimo
        if G.nodes[node]["state"] <= 0:
            G.nodes[node]["state"] = 10.0
    print(f"Espécie {node} agora {'ATIVA' if G.nodes[node]['active'] else 'INATIVA'}")


def toggle_incoming_edges(G: nx.DiGraph, node: str):
    """Ativa/inativa todas as interações que chegam no nó (como se removesse predação, mutualismo etc.)."""
    if node not in G.nodes:
        return
    for u, v, data in G.in_edges(node, data=True):
        data["enabled"] = not data.get("enabled", True)
    print(f"Interações que CHEGAM em {node} foram {'ativadas' if data.get('enabled', True) else 'desativadas'}.")


def show_history_plot(G: nx.DiGraph):
    """Abre um gráfico Matplotlib com o histórico de estados de cada espécie."""
    plt.figure(figsize=(10, 6))
    for node, data in G.nodes(data=True):
        hist = data.get("history", [])
        if not hist:
            continue
        plt.plot(hist, label=node)
    plt.xlabel("Passo de tempo")
    plt.ylabel("Estado / Abundância")
    plt.title("Histórico de estados dos nós da rede")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# ---------------- 6. LOOP PRINCIPAL ---------------- #

def main():
    global time_step
    clock = pygame.time.Clock()
    running = True
    selected_node: str | None = None

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            global camera_offset_x, camera_offset_y, zoom, dragging, last_mouse_pos

            # -------------------------
            # ZOOM DO MOUSE (scroll)
            # -------------------------
            if event.type == pygame.MOUSEWHEEL:
                zoom += event.y * 0.1
                zoom = max(0.2, min(3.0, zoom))  # limites

            # -------------------------
            # INICIAR ARRASTE (PAN)
            # botão direito = 3
            # -------------------------
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    dragging = True
                    last_mouse_pos = event.pos

                # clique esquerdo continua selecionando nó
                if event.button == 1:
                    node = get_node_at_position(event.pos)
                    if node:
                        selected_node = node

            # -------------------------
            # PARAR ARRASTE
            # -------------------------
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    dragging = False

            # -------------------------
            # MOVER A CÂMERA (PAN)
            # -------------------------
            if event.type == pygame.MOUSEMOTION and dragging:
                mx, my = event.pos
                lx, ly = last_mouse_pos
                dx = mx - lx
                dy = my - ly
                camera_offset_x += dx
                camera_offset_y += dy
                last_mouse_pos = event.pos

            # -------------------------
            # FECHAR JOGO
            # -------------------------
            if event.type == pygame.QUIT:
                running = False

            # -------------------------
            # TECLAS DO JOGO
            # -------------------------
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                # Simulação
                if event.key == pygame.K_SPACE:
                    simulate_step(G)
                if event.key == pygame.K_r:
                    for _ in range(10):
                        simulate_step(G)

                # Ativar/inativar espécie selecionada
                if event.key == pygame.K_e and selected_node:
                    toggle_species(G, selected_node)

                # Ativar/inativar interações que chegam no nó selecionado
                if event.key == pygame.K_x and selected_node:
                    toggle_incoming_edges(G, selected_node)

                # Eventos ecológicos
                if event.key == pygame.K_s:
                    apply_event(G, "seca")
                if event.key == pygame.K_d:
                    apply_event(G, "doenca_herbivoros")
                if event.key == pygame.K_p:
                    apply_event(G, "explosao_parasitas")
                if event.key == pygame.K_i:
                    apply_event(G, "invasora_gato")

                # Gráfico de histórico
                if event.key == pygame.K_g:
                    show_history_plot(G)

                

                

            draw_graph(G, selected_node)
            pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
