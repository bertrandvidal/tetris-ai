import gym
import sys
import os
from tetris_ai.train import *


if __name__ == "__main__":
    env = gym.make("tetris_ai:tetris_gym-v0")
    agent, model = get_agent(env)
    agent.load_weights(os.path.abspath(sys.argv[1]))
    # Finally, evaluate our algorithm for 5 episodes.
    agent.test(
        env,
        nb_episodes=20,
        visualize=True,
        verbose=0,
        callbacks=[
            EpisodeRewardsCallback(),
            ActionRecorderCallback(env),
        ],
    )
