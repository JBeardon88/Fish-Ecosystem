# SECTION 4: PREY CLASS
# ---------------------
class Prey(Agent):
    def __init__(self):
        super().__init__()
        self.nn = NeuralNetwork(input_size=3, hidden_size=5, output_size=2)  # Example sizes
        self.reproduction_cooldown = 100
        self.fleeing_energy_cost = 0.5  # Higher energy cost when fleeing
        self.safe_energy_gain = 0.5   # Energy gain when moving safely

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

    def update(self, agent_list, predator_list, grid):
        # Retrieve nearby predators using spatial partitioning
        current_cell = get_grid_cell(self.position)
        nearby_cells = get_nearby_cells(current_cell)
        nearby_predators = [pred for cell in nearby_cells for pred in grid.get(cell, []) if isinstance(pred, Predator)]
        visible_predators = [pred for pred in nearby_predators if self.is_within_fov(pred)]

        # Prepare inputs for neural network (example: distance, angle, energy)
        # For simplicity, let's assume these methods exist and return appropriate values
        distance, angle, energy = self.get_nearest_predator_info(predator_list), self.energy

        # Normalize inputs
        normalized_inputs = [distance / MAX_DISTANCE, angle / math.pi, energy / MAX_ENERGY]

        # Neural network makes decision
        decision = self.nn.forward(normalized_inputs)

        # Interpret decision (e.g., first output for direction, second for speed)
        self.direction += decision[0] * TURN_ANGLE - TURN_ANGLE / 2  # Adjust direction
        self.velocity = decision[1] * MAX_SPEED       

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
            offspring.nn = copy.deepcopy(self.nn)  # Deep copy parent's neural network
            offspring.nn.mutate(rate=0.01)  # Small mutation rate
            offset = random.randint(-20, 20)
            offspring.position = (self.position[0] + offset, self.position[1] + offset)
            offspring.grid_cell = get_grid_cell(offspring.position)
            agent_list.append(offspring)
            self.reproduction_cooldown = 100
