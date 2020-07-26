import gym
from tetris_ai.game import *

class TetrisEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    drawer = None
    game = None
    applier = None
    counter = 0

    def __init__(self):
        pass

    def step(self, action):
        self.counter += 1
        print(f"step {self.counter}: {self.game.score}")
        if self.game.figure is None:
            self.game.new_figure()
        self.game.go_down()
        self.applier.apply_actions(action, self.game)
        return self.game, self.game.score, self.game.is_done(), None

    def reset(self):
        self.drawer = TetrisDrawer()
        self.game = Tetris(20, 10)
        self.applier = ActionApplier()
        self.counter = 0
        return self.game

    def render(self, mode="human"):
        self.drawer.render(self.game)

    def close(self):
        self.drawer.close()
