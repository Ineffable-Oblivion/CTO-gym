import gym

class CtoEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, targets=10, sensorRange=15, updateRate=10, totalSimTime=1500):
        # general variables in the environment
        self.runTime = totalSimTime        

        #total number of targets in the simulation
        self.numTargets = targets 

        #sensor range of the observer
        self.sensorRange = sensorRange

        #time after which observer takes the decision
        self.updateRate = updateRate

        self.episodes = self.runTime / self.updateRate

        self.curr_episode = 0



    def step(self, action):
        pass

    def reset(self):
        pass

    def render(self, mode='human', close=False):
        return