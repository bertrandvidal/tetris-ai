import gym
from gym import spaces
from tetris_ai.game import *

class TetrisEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    BOARD_HEIGHT = 20
    BOARD_WIDTH = 10

    drawer = None
    game = None
    applier = None
    counter = 0

    def __init__(self):
        self.observation_space = spaces.Tuple((spaces.Discrete(TetrisEnv.BOARD_HEIGHT),
                                              spaces.Discrete(TetrisEnv.BOARD_WIDTH)))
        self.action_space = spaces.Discrete(max([action.value for action in
                                                 Actions if action not in
                                                 [Actions.QUIT, Actions.SPACE]]))

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
        self.game = Tetris(TetrisEnv.BOARD_HEIGHT, TetrisEnv.BOARD_WIDTH)
        self.applier = ActionApplier()
        self.counter = 0
        return self.game

    def render(self, mode="human"):
        self.drawer.render(self.game)

    def close(self):
        self.drawer.close()
