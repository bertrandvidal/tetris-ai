import gym
from sys import stderr
from gym import spaces
from tetris_ai.game import *
import numpy as np
from termcolor import colored


class TetrisEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    BOARD_HEIGHT = 20
    BOARD_WIDTH = 10

    drawer = None
    game = None
    applier = ActionApplier()
    counter = 0
    lower_tier_occupied_area = 0
    upper_tier_occupied_area = 0
    reward = 0

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
                    if action not in [Actions.QUIT, Actions.SPACE, Actions.DOWN]
                ]
            )
        )

    def step(self, action):
        self.counter += 1
        action_to_perform = Actions(action)
        reward = self._reward()
        self.reward += reward
        if self.counter % 10 == 0:
            print(
                colored(
                    f"step {self.counter}({self.reward:.5f}): {action_to_perform}", "green"
                ),
                file=stderr,
            )
        if self.game.figure is None:
            self.game.new_figure()
        self.game.go_down()
        self.applier.apply_actions([action_to_perform], self.game)
        return self._game_to_observation(), reward, self.game.is_done(), {}

    def reset(self):
        self.drawer = TetrisDrawer()
        self.game = Tetris(TetrisEnv.BOARD_HEIGHT, TetrisEnv.BOARD_WIDTH)
        self.counter = 0
        self.reward = 0
        self.lower_tier_occupied_area = 0
        self.upper_tier_occupied_area = 0
        return self._game_to_observation()

    def render(self, mode="human"):
        self.drawer.render(self.game, self._get_display_info())

    def close(self):
        self.drawer.close()

    def _get_display_info(self):
        return f"step {self.counter}({self.reward:.5f})"

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

    def _reward(self):
        total_reward = self.game.score
        third_height = TetrisEnv.BOARD_HEIGHT // 3 + 1
        third_surface_area = third_height * TetrisEnv.BOARD_WIDTH
        lower_tier_occupied_area = 0
        upper_tier_occupied_area = 0
        for i in range(TetrisEnv.BOARD_HEIGHT):
            for j in range(TetrisEnv.BOARD_WIDTH):
                if self.game.field[i][j] != 0:
                    # (0, 0) is top left so we need i to be greater than 2
                    # times a third of the height
                    if i >= 2 * third_height:
                        lower_tier_occupied_area += 1
                    if i < third_height:
                        upper_tier_occupied_area += 1
        positive_reward_occupied_aread = (
            lower_tier_occupied_area - self.lower_tier_occupied_area
        )
        negative_reward_occupied_aread = (
            upper_tier_occupied_area - self.upper_tier_occupied_area
        )
        self.lower_tier_occupied_area = lower_tier_occupied_area
        self.upper_tier_occupied_area = upper_tier_occupied_area
        if self.counter % 10 == 0:
            print(
                colored(
                    f"{total_reward} + ({positive_reward_occupied_aread} / {third_surface_area}) - ({negative_reward_occupied_aread} / {third_surface_area})",
                    "green",
                ),
                file=stderr,
            )
        return (
            total_reward
            + (positive_reward_occupied_aread / third_surface_area)
            - (negative_reward_occupied_aread / third_surface_area)
        )
