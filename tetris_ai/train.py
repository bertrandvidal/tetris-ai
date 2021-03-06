import gym
import os
from termcolor import colored
from datetime import datetime
from tetris_ai.game import *
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Flatten
from tensorflow.keras.optimizers import Adam
from termcolor import colored
from collections import Counter
from sys import stderr

from rl.agents.dqn import DQNAgent
from rl.callbacks import Callback
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory


def get_agent(env):
    nb_actions = env.action_space.n
    model = Sequential()
    input_size = env.BOARD_HEIGHT * env.BOARD_WIDTH
    model.add(Flatten(input_shape=(1,) + env.observation_space.shape))

    model.add(Dense(input_size, activation="relu"))
    model.add(Dense(input_size, activation="relu"))
    model.add(Dense(input_size, activation="relu"))

    model.add(Dense(nb_actions, activation="linear"))
    print(model.summary())

    # still not understanding that part
    memory = SequentialMemory(limit=500, window_length=1)
    policy = BoltzmannQPolicy()
    dqn = DQNAgent(
        model=model,
        nb_actions=nb_actions,
        memory=memory,
        nb_steps_warmup=100,
        target_model_update=1e-2,
        policy=policy,
    )
    dqn.compile(Adam(lr=0.1), metrics=["mae"])
    return dqn, model


class ResetEnvCallback(Callback):
    def __init__(self, env):
        self._set_env(env)

    def on_episode_end(self, episode, logs={}):
        self.env.reset()


class LogStepCallback(Callback):
    def __init__(self, nb_steps, log_every=50):
        self.current_step = 0
        self.nb_steps = nb_steps
        self.log_every = log_every

    def on_step_end(self, step, logs={}):
        self.current_step += 1
        if self.current_step % self.log_every == 0:
            print(
                colored(f"{self.current_step} / {self.nb_steps}", "blue"), file=stderr
            )


class EpisodeRewardsCallback(Callback):
    max_reward = -1

    def __init__(self):
        self.max_reward = -1

    def on_episode_end(self, episode, logs={}):
        self.max_reward = max(self.max_reward, logs["episode_reward"])
        print(colored(f"max reward: {self.max_reward:.5f}", "red"), file=stderr)


class ActionRecorderCallback(Callback):
    episode_actions = []
    action_mapping = None
    TOTAL_ACTIONS = Counter()

    def __init__(self, env):
        self.action_mapping = env.ACTIONS
        self.episode_actions = []

    def on_action_begin(self, action, logs={}):
        self.episode_actions.append(action)

    def on_episode_begin(self, episode, logs={}):
        self.episode_actions = []

    def on_episode_end(self, episode, logs={}):
        ActionRecorderCallback.TOTAL_ACTIONS.update(
            [Actions(self.action_mapping[a]) for a in self.episode_actions]
        )
        print(
            colored(f"actions:{ActionRecorderCallback.TOTAL_ACTIONS}", "red"),
            file=stderr,
        )


if __name__ == "__main__":
    version = "0009"
    nb_steps = 100000
    env = gym.make("tetris_ai:tetris_gym-v0")
    base_folder = "nn_weights"
    filename = "dqn_{}_{}.h5f".format(env.spec.id, version)
    complete_path = os.path.abspath(os.path.join(base_folder, filename))
    np.random.seed(123)
    env.seed(123)
    agent, model = get_agent(env)

    if any(path.startswith(filename) for path in os.listdir(base_folder)):
        # load existing weights
        agent.load_weights(complete_path)

    agent.fit(
        env,
        nb_steps=nb_steps,
        visualize=False,
        verbose=0,
        callbacks=[
            ResetEnvCallback(env),
            LogStepCallback(nb_steps),
            EpisodeRewardsCallback(),
            ActionRecorderCallback(env),
        ],
    )

    print(colored("Running Tests", "red"), file=stderr)
    # After training is done, we save the final weights to the same file
    agent.save_weights(complete_path, overwrite=True)

    # Finally, evaluate our algorithm for 5 episodes.
    agent.test(
        env,
        nb_episodes=10,
        visualize=True,
        verbose=0,
        callbacks=[EpisodeRewardsCallback(), ActionRecorderCallback(env)],
    )
