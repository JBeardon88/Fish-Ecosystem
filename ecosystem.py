# ecosystem.py
import pygame
from Fish import Prey, Predator

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COLS = 20
GRID_ROWS = 15

# SECTION 1: PYGAME INITIALIZATION
# --------------------------------
pygame.init()

# SECTION 2: DISPLAY SETUP
# ------------------------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Predator-Prey Simulation")

# SECTION 3: AGENT INITIALIZATION
# -------------------------------
agents = [Prey() for _ in range(10)]  # 10 prey
agents.extend(Predator() for _ in range(20))  # 10 predators

# SECTION 4: MAIN GAME LOOP
# -------------------------
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update agent states
    predators = [agent for agent in agents if isinstance(agent, Predator)]
    prey = [agent for agent in agents if isinstance(agent, Prey)]

    for agent in agents[:]:  # Iterate over a copy of the list
        if isinstance(agent, Prey):
            agent.update(agents, predators)
        elif isinstance(agent, Predator):
            agent.update(agents, prey)

    # SECTION 5: DRAWING
    screen.fill((255, 255, 255))  # Clear the screen with a white background

    # Draw grid lines
    for x in range(0, SCREEN_WIDTH, SCREEN_WIDTH // GRID_COLS):
        pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, SCREEN_HEIGHT // GRID_ROWS):
        pygame.draw.line(screen, (200, 200, 200), (0, y), (SCREEN_WIDTH, y))

    # Draw agents
    for agent in agents:
        if isinstance(agent, Prey):
            color = (0, 255, 0)  # Green for prey
        else:
            color = (255, 0, 0)  # Red for predator
        pygame.draw.circle(screen, color, (int(agent.position[0]), int(agent.position[1])), 5)

    # SECTION 6: DISPLAY REFRESH
    # --------------------------
    pygame.display.flip()

# SECTION 7: QUIT PYGAME
# ----------------------
pygame.quit()
