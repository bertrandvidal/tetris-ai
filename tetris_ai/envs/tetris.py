import gym
from tetris_ai.game import *

class TetrisEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    drawer = None
    game = None

    def __init__(self):
        pass

    def step(self, action):
        return self.game, self.game.score, self.game.is_done(), None

    def reset(self):
        self.drawer = TetrisDrawer()
        self.game = Tetris(20, 10)
        return game

    def render(self, mode="human"):
        self.drawer.render(self.game)

    def close(self):
        pass
