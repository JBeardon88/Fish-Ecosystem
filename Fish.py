# Fish.py
import pygame
import random
import math

# SECTION 1: CONFIGURABLE PARAMETERS
# -----------------------------------
GRID_COLS, GRID_ROWS = 20, 15  # Grid dimensions
MAX_SPEED = 1
TURN_ANGLE = math.pi / 8  # 22.5 degrees in radians
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PREY_ENERGY_GAIN = 1
PREDATOR_ENERGY_GAIN = 10
ENERGY_TO_REPRODUCE = 500
PREY_ENERGY_TO_REPRODUCE = 500  # Adjust this value as needed

# SECTION 2: UTILITY FUNCTIONS
# ----------------------------
def get_grid_cell(position):
    col_width, row_height = SCREEN_WIDTH / GRID_COLS, SCREEN_HEIGHT / GRID_ROWS
    col = int(position[0] / col_width)
    row = int(position[1] / row_height)
    return col, row

def random_position():
    return random.randrange(0, SCREEN_WIDTH), random.randrange(0, SCREEN_HEIGHT)

# SECTION 3: BASE AGENT CLASS
# ---------------------------
class Agent:
    def __init__(self):
        self.position = random_position()
        self.energy = 50
        self.velocity = random.uniform(0, MAX_SPEED)
        self.direction = random.uniform(0, 2 * math.pi)
        self.grid_cell = get_grid_cell(self.position)

    def move(self):
        dx = math.cos(self.direction) * self.velocity
        dy = math.sin(self.direction) * self.velocity
        self.position = (self.position[0] + dx) % SCREEN_WIDTH, (self.position[1] + dy) % SCREEN_HEIGHT
        self.grid_cell = get_grid_cell(self.position)

    def update(self):
        # To be overridden in subclasses
        pass

    def reproduce(self, agent_list):
        if self.energy >= ENERGY_TO_REPRODUCE:
            self.energy /= 2
            offspring = type(self)()
            offspring.position = (self.position[0] + random.randint(-20, 20), 
                                  self.position[1] + random.randint(-20, 20))
            offspring.grid_cell = get_grid_cell(offspring.position)
            agent_list.append(offspring)
    
    def _distance_to(self, other_agent):
        x1, y1 = self.position
        x2, y2 = other_agent.position
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def move(self):
        if self.velocity < MAX_SPEED:
            self.velocity += 0.1  # Gradually increase speed
        dx = math.cos(self.direction) * self.velocity
        dy = math.sin(self.direction) * self.velocity
        self.position = (self.position[0] + dx) % SCREEN_WIDTH, (self.position[1] + dy) % SCREEN_HEIGHT
        self.grid_cell = get_grid_cell(self.position)



# SECTION 4: PREY CLASS
# ---------------------
class Prey(Agent):
    def __init__(self):
        super().__init__()
        self.reproduction_cooldown = 0  # Initialize cooldown for reproduction

    def update(self, agent_list, predator_list):
        # Check for nearby predators
        is_predator_close = any(self._distance_to(predator) < 50 for predator in predator_list)
        
        if is_predator_close:
            # Move away from the predator
            self.direction = random.uniform(0, 2 * math.pi)
            self.velocity = MAX_SPEED
        else:
            # Stay still to gain energy, if no predator is close
            self.velocity = 0
            self.energy += PREY_ENERGY_GAIN
        
        # Move the prey
        self.move()

        # Handle reproduction
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        else:
            self.reproduce(agent_list)

    def reproduce(self, agent_list):
        if self.energy >= PREY_ENERGY_TO_REPRODUCE and self.reproduction_cooldown == 0:
            self.energy /= 2  # Energy is halved upon reproduction
            offspring = type(self)()
            offset = random.randint(-100, 100)  # Disperse offspring
            offspring.position = (self.position[0] + offset, self.position[1] + offset)
            offspring.grid_cell = get_grid_cell(offspring.position)
            agent_list.append(offspring)
            self.reproduction_cooldown = 100  # Cooldown period after reproducing


# SECTION 5: PREDATOR CLASS
# -------------------------
class Predator(Agent):
    def update(self, agent_list, prey_list):
        # Decrease energy each update cycle
        self.energy -= 0.1  # Consider adjusting this rate

        # Find the closest prey
        closest_prey = min(prey_list, key=lambda prey: self._distance_to(prey), default=None)

        # If there is prey close enough, eat it and gain energy
        if closest_prey and self._distance_to(closest_prey) < 20:  # Increased distance
            self.energy += PREDATOR_ENERGY_GAIN
            prey_list.remove(closest_prey)
        elif closest_prey:
            # Move towards the closest prey
            self.direction = math.atan2(closest_prey.position[1] - self.position[1],
                                        closest_prey.position[0] - self.position[0])
            self.velocity = MAX_SPEED
        else:
            # No prey in sight, reduce velocity
            self.velocity *= 0.5  # Gradually reduce speed when not chasing prey

        # Move and check for reproduction
        self.move()
        self.reproduce(agent_list)

        # Check for predator's death due to energy depletion
        if self.energy <= 0:
            agent_list.remove(self)
            return  # Exit the method to avoid further actions on a removed predator
