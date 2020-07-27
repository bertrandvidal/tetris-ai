import gym
from gym import spaces
from tetris_ai.game import *
import numpy as np


class TetrisEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    BOARD_HEIGHT = 20
    BOARD_WIDTH = 10

    drawer = None
    game = None
    applier = None
    counter = 0

    def __init__(self):
        # observation_space is the tetris "screen", height x width of 0/1
        # wheter the space is occupied by a piece or not
        self.observation_space = spaces.Box(
            low=0,
            high=1,
            shape=(TetrisEnv.BOARD_HEIGHT, TetrisEnv.BOARD_WIDTH),
            dtype=np.uintc,
        )
        self.action_space = spaces.Discrete(
            max(
                [
                    action.value
                    for action in Actions
                    if action not in [Actions.QUIT, Actions.SPACE]
                ]
            )
        )

    def step(self, action):
        self.counter += 1
        print(f"step {self.counter}: {self.game.score}")
        if self.game.figure is None:
            self.game.new_figure()
        self.game.go_down()
        self.applier.apply_actions([Actions(action)], self.game)
        return self._game_to_observation(), self.game.score, self.game.is_done(), {}

    def reset(self):
        self.drawer = TetrisDrawer()
        self.game = Tetris(TetrisEnv.BOARD_HEIGHT, TetrisEnv.BOARD_WIDTH)
        self.applier = ActionApplier()
        self.counter = 0
        return self._game_to_observation()

    def render(self, mode="human"):
        self.drawer.render(self.game)

    def close(self):
        self.drawer.close()

    def _game_to_observation(self):
        """returns a 2d array of booleans representing whether or not a piece
        is in position (x,y)
        """
        observation = []
        for i in range(TetrisEnv.BOARD_HEIGHT):
            new_line = []
            for j in range(TetrisEnv.BOARD_WIDTH):
                new_line.append(bool(self.game.field[i][j]))
            observation.append(new_line)
        return observation
