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
    total_contiguous = 0
    reward = 0
    log_sampling = 25
    ROTATE_WEIGHT = 2
    SIDE_WEIGHT = 4
    ACTIONS = (
        [Actions.ROTATE] * ROTATE_WEIGHT
        + [Actions.LEFT] * SIDE_WEIGHT
        + [Actions.RIGHT] * SIDE_WEIGHT
    )

    def __init__(self):
        # observation_space is the tetris "screen", height x width of 0/1
        # wheter the space is occupied by a piece or not
        self.observation_space = spaces.Box(
            low=0,
            high=1,
            shape=(TetrisEnv.BOARD_HEIGHT, TetrisEnv.BOARD_WIDTH),
            dtype=np.uintc,
        )
        # action_space is the possible movements "downgraded" to a one
        # dimensional space. Remove the ability to QUIT/DOWN/SPACE since we do
        # not want the agent to chose those. We also skew the choice so ROTATE
        # is less frequent than RIGHT/LEFT
        self.action_space = spaces.Discrete(len(TetrisEnv.ACTIONS))

    def step(self, action):
        self.counter += 1
        action_to_perform = Actions(TetrisEnv.ACTIONS[action])
        # we actually get the reward from the previous action given that the
        # one passed in isn't applied yet
        reward = self._reward()
        self.reward += reward
        if self.counter % self.log_sampling == 0:
            print(
                colored(
                    f"step {self.counter}({self.reward:.5f}): {action_to_perform}",
                    "green",
                ),
                file=stderr,
            )
        # game.figure is the piece that we control/that is going down
        if self.game.figure is None:
            self.game.new_figure()
        # for each step we move one step downward
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
        self.total_contiguous = 0
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
        rows_cleared = 2 if self.game.score else 0
        positive, negative = self._get_occupied_area_rewards()
        low_rows = self._get_low_rows_rewards()
        if self.counter % self.log_sampling == 0:
            print(
                colored(
                    f"{rows_cleared} + {positive:.5f} - {negative:.5f} + {low_rows:.5f}",
                    "green",
                ),
                file=stderr,
            )
        return rows_cleared + positive + negative

    def _get_low_rows_rewards(self):
        """For low rows, find the longest continuous segment of tetris, express
        as a ratio of the row length and sum.
        """
        nb_low_rows = 5
        low_rows = self.game.field[TetrisEnv.BOARD_HEIGHT - nb_low_rows :]
        total_contiguous = 0
        for row in low_rows:
            segment_size = 0
            max_segment = 0
            previous = None
            for column in row:
                if column != 0:
                    segment_size += 1
                    max_segment = max(max_segment, segment_size)
                else:
                    segment_size = 0
            total_contiguous += max_segment / TetrisEnv.BOARD_WIDTH
        delta_contiguous = total_contiguous - self.total_contiguous
        self.total_contiguous = total_contiguous
        return delta_contiguous / nb_low_rows

    def _get_occupied_area_rewards(self):
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
        return (
            (positive_reward_occupied_aread / third_surface_area),
            (negative_reward_occupied_aread / third_surface_area),
        )
