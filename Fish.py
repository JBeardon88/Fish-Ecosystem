import pygame
import random
import math
from neural_class import NeuralNetwork
import copy
from functools import lru_cache



# SECTION 0.5 - GRIDSQUARES! MAKING PREY EAT FOOD
class GridSquare:
    def __init__(self, max_energy, regen_rate):
        self.max_energy = max_energy
        self.current_energy = max_energy
        self.regen_rate = regen_rate

    def consume_energy(self, amount):
        consumed = min(self.current_energy, amount)
        self.current_energy -= consumed
        return consumed

    def regenerate_energy(self):
        if self.current_energy < self.max_energy:
            self.current_energy = min(self.max_energy, self.current_energy + self.regen_rate)



# SECTION 1: CONFIGURABLE PARAMETERS
# -----------------------------------
GRID_COLS, GRID_ROWS = 20, 15  # Grid dimensions
MAX_SPEED = 1
TURN_ANGLE = math.pi / 8  # 22.5 degrees in radians
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PREY_ENERGY_GAIN = 200
PREDATOR_ENERGY_GAIN = 100
ENERGY_TO_REPRODUCE = 1000
PREY_ENERGY_TO_REPRODUCE = 1000  # Adjust this value as needed
MAX_ENERGY = 1200



## Defining sight range for prey at half a grid square
# Calculate the dimensions of a grid square
grid_square_width = SCREEN_WIDTH / GRID_COLS
grid_square_height = SCREEN_HEIGHT / GRID_ROWS

# Calculate the diagonal of a grid square (using Pythagoras' theorem)
grid_square_diagonal = math.sqrt(grid_square_width**2 + grid_square_height**2)

# Set MAX_DISTANCE to half the diagonal length of a grid square
MAX_DISTANCE = grid_square_diagonal




# SECTION 2: UTILITY FUNCTIONS
# ----------------------------
def get_grid_cell(position):
    col_width, row_height = SCREEN_WIDTH / GRID_COLS, SCREEN_HEIGHT / GRID_ROWS
    col = int(position[0] / col_width)
    row = int(position[1] / row_height)
    # Ensure that col and row are within the grid's range
    col = max(0, min(col, GRID_COLS - 1))
    row = max(0, min(row, GRID_ROWS - 1))
    return col, row


from collections import defaultdict

# EFFICIENT GRID USE APPARENTLY

def update_agent_grid_cells(agent_list, grid_cols, grid_rows, screen_width, screen_height):
    grid = defaultdict(list)
    col_width, row_height = screen_width / grid_cols, screen_height / grid_rows

    for agent in agent_list:
        col = int(agent.position[0] / col_width)
        row = int(agent.position[1] / row_height)
        new_cell = (col, row)

        # Update grid cell only if it has changed
        if new_cell != agent.grid_cell:
            agent.grid_cell = new_cell
        grid[new_cell].append(agent)

    return grid

def get_nearby_cells(cell, grid_cols, grid_rows):
    x, y = cell
    neighbors = [(x + dx, y + dy) for dx in range(-1, 2) for dy in range(-1, 2)]
    # Filter out cells that are outside the grid
    return [(nx, ny) for nx, ny in neighbors if 0 <= nx < grid_cols and 0 <= ny < grid_rows]

