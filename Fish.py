import pygame
import random
import math

# SECTION 1: CONFIGURABLE PARAMETERS
# -----------------------------------
GRID_COLS, GRID_ROWS = 20, 15  # Grid dimensions
MAX_SPEED = 0.1
TURN_ANGLE = math.pi / 8  # 22.5 degrees in radians
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PREY_ENERGY_GAIN = 1
PREDATOR_ENERGY_GAIN = 4
ENERGY_TO_REPRODUCE = 800
PREY_ENERGY_TO_REPRODUCE = 400  # Adjust this value as needed

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
        if self.velocity < MAX_SPEED:
            self.velocity += 0.1  # Gradually increase speed
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
            offspring.position = (self.position[0] + random.randint(-50, 50), 
                                  self.position[1] + random.randint(-50, 50))
            offspring.grid_cell = get_grid_cell(offspring.position)
            agent_list.append(offspring)

    def _distance_to(self, other_agent):
        x1, y1 = self.position
        x2, y2 = other_agent.position
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# SECTION 4: PREY CLASS
# ---------------------
class Prey(Agent):
    def __init__(self):
        super().__init__()
        self.reproduction_cooldown = 100  # Initialize cooldown for reproduction

    def is_within_fov(self, predator):
        return self._distance_to(predator) < 100  # FOV radius

    def update(self, agent_list, predator_list):
        visible_predators = [pred for pred in predator_list if self.is_within_fov(pred)]
        if visible_predators:
            closest_predator = min(visible_predators, key=lambda p: self._distance_to(p))
            self.direction = math.atan2(self.position[1] - closest_predator.position[1],
                                        self.position[0] - closest_predator.position[0]) + math.pi
            self.velocity = MAX_SPEED
        else:
            self.velocity = 0
            self.energy += PREY_ENERGY_GAIN

        self.move()

        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        else:
            self.reproduce(agent_list)

    def reproduce(self, agent_list):
        if self.energy >= PREY_ENERGY_TO_REPRODUCE and self.reproduction_cooldown == 0:
            self.energy /= 2  # Energy is halved upon reproduction
            offspring = Prey()
            offset = random.randint(-20, 20)  # Disperse offspring
            offspring.position = (self.position[0] + offset, self.position[1] + offset)
            offspring.grid_cell = get_grid_cell(offspring.position)
            agent_list.append(offspring)
            self.reproduction_cooldown = 100  # Reset cooldown period after reproducing

# SECTION 5: PREDATOR CLASS
# -------------------------
class Predator(Agent):
    def __init__(self):
        super().__init__()
        self.energy = 100  # Starting energy for predator
        self.reproduction_cooldown = 0  # Initialize reproduction cooldown
    def is_within_fov(self, prey):
        angle_to_prey = math.atan2(prey.position[1] - self.position[1],
                                prey.position[0] - self.position[0])
        angle_difference = abs(self.direction - angle_to_prey)
        return angle_difference < math.pi / 4 and self._distance_to(prey) < 200  # FOV settings

    def update(self, agent_list, prey_list):
        self.energy -= 0.1  # Energy depletion rate

        visible_prey = [prey for prey in prey_list if self.is_within_fov(prey)]
        if visible_prey:
            closest_prey = min(visible_prey, key=lambda p: self._distance_to(p))
            self.direction = math.atan2(closest_prey.position[1] - self.position[1],
                                        closest_prey.position[0] - self.position[0])
            self.velocity = MAX_SPEED
            if self._distance_to(closest_prey) < 20:
                self.energy += PREDATOR_ENERGY_GAIN
                prey_list.remove(closest_prey)
        else:
            if random.random() < 0.05:  # 5% chance to change direction
                self.direction += random.choice([-1, 1]) * TURN_ANGLE

        self.move()

        if self.energy >= ENERGY_TO_REPRODUCE and self.reproduction_cooldown <= 0:
            self.reproduce(agent_list)

        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1

        if self.energy <= 0:
            agent_list.remove(self)

    def reproduce(self, agent_list):
        self.energy /= 2  # Split energy with offspring
        offspring = Predator()
        
        # Spawn the offspring close to the parent
        offset_x = random.randint(-10, 10)  # Small random offset
        offset_y = random.randint(-10, 10)
        offspring.position = (self.position[0] + offset_x, self.position[1] + offset_y)
        offspring.grid_cell = get_grid_cell(offspring.position)

        agent_list.append(offspring)

        # Reset reproduction cooldown
        self.reproduction_cooldown = 100  # Set cooldown duration

    
