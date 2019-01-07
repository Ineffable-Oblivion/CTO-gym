import gym
import random
import numpy as np
from math import sqrt
from gym.envs.classic_control import rendering

class CtoEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    """
    Summary of the the environment variables
            
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
        self.viewer = None


    # Checks whether the two points are at least one unit apart
    def acceptable(self, index, agent=False):
        if not agent:
            if index == 0:
                return True
            
            else:
                for i in xrange(index):
                    if self.distance(self.targetLocations[index], 
                                        self.targetLocations[i]) <= 1:
                        return False

                return True
        
        else:
            for i, pos in enumerate(self.targetLocations):
                if self.distance(self.agentPosition, pos) <= 1:
                        return False

            return True

    # Calculates euclidean distance between two points
    def distance(self, pos1, pos2):
        euclideanDistance = (pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2
        return sqrt(euclideanDistance)

    def reset(self):
        self.state = np.array([(0.0, 0.0)]*self.numTargets)

        for i, t in enumerate(self.targetLocations):
            if self.distance(self.agentPosition, t) <= self.sensorRange:
                self.state[i] = t

        return self.state

    def step(self, action):
        pass

    def render(self, mode='human'):
        screen_width = 600
        screen_height = 600

        self.viewer = rendering.Viewer(screen_width, screen_height)

        #Borders for neat view
        borderOffset = 50 #Reduces 50px along 4 sides
        border = rendering.Line((borderOffset, borderOffset), 
                                (screen_width - borderOffset, borderOffset))
        self.viewer.add_geom(border)
        border = rendering.Line((borderOffset, borderOffset), 
                                (borderOffset, screen_height - borderOffset))
        self.viewer.add_geom(border)
        border = rendering.Line((screen_width - borderOffset, screen_height - borderOffset), 
                                (screen_width - borderOffset, borderOffset))
        self.viewer.add_geom(border)
        border = rendering.Line((screen_width - borderOffset, screen_height - borderOffset), 
                                (borderOffset, screen_height - borderOffset))
        self.viewer.add_geom(border)

        scale = ( (screen_width - 2*borderOffset)/self.gridWidth, 
                    (screen_height - 2*borderOffset)/self.gridHeight)

        for i in self.targetLocations:
            point = (scale[0]*i[0] + borderOffset, scale[1]*i[1] + borderOffset)

            location = rendering.Transform(translation=point)
            axle = rendering.make_circle(4.0)
            axle.add_attr(location)
            axle.set_color(1.0, 0.0, 0.0)
            self.viewer.add_geom(axle)

        agent = (scale[0]*self.agentPosition[0] + borderOffset, scale[1]*self.agentPosition[1] + borderOffset)
        location = rendering.Transform(translation=agent)
        axle = rendering.make_circle(4.0)
        axle.add_attr(location)
        axle.set_color(0.0, 0.0, 1.0)
        self.viewer.add_geom(axle)

        coverage = self.viewer.draw_circle(radius=scale[0]*self.sensorRange, res=30, filled=False)
        coverage.add_attr(location)
        coverage.set_color(0.5, 0.5, 0.8)
        self.viewer.add_geom(coverage)

        return self.viewer.render(return_rgb_array = mode=='rgb_array')