def handle_collision_efficiently(agent, grid, grid_cols, grid_rows, collision_distance=5):
    nearby_cells = get_nearby_cells(agent.grid_cell, grid_cols, grid_rows)

    for nearby_cell in nearby_cells:
        for other_agent in grid.get(nearby_cell, []):
            if other_agent != agent and agent._distance_to(other_agent) < collision_distance:
                agent.direction += math.pi
                agent.move()


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


    # GET YOUR BODY MOVING ON THE FLOOR TONIGHT (aw yeah)

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

    def angle_diff(self, angle1, angle2):
        # Calculate the difference between two angles
        diff = abs(angle1 - angle2) % (2 * math.pi)
        return min(diff, 2 * math.pi - diff)
     
    @staticmethod
    @lru_cache(maxsize=1000)  # Adjust maxsize as needed
    def calculate_distance(x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def _distance_to(self, other_agent):
        return Agent.calculate_distance(self.position[0], self.position[1], 
                                        other_agent.position[0], other_agent.position[1])
    
    def handle_collision(self, same_type_agents, collision_distance=5):
        for other in same_type_agents:
            if other != self and self._distance_to(other) < collision_distance:
                # Simple collision response
                self.direction += math.pi  # Reverse direction
                self.move()  # Move away

    def handle_collision_efficiently(self, grid, grid_cols, grid_rows, collision_distance=5):
        # The method implementation...
        cell = get_grid_cell(self.position)
        nearby_cells = get_nearby_cells(cell, grid_cols, grid_rows)

        for nearby_cell in nearby_cells:
            for other_agent in grid.get(nearby_cell, []):
                if other_agent != self and self._distance_to(other_agent) < collision_distance:
                    self.direction += math.pi
                    self.move()


# SECTION 4: PREY CLASS
# ---------------------
class Prey(Agent):
    def __init__(self, color=(0, 255, 0), fov_angle=120, fov_distance=400):
        super().__init__()
        self.nn = NeuralNetwork(input_size=3, hidden_size=5, output_size=2)
        self.reproduction_cooldown = 100
        self.fleeing_energy_cost = 0.5
        self.safe_energy_gain = 0.5
        self.color = color
        self.fov_angle = fov_angle
        self.fov_distance = fov_distance
        self.speed_boost_multiplier = 1.2
        self.boost_energy_cost = 100
        self.boost_cooldown = 0  # Cooldown timer for boosting
        self.is_boosting = False  # Indicates if currently boosting
        self.after_boost_slowdown = 0.5  # Slowdown multiplier after boosting
        self.boost_cooldown_timer = 180  # Cooldown period after boosting
        self.boost_energy_threshold = 0.75 * MAX_ENERGY  # Adjust MAX_ENERGY as needed

    def detect_predators(self, predator_list):
        for predator in predator_list:
            if self._distance_to(predator) <= self.fov_distance:
                return True
        return False

    def get_nearest_predator_info(self, predator_list):
        """
        Find the nearest predator and calculate the relative distance and angle.
        Returns a tuple (distance, angle) where distance is normalized between 0 and 1,
        and angle is normalized between -1 and 1 (-1 being direct left, 1 being direct right).
        """
        if not predator_list:
            return (1, 0)  # No predators in sight

        # Find the closest predator
        closest_predator = min(predator_list, key=lambda p: self._distance_to(p))
        distance = self._distance_to(closest_predator) / MAX_DISTANCE  # Normalize distance
        angle_to_predator = math.atan2(closest_predator.position[1] - self.position[1],
                                       closest_predator.position[0] - self.position[0])
        angle_diff = self.angle_diff(self.direction, angle_to_predator)
        angle = angle_diff / math.pi  # Normalize angle


        return (distance, angle)



    # In the Prey class
    def update(self, agent_list, predator_list, spatial_grid, energy_grid, grid_cols, grid_rows):
        # Determine if predators are nearby and update self.predator_nearby accordingly
        self.predator_nearby = self.detect_predators(predator_list)
        self.move(energy_grid)  # Corrected to match the move method's definition


        current_cell = self.grid_cell  # or however you get the current cell
        nearby_cells = get_nearby_cells(self.grid_cell, grid_cols, grid_rows)
        nearby_predators = [pred for cell in nearby_cells for pred in spatial_grid.get(cell, []) if isinstance(pred, Predator)]

        # ... rest of the update method ...

        # This will assign the first two values returned from get_nearest_predator_info to distance and angle
        # and the third value, self.energy, to energy.
        distance, angle = self.get_nearest_predator_info(predator_list)
        energy = self.energy

        # Existing logic to calculate nearest predator info...
        distance, angle = self.get_nearest_predator_info(predator_list)
        predator_nearby = distance < 1.0  # Assuming normalized distance, adjust this condition as needed
    

        # Normalize inputs
        normalized_inputs = [distance / MAX_DISTANCE, angle / math.pi, energy / MAX_ENERGY]

        # Neural network makes decision
        decision = self.nn.forward(normalized_inputs)

        # Interpret decision (e.g., first output for direction, second for speed)
        self.direction += decision[0] * TURN_ANGLE - TURN_ANGLE / 2  # Adjust direction
        self.velocity = decision[1] * MAX_SPEED       

        # Adjust the call to move
        self.move(energy_grid)

                # Decrease cooldown timer if active
        if self.boost_cooldown > 0:
            self.boost_cooldown -= 1

        #super().update(agent_list, predator_list, spatial_grid, energy_grid, grid_cols, grid_rows)
        # More logic can follow here

        # Handle reproduction
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        elif self.energy >= PREY_ENERGY_TO_REPRODUCE:
            #print(f"Prey ready for reproduction. Energy: {self.energy}")
            self.reproduce(agent_list)

    def handle_collision(self, same_type_agents, energy_grid):
        for other_agent in same_type_agents:
            if self != other_agent and self._distance_to(other_agent) < collision_distance:
                self.direction += math.pi  # Reverse direction
                self.move(energy_grid)  # Use class attribute directly



    def is_in_deadlock(self, predator_list):
        """ Check for deadlock situation. """
        deadlock_radius = 50
        for pred in predator_list:
            if self._distance_to(pred) < deadlock_radius:
                return True
        return False

    def reproduce(self, agent_list):
        if self.energy >= PREY_ENERGY_TO_REPRODUCE:
            self.energy /= 2
            offspring = Prey(color=self.color, fov_angle=self.fov_angle, fov_distance=self.fov_distance)

            MUTATION_CHANCE = 0.5
            if random.random() < MUTATION_CHANCE:
                offspring.nn = copy.deepcopy(self.nn)
                offspring.nn.mutate(rate=0.1)
                offspring.color = self.mutate_color()
                offspring.fov_angle = self.mutate_fov_angle()
                offspring.fov_distance = self.mutate_fov_distance()
                #print(f"[Mutate Color] Color after mutation: {self.color}")

            offset = random.randint(-20, 20)
            offspring.position = (self.position[0] + offset, self.position[1] + offset)
            offspring.grid_cell = get_grid_cell(offspring.position)
            agent_list.append(offspring)
            self.reproduction_cooldown = 100

    def mutate_fov_angle(self):
        # Adjust the mutation range as needed
        return max(60, min(180, self.fov_angle + random.randint(-15, 15)))

    def mutate_fov_distance(self):
        # Adjust the mutation range as needed
        return max(50, self.fov_distance + random.randint(-10, 10))

    def mutate_color(self):
        shift = lambda x: max(0, min(255, x + random.randint(-50, 50)))
        return tuple(shift(c) for c in self.color)
    

    @staticmethod
    def random_color():
        # Generates a random color within a reasonable range
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))



