from gym.envs.registration import register

register(
    id='CTO-v0',
    entry_point='gym_cto.envs:CtoEnv',
)