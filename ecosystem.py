import pygame
from Fish import Prey, Predator
from gui_utils import draw_text, draw_button, is_button_clicked  # Make sure to create gui_utils.py as per previous instructions

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

# Font setup for GUI
font = pygame.font.SysFont(None, 36)  # For counters
button_font = pygame.font.SysFont(None, 30)  # For buttons

# Reset button properties
reset_button_pos = (SCREEN_WIDTH - 110, 10)
reset_button_size = (100, 40)
button_color = (0, 128, 0)  # Green button
text_color = (255, 255, 255)  # White text

# SECTION 3: AGENT INITIALIZATION
# -------------------------------
def reset_agents():
    return [Prey() for _ in range(10)] + [Predator() for _ in range(20)]

agents = reset_agents()

# SECTION 4: MAIN GAME LOOP
# -------------------------
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if is_button_clicked(event.pos, reset_button_pos, reset_button_size):
                agents = reset_agents()  # Reset the simulation

    # Update agent states
    predators = [agent for agent in agents if isinstance(agent, Predator)]
    prey = [agent for agent in agents if isinstance(agent, Prey)]

    for agent in agents[:]:
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

    # Draw counters for predators and prey
    prey_count = len([agent for agent in agents if isinstance(agent, Prey)])
    predator_count = len([agent for agent in agents if isinstance(agent, Predator)])
    draw_text(screen, f"Prey: {prey_count}", (10, 10), font)
    draw_text(screen, f"Predators: {predator_count}", (10, 40), font)

    # Draw reset button
    draw_button(screen, "Reset", reset_button_pos, reset_button_size, button_font, button_color, text_color)

    # SECTION 6: DISPLAY REFRESH
    pygame.display.flip()

# SECTION 7: QUIT PYGAME
pygame.quit()
