import pygame
from Fish import ENERGY_TO_REPRODUCE, Prey, Predator, update_agent_grid_cells
from gui_utils import draw_text, draw_button, is_button_clicked  # Make sure to create gui_utils.py as per previous instructions
from Fish import ENERGY_TO_REPRODUCE, Prey, Predator, update_agent_grid_cells, GridSquare


# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COLS = 20
GRID_ROWS = 15


# Constants for GridSquare
GRID_MAX_ENERGY = 25  # Maximum energy a grid square can hold
GRID_REGEN_RATE = 0.5    # Rate at which energy regenerates in each square

# Initialize the grid with GridSquares
energy_grid = [[GridSquare(GRID_MAX_ENERGY, GRID_REGEN_RATE) for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]



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
reset_button_pos = (SCREEN_WIDTH - 220, 110)
reset_button_size = (50, 20)
button_color = (0, 128, 0)  # Green button
text_color = (255, 255, 255)  # White text

# FPS Clock
clock = pygame.time.Clock()

# SPAWN button properties
spawn_pred_button_pos = (SCREEN_WIDTH - 220, 10)
spawn_pred_button_size = (50, 20)
spawn_prey_button_pos = (SCREEN_WIDTH - 220, 60)
spawn_prey_button_size = (50, 20)



# SECTION 3: AGENT INITIALIZATION
# -------------------------------
def reset_agents():
    return [Prey() for _ in range(70)] + [Predator() for _ in range(5)]

agents = reset_agents()

# FUZZY CIRCLES
def draw_fuzzy_circle(surface, color, position, radius):
    x, y = position
    temp_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for i in range(radius, 0, -1):
        alpha = int(255 * (1 - i / radius))
        pygame.draw.circle(temp_surface, color + (alpha,), (radius, radius), i)
    surface.blit(temp_surface, (x - radius, y - radius))

# Function to interpolate between two colors
def lerp_color(color1, color2, factor):
    return (
        int(color1[0] + (color2[0] - color1[0]) * factor),
        int(color1[1] + (color2[1] - color1[1]) * factor),
        int(color1[2] + (color2[2] - color1[2]) * factor)
    )

# for fuzzy colors to work
max_energy = ENERGY_TO_REPRODUCE 

def spawn_prey(number, agent_list):
    for _ in range(number):
        new_prey = Prey()
        agent_list.append(new_prey)

def spawn_predators(number, agent_list):
    for _ in range(number):
        new_predator = Predator()
        agent_list.append(new_predator)


# SECTION 4: MAIN GAME LOOP
# -------------------------
running = True
# Flags to track if the spawn buttons are currently pressed
spawn_pred_pressed = False
spawn_prey_pressed = False

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if is_button_clicked(event.pos, reset_button_pos, reset_button_size) and not spawn_pred_pressed and not spawn_prey_pressed:
                agents = reset_agents()  # Reset the simulation
            elif is_button_clicked(event.pos, spawn_pred_button_pos, spawn_pred_button_size) and not spawn_pred_pressed:
                spawn_predators(5, agents)
                spawn_pred_pressed = True
            elif is_button_clicked(event.pos, spawn_prey_button_pos, spawn_prey_button_size) and not spawn_prey_pressed:
                spawn_prey(50, agents)
                spawn_prey_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            spawn_pred_pressed = False
            spawn_prey_pressed = False

    # Update agent states
    predators = [agent for agent in agents if isinstance(agent, Predator)]
    prey = [agent for agent in agents if isinstance(agent, Prey)]

    # Update the grid for the current frame
    spatial_grid = update_agent_grid_cells(agents, GRID_COLS, GRID_ROWS, SCREEN_WIDTH, SCREEN_HEIGHT)

    for agent in agents:
        if isinstance(agent, Prey):
            agent.update(agents, predators, spatial_grid, energy_grid, GRID_COLS, GRID_ROWS)
        elif isinstance(agent, Predator):
            # If Predator update method doesn't use energy_grid, don't pass it
            agent.update(agents, prey, spatial_grid, GRID_COLS, GRID_ROWS)

    # SECTION 5: DRAWING
    screen.fill((255, 255, 255))  # Clear the screen with a white background

    # Calculate and display FPS
    fps = clock.get_fps()
    draw_text(screen, f"FPS: {int(fps)}", (10, 70), font, (0, 0, 0))  # Position and color can be adjusted

    # Draw grid lines
    for x in range(0, SCREEN_WIDTH, SCREEN_WIDTH // GRID_COLS):
        pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, SCREEN_HEIGHT // GRID_ROWS):
        pygame.draw.line(screen, (200, 200, 200), (0, y), (SCREEN_WIDTH, y))

     # Regenerate energy in each grid square
    for row in energy_grid:
        for cell in row:
            cell.regenerate_energy()
   
    # DRAW AGENTS - FUZZY CIRCLES AND EMOTIONS

    for agent in agents:
        if isinstance(agent, Prey):
            color = (0, 255, 0)  # Green for prey
            draw_fuzzy_circle(screen, color, agent.position, 5)
        elif isinstance(agent, Predator):
            # Interpolate color based on energy
            low_energy_color = (255, 0, 0)  # Red for low energy
            high_energy_color = (0, 0, 255)  # Blue for high energy
            energy_factor = max(0, min(1, agent.energy / max_energy))
            color = lerp_color(low_energy_color, high_energy_color, energy_factor)
            draw_fuzzy_circle(screen, color, agent.position, 5)

    # Draw counters for predators and prey
    prey_count = len([agent for agent in agents if isinstance(agent, Prey)])
    predator_count = len([agent for agent in agents if isinstance(agent, Predator)])
    draw_text(screen, f"Prey: {prey_count}", (10, 10), font, (0, 0, 0))  # Black color for text
    draw_text(screen, f"Predators: {predator_count}", (10, 40), font, (0, 0, 0))
    
    # Draw reset button
    draw_button(screen, "Reset", reset_button_pos, reset_button_size, button_font, button_color, text_color)

    # Draw spawn buttons and make sure they are redrawn every frame
    draw_button(screen, "Spawn Preds", spawn_pred_button_pos, spawn_pred_button_size, button_font, button_color, text_color)
    draw_button(screen, "Spawn Prey", spawn_prey_button_pos, spawn_prey_button_size, button_font, button_color, text_color)

    #Clock?
    pygame.display.flip()
    clock.tick(60)  # You can adjust this value based on desired FPS

    # SECTION 6: DISPLAY REFRESH
    pygame.display.flip()



# SECTION 7: QUIT PYGAME
pygame.quit()
