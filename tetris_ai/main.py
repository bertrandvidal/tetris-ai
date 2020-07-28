import gym
from datetime import datetime
from tetris_ai.game import *
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Flatten
from tensorflow.keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

env = gym.make("tetris_ai:tetris_gym-v0")
observation = env.reset()
action_decider = RandomActionDecider()

np.random.seed(123)
env.seed(123)
nb_actions = env.action_space.n

# I do not understand the following
model = Sequential()
model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
model.add(Dense(16))
model.add(Activation("relu"))
model.add(Dense(16))
model.add(Activation("relu"))
model.add(Dense(16))
model.add(Activation("relu"))
model.add(Dense(nb_actions))
model.add(Activation("linear"))
print(model.summary())

# still not understanding that part
memory = SequentialMemory(limit=500, window_length=1)
policy = BoltzmannQPolicy()
dqn = DQNAgent(
    model=model,
    nb_actions=nb_actions,
    memory=memory,
    nb_steps_warmup=10,
    target_model_update=1e-2,
    policy=policy,
)
dqn.compile(Adam(lr=1e-3), metrics=["mae"])

from rl.callbacks import Callback


class ResetEnvCallback(Callback):
    env = None

    def __init__(self, env):
        self.env = env

    def on_episode_end(self, episode, logs={}):
        self.env.reset()


dqn.fit(
    env, nb_steps=1000, visualize=True, verbose=0, callbacks=[ResetEnvCallback(env)]
)

# After training is done, we save the final weights.
dqn.save_weights(
    "nn_weights/dqn_{}_{}_weights.h5f".format(
        env.spec.id, datetime.now().strftime("%Y%m%d%H%M")
    ),
    overwrite=True,
)

# Finally, evaluate our algorithm for 5 episodes.
dqn.test(env, nb_episodes=5, visualize=True)
