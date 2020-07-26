import gym
from tetris_ai.game import *

env = gym.make("tetris_ai:tetris_gym-v0")
observation = env.reset()
action_decider = RandomActionDecider()

for iteration in range(50):
    env.render()
    action =  action_decider.get_action(observation)
    observation, reward, done, info = env.step(action)
    if done:
        continue

env.close()
pygame.quit()
