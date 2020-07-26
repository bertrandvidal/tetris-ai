from gym.envs.registration import register

register(
    id="tetris_gym-v0", entry_point="tetris_ai.envs:TetrisEnv",
)
