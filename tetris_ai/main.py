import gym
from tetris_ai.game import *

env = gym.make("tetris_ai:tetris_gym-v0")
observation = env.reset()
action_decider = RandomActionDecider()
done = False

while not done:
    env.render()
    action =  action_decider.get_action(observation)
    observation, reward, done, info = env.step(action)
    print(f"{action}: {reward} - {done}")

env.close()
