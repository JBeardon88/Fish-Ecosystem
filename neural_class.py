import random
import math

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        # Initialize weights
        self.weights_input_to_hidden = [[random.uniform(-1, 1) for _ in range(hidden_size)] for _ in range(input_size)]
        self.weights_hidden_to_output = [[random.uniform(-1, 1) for _ in range(output_size)] for _ in range(hidden_size)]

    def forward(self, inputs):
        # Hidden layer
        hidden = [0] * self.hidden_size
        for i in range(self.hidden_size):
            for j in range(self.input_size):
                hidden[i] += inputs[j] * self.weights_input_to_hidden[j][i]
            hidden[i] = sigmoid(hidden[i])

        # Output layer
        output = [0] * self.output_size
        for i in range(self.output_size):
            for j in range(self.hidden_size):
                output[i] += hidden[j] * self.weights_hidden_to_output[j][i]
            output[i] = sigmoid(output[i])

        return output

    def mutate(self, rate):
        def mutate_value(value):
            if random.random() < rate:
                return value + random.uniform(-0.1, 0.1)
            return value

        self.weights_input_to_hidden = [[mutate_value(w) for w in layer] for layer in self.weights_input_to_hidden]
        self.weights_hidden_to_output = [[mutate_value(w) for w in layer] for layer in self.weights_hidden_to_output]
