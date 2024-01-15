import pygame
import random
import math

# SECTION 1: CONFIGURABLE PARAMETERS
# -----------------------------------
GRID_COLS, GRID_ROWS = 20, 15  # Grid dimensions
MAX_SPEED = 0.5
TURN_ANGLE = math.pi / 8  # 22.5 degrees in radians
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PREY_ENERGY_GAIN = 1
PREDATOR_ENERGY_GAIN = 25
ENERGY_TO_REPRODUCE = 400
PREY_ENERGY_TO_REPRODUCE = 300  # Adjust this value as needed

# SECTION 2: UTILITY FUNCTIONS
# ----------------------------
def get_grid_cell(position):
    col_width, row_height = SCREEN_WIDTH / GRID_COLS, SCREEN_HEIGHT / GRID_ROWS
    col = int(position[0] / col_width)
    row = int(position[1] / row_height)
    return col, row

from collections import defaultdict

def get_nearby_cells(cell):
    x, y = cell
    return [(x + dx, y + dy) for dx in range(-1, 2) for dy in range(-1, 2)]

def update_agent_grid_cells(agent_list):
    grid = defaultdict(list)
    for agent in agent_list:
        cell = get_grid_cell(agent.position)
        grid[cell].append(agent)
    return grid

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
        
        # Calculate the new position
        dx = math.cos(self.direction) * self.velocity
        dy = math.sin(self.direction) * self.velocity
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy

        # Check for border collision
        if new_x <= 0 or new_x >= SCREEN_WIDTH:
            self.direction = math.pi - self.direction  # Reverse horizontal direction
        if new_y <= 0 or new_y >= SCREEN_HEIGHT:
            self.direction = -self.direction  # Reverse vertical direction

        # Update position with border constraints
        self.position = (max(0, min(SCREEN_WIDTH, new_x)), 
                         max(0, min(SCREEN_HEIGHT, new_y)))
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
    
    def handle_collision(self, same_type_agents, collision_distance=5):
        for other in same_type_agents:
            if other != self and self._distance_to(other) < collision_distance:
                # Simple collision response
                self.direction += math.pi  # Reverse direction
                self.move()  # Move away

    def handle_collision_efficiently(self, grid, collision_distance=5):
        cell = get_grid_cell(self.position)
        nearby_cells = get_nearby_cells(cell)

        for nearby_cell in nearby_cells:
            for other_agent in grid.get(nearby_cell, []):
                if other_agent != self and self._distance_to(other_agent) < collision_distance:
                    self.direction += math.pi
                    self.move()


# SECTION 4: PREY CLASS
# ---------------------
class Prey(Agent):
    def __init__(self):
        super().__init__()
        self.reproduction_cooldown = 100
        self.fleeing_energy_cost = 1  # Higher energy cost when fleeing
        self.safe_energy_gain = 0.5   # Energy gain when moving safely

    def is_within_fov(self, predator):
        """ Check if a predator is within the field of view. """
        return self._distance_to(predator) < 100

    def update(self, agent_list, predator_list, grid):
        # Retrieve nearby predators using spatial partitioning
        current_cell = get_grid_cell(self.position)
        nearby_cells = get_nearby_cells(current_cell)
        nearby_predators = [pred for cell in nearby_cells for pred in grid.get(cell, []) if isinstance(pred, Predator)]
        visible_predators = [pred for pred in nearby_predators if self.is_within_fov(pred)]

        if visible_predators:
            # Fleeing from predator
            closest_predator = min(visible_predators, key=lambda p: self._distance_to(p))
            self.direction = math.atan2(self.position[1] - closest_predator.position[1],
                                        self.position[0] - closest_predator.position[0]) + math.pi
            self.velocity = MAX_SPEED
            self.energy -= self.fleeing_energy_cost
        else:
            # Safe movement
            self.velocity = MAX_SPEED / 2
            self.energy += self.safe_energy_gain

        # Ensure energy does not drop below zero
        self.energy = max(self.energy, 0)

        self.move()

        # Handle reproduction
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        elif self.energy >= PREY_ENERGY_TO_REPRODUCE:
            self.reproduce(agent_list)

        # Collision handling
        self.handle_collision([a for a in agent_list if isinstance(a, Prey)])
        self.handle_collision_efficiently(grid)

    def is_in_deadlock(self, predator_list):
        """ Check for deadlock situation. """
        deadlock_radius = 50
        for pred in predator_list:
            if self._distance_to(pred) < deadlock_radius:
                return True
        return False

    def reproduce(self, agent_list):
        """ Handle reproduction process. """
        if self.energy >= PREY_ENERGY_TO_REPRODUCE:
            self.energy /= 2
            offspring = Prey()
            offset = random.randint(-20, 20)
            offspring.position = (self.position[0] + offset, self.position[1] + offset)
            offspring.grid_cell = get_grid_cell(offspring.position)
            agent_list.append(offspring)
            self.reproduction_cooldown = 100



# SECTION 5: PREDATOR CLASS
# -------------------------
class Predator(Agent):
    def __init__(self):
        super().__init__()
        self.energy = 100  # Starting energy for predator
        self.reproduction_cooldown = 0  # Initialize reproduction cooldown
        self.eating_cooldown = 0  # Cooldown after eating prey

    def update(self, agent_list, prey_list, grid):
        # Energy depletion for moving
        energy_before_move = self.energy
        self.energy -= 0.15  # Energy depletion rate for moving

        if self.eating_cooldown > 0:
            self.eating_cooldown -= 1
            temp_speed = self.velocity / 2  # Temporary reduced speed during cooldown
        else:
            temp_speed = self.velocity  # Normal speed

        # Optimized retrieval of nearby prey
        current_cell = get_grid_cell(self.position)
        nearby_cells = get_nearby_cells(current_cell)
        nearby_prey = []
        for cell in nearby_cells:
            if cell in grid:
                for prey in grid[cell]:
                    if isinstance(prey, Prey):
                        nearby_prey.append(prey)

        visible_prey = [prey for prey in nearby_prey if self.is_within_fov(prey)]
        if visible_prey:
            closest_prey = min(visible_prey, key=lambda p: self._distance_to(p))
            self.direction = math.atan2(closest_prey.position[1] - self.position[1],
                                        closest_prey.position[0] - self.position[0])

            if self._distance_to(closest_prey) < 20:
                energy_before_eating = self.energy
                self.energy += PREDATOR_ENERGY_GAIN

                # Check if the prey is still in the list before removing
                if closest_prey in prey_list:
                    prey_list.remove(closest_prey)
                    agent_list.remove(closest_prey)
                
                self.eating_cooldown = 30
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

        self.handle_collision([a for a in agent_list if isinstance(a, Predator)])  # Only check collision with other predators
        self.handle_collision_efficiently(grid)

    def angle_diff(self, angle1, angle2):
        # Calculate the difference between two angles
        diff = abs(angle1 - angle2) % (2 * math.pi)
        return min(diff, 2 * math.pi - diff)

    def is_within_fov(self, prey):
        # Check if a prey is within the field of view of the predator
        angle_to_prey = math.atan2(prey.position[1] - self.position[1], prey.position[0] - self.position[0])
        angle_difference = self.angle_diff(self.direction, angle_to_prey)
        return angle_difference < math.pi / 4 and self._distance_to(prey) < 200  # FOV settings

    def reproduce(self, agent_list):
        # Handle the reproduction process
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


