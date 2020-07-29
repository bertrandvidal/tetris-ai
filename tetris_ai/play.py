import gym
import sys
import os
from tetris_ai.train import get_agent

env = gym.make("tetris_ai:tetris_gym-v0")

if __name__ == "__main__":
    agent = get_agent()
    agent.load_weights(os.path.abspath(sys.argv[1]))
    # Finally, evaluate our algorithm for 5 episodes.
    agent.test(env, nb_episodes=5, visualize=True, verbose=0)