# GRID EATING SHENANINGANS WHERE THE PREY MUNCH OUT ENERGY FROM THE GRID

    def move(self, energy_grid):
        original_velocity = self.velocity
        
        # Apply speed boost if not on cooldown and conditions are met
        if self.energy > self.boost_energy_threshold and self.predator_nearby and self.boost_cooldown == 0:
            self.velocity *= self.speed_boost_multiplier
            self.energy -= self.boost_energy_cost
            self.boost_cooldown = self.boost_cooldown_timer  # Start cooldown
            self.is_boosting = True
            # print(f"Boosting! Energy: {self.energy}, Velocity: {self.velocity}")
        elif self.boost_cooldown > 0 and not self.is_boosting:
            # Apply slowdown if in cooldown but not currently boosting
            self.velocity *= self.after_boost_slowdown

        super().move()
        
        # Reset velocity to original if it was boosted or slowed, ensuring it's always defined
        self.velocity = original_velocity
        
        # Handle energy grid consumption and cooldown logic
        col, row = get_grid_cell(self.position)
        if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
            self.energy += energy_grid[col][row].consume_energy(PREY_ENERGY_GAIN)
        self.energy = min(self.energy, MAX_ENERGY)
        
        # If was boosting on this move, reset is_boosting for next move
        if self.is_boosting:
            self.is_boosting = False

    # Move the grid arguments correctly? The robot made me do it. 
    def handle_collision(self, same_type_agents, energy_grid, collision_distance=5):
        for other in same_type_agents:
            if other != self and self._distance_to(other) < collision_distance:
                self.direction += math.pi  # Reverse direction
                self.move(energy_grid)  # Pass energy_grid here

    def handle_collision_efficiently(self, spatial_grid, grid_cols, grid_rows, energy_grid, collision_distance=5):
        cell = get_grid_cell(self.position)
        nearby_cells = get_nearby_cells(cell, grid_cols, grid_rows)

        for nearby_cell in nearby_cells:
            for other_agent in spatial_grid.get(nearby_cell, []):
                if other_agent != self and self._distance_to(other_agent) < collision_distance:
                    # Simple collision response: reverse direction and move
                    self.direction += math.pi
                    self.move(energy_grid)  # Move and consume energy from the grid

