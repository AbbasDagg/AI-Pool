import random

MOVE_NUMBER = 2
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

class Ai:
    def __init__(self):
        self.moves = []
        self.fitness = 0
        self.game = None

    def generate_moves(self):
        self.moves = []
        for _ in range(MOVE_NUMBER):
            # Generate random moves (x, y) within the screen bounds
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            self.moves.append((x, y))

    def set_game(self, game):
        self.game = game


# def main():
#     # Create an instance of the Ai class
#     ai_player = Ai()
#     ai_player.generate_moves()

#     # Print the generated moves
#     print("Generated Moves:")
#     for move in ai_player.moves:
#         print(move)