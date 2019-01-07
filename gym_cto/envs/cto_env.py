import gym
import random
import numpy as np
from math import sqrt

class CtoEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    """
    Summary of the initialized the environment variables
            
        runTime
            The total time simulation runs for

        updateRate
            Time interval between each decision making/action

        episodes
            Equal to runTime / updaRate
            Simulation terminates after these many episodes

        gridWidth, gridHeight
            Dimensions of the 2D arena

        sensorRange
            The maximum distance between agent and target for the agent to notice
            the target
    
    """

    def __init__(self, targets=10, sensorRange=15, updateRate=10, targetMaxStep=100,
                    targetSpeed=1.0,
                    totalSimTime=1500, gridWidth=150, gridHeight=150):
        # general variables in the environment
        self.runTime = totalSimTime        

        #total number of targets in the simulation
        self.numTargets = targets

        #maximum time for which one target can stay oncourse for its destination
        self.targetMaxStep = targetMaxStep

        #sensor range of the observer
        self.sensorRange = sensorRange

        #time after which observer takes the decision
        self.updateRate = updateRate

        #2D field dimensions
        self.gridHeight = gridHeight
        self.gridWidth = gridWidth

        #Initialize target locations and their destinations
        self.targetLocations = np.array([(0.0, 0.0)]*self.numTargets)
        self.targetDestinations = np.array([(0.0, 0.0)]*self.numTargets)
        self.targetSteps = np.array([self.targetMaxStep]*self.numTargets)

        for i in xrange(self.numTargets):
            self.targetDestinations[i][0] = random.uniform(0, self.gridWidth)
            self.targetDestinations[i][1] = random.uniform(0, self.gridHeight)

            self.targetLocations[i][0] = random.uniform(0, self.gridWidth)
            self.targetLocations[i][1] = random.uniform(0, self.gridHeight)

            while not self.acceptable(i):
                self.targetLocations[i][0] = random.uniform(0, self.gridWidth)
                self.targetLocations[i][1] = random.uniform(0, self.gridHeight)

        #Initialize the agent and ensure it is not on top of other target
        self.agentPosition = np.array([0.0, 0.0])
        self.agentPosition[0] = random.uniform(0, self.gridWidth)
        self.agentPosition[1] = random.uniform(0, self.gridHeight)
        while not self.acceptable(-1, True):
            self.agentPosition[0] = random.uniform(0, self.gridWidth)
            self.agentPosition[1] = random.uniform(0, self.gridHeight)


        self.episodes = self.runTime / self.updateRate

        self.curr_episode = 0
        self.curr_step = 0


    # Checks whether the two points are at least one unit apart
    def acceptable(self, index, agent=False):
        if not agent:
            if index == 0:
                return True
            
            else:
                for i in xrange(index):
                    distance = (self.targetLocations[i][0] - self.targetLocations[index][0])**2
                    distance += (self.targetLocations[i][1] - self.targetLocations[index][1])**2

                    if sqrt(distance) <= 1:
                        return False

                return True
        
        else:
            for i, pos in enumerate(self.targetLocations):
                distance = (self.agentPosition[0] - pos[0])**2
                distance += (self.agentPosition[1] - pos[1])**2

                if sqrt(distance) <= 1:
                        return False

            return True


    def step(self, action):
        pass

    def reset(self):
        pass

    def render(self, mode='human', close=False):
        return