# SECTION 5: PREDATOR CLASS
# -------------------------
class Predator(Agent):
    def __init__(self, color=(255, 0, 0), fov_angle=45, fov_distance=1000):
        super().__init__()
        self.nn = NeuralNetwork(input_size=3, hidden_size=5, output_size=2)
        self.energy = 100
        self.reproduction_cooldown = 0
        self.eating_cooldown = 0
        self.color = color
        self.fov_angle = fov_angle
        self.fov_distance = fov_distance
        self.max_velocity = 2  # Adjusted maximum speed to 2 times the minimum speed
        self.energy_consumption_rate = .7  # Base energy consumption rate for minimum speed

    def move(self):
        dx = math.cos(self.direction) * self.velocity
        dy = math.sin(self.direction) * self.velocity
        self.position = (max(0, min(SCREEN_WIDTH, self.position[0] + dx)),
                         max(0, min(SCREEN_HEIGHT, self.position[1] + dy)))

        # Ensure minimum velocity of 1
        self.velocity = max(1, min(self.velocity, self.max_velocity))

        # Dynamic energy consumption based on velocity
        if self.velocity == self.max_velocity:  # If moving at maximum speed
            self.energy -= 2 * self.energy_consumption_rate  # Consuming double energy
        else:
            self.energy -= self.energy_consumption_rate  # Consuming base energy for speeds >= 1 and <= max_velocity

        self.grid_cell = get_grid_cell(self.position)  # Update grid cell position
        self.energy = max(self.energy, 0)  # Ensure energy doesn't go negative

    # Other methods remain unchanged
    def get_nearest_prey_info(self, prey_list):
        detectable_prey = [prey for prey in prey_list if self.is_within_fov(prey)]
        if not detectable_prey:
            return (1, 0)  # No detectable prey in sight

        closest_prey = min(detectable_prey, key=lambda p: self._distance_to(p))
        distance = self._distance_to(closest_prey) / MAX_DISTANCE
        angle_to_prey = math.atan2(closest_prey.position[1] - self.position[1],
                                   closest_prey.position[0] - self.position[0])
        angle_diff = self.angle_diff(self.direction, angle_to_prey)
        angle = angle_diff / math.pi

        return (distance, angle)

    def is_within_fov(self, prey):
        distance = self._distance_to(prey)
        if distance > self.fov_distance:
            return False

        angle_to_prey = math.atan2(prey.position[1] - self.position[1],
                                   prey.position[0] - self.position[0])
        relative_angle = abs(self.angle_diff(self.direction, angle_to_prey))
        if relative_angle > math.radians(self.fov_angle / 2):
            return False

        return True

    def update(self, agent_list, prey_list, grid, grid_cols, grid_rows):
        # Optimized retrieval of nearby prey
        current_cell = self.grid_cell  # or however you get the current cell
        nearby_cells = get_nearby_cells(current_cell, GRID_COLS, GRID_ROWS)
        nearby_prey = [prey for cell in nearby_cells for prey in grid.get(cell, []) if isinstance(prey, Prey)]

        # Get the nearest prey information
        distance, angle = self.get_nearest_prey_info(nearby_prey)
        energy = self.energy

        # Normalize inputs
        normalized_inputs = [distance / MAX_DISTANCE, angle / math.pi, energy / MAX_ENERGY]

        # Neural network makes decision
        decision = self.nn.forward(normalized_inputs)

        # Interpret decision (e.g., first output for direction, second for speed)
        self.direction += decision[0] * TURN_ANGLE - TURN_ANGLE / 2  # Adjust direction
        self.velocity = decision[1] * MAX_SPEED

        
        # print(f"NN Decision - Direction: {decision[0]}, Velocity: {self.velocity}")


        if nearby_prey:
            closest_prey = min(nearby_prey, key=lambda p: self._distance_to(p))
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

        # Movement and energy depletion
        #self.energy -= .5  # Energy depletion rate for moving
        self.energy = max(self.energy, 0)  # Prevent negative energy
        self.move()

        # Reproduction
        if self.energy >= ENERGY_TO_REPRODUCE and self.reproduction_cooldown <= 0:
            self.reproduce(agent_list)

        # Cooldown
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1

        # Death condition
        if self.energy <= 0:
            agent_list.remove(self)

        # Collision handling
        self.handle_collision([a for a in agent_list if isinstance(a, Predator)])
        self.handle_collision_efficiently(grid, grid_cols, grid_rows)

    def is_close_to_reproducing(self, energy_to_reproduce):
        glow_threshold = energy_to_reproduce * 0.5
        return self.energy >= glow_threshold

    def mutate_color(self):
        shift = lambda x: max(0, min(255, x + random.randint(-100, 100)))  # Shift within [-10, 10] range
        self.color = tuple(shift(c) for c in self.color)  # Apply the shift to each RGB component
     #   print(f"[Mutate Color] Color after mutation: {self.color}")

    # ... rest of the existing methods ...

    def reproduce(self, agent_list):
        if self.energy >= ENERGY_TO_REPRODUCE:
            self.energy /= 2
            offspring = Predator(color=self.color, fov_angle=self.fov_angle, fov_distance=self.fov_distance)
            offspring.nn = copy.deepcopy(self.nn)

            # Neural network mutation flag
            nn_mutated = random.random() < 0.5
            if nn_mutated:
                #print(f"Before Mutation: Color: {offspring.color}, FOV Angle: {offspring.fov_angle}, FOV Distance: {offspring.fov_distance}")
                offspring.nn.mutate(rate=0.2)
                offspring.color = self.mutate_color()
                # Directly call mutate_fov() on the offspring to adjust both FOV angle and distance
                offspring.mutate_fov()
                #print(f"After Mutation: Color: {offspring.color}, FOV Angle: {offspring.fov_angle}, FOV Distance: {offspring.fov_distance}")

            # Positioning the offspring
            offset = random.randint(-10, 10)
            offspring.position = (self.position[0] + offset, self.position[1] + offset)
            offspring.grid_cell = get_grid_cell(offspring.position)
            agent_list.append(offspring)
            self.reproduction_cooldown = 100

    def mutate_fov(self):
        # Determine the change magnitude (positive or negative)
        change = random.randint(-30, 30)  # Adjust the range as needed for your simulation
        self.fov_distance += change
        self.fov_angle -= change

    def mutate_color(self):
        new_color = tuple(max(0, min(255, c + random.randint(-50, 50))) for c in self.color)
        #print(f"Old Color: {self.color}, New Color: {new_color}")  # Debug print
        return new_color
