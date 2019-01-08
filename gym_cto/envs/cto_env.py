import gym
import random
import numpy as np
from math import sqrt
from gym.envs.classic_control import rendering
from gym import logger

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

    def __init__(self):
        self.curr_episode = 0
        self.curr_step = 0
        self.viewer = None


    def initialize(self, targets=10, sensorRange=15, updateRate=10, targetMaxStep=100,
                    targetSpeed=1.0,
                    totalSimTime=1500, gridWidth=150, gridHeight=150):
        # general variables in the environment
        self.runTime = totalSimTime        

        #total number of targets in the simulation
        self.numTargets = targets

        #maximum time for which one target can stay oncourse for its destination
        self.targetMaxStep = targetMaxStep

        #speed of target
        self.targetSpeed = targetSpeed
        self.agentSpeed = 1.0

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
        self.targetPosIncrements = np.array([(-1000.0, -1000.0)]*self.numTargets)

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


    # Checks whether the two points are at least one unit apart
    def acceptable(self, index, agent=False):
        if not agent:
            if index == 0:
                return True            
            else:
                for i in xrange(index):
                    if self.distance(self.targetLocations[index], self.targetLocations[i]) <= 1:
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
        if self.curr_episode >= self.episodes:
            logger.warn("You are calling 'step()' even though this environment has already returned done = True. You should always call 'reset()' once you receive 'done = True'")
            return

        self.curr_episode += 1

        reward = 0
        agentReachedDest = False
        for _ in xrange(self.updateRate):
            self.curr_step += 1

            #Move targets
            for i in xrange(self.numTargets):
                self.moveTarget(i)

            #Move agent
            if not agentReachedDest:
                agentReachedDest = self.moveAgent(action)

            #Calculate reward at this step
            for i, t in enumerate(self.targetLocations):
                if self.distance(self.agentPosition, t) <= self.sensorRange:
                    reward += 1
        
        return self.reset(), reward, self.curr_episode > self.episodes, {}
            

    def moveTarget(self, idx):
        # Check if this target has been oncourse for max allowed time or it reached its destination
        if self.targetSteps[idx] == 0 or (abs(self.targetDestinations[idx][0] - self.targetLocations[idx][0]) < 1 and 
            abs(self.targetDestinations[idx][1] - self.targetLocations[idx][1]) < 1):
            self.targetDestinations[idx][0] = random.uniform(0, self.gridWidth)
            self.targetDestinations[idx][1] = random.uniform(0, self.gridHeight)            
            #Create new destination and reset step counter to max allowed time and position increments to default   
            self.targetSteps[idx] = self.targetMaxStep
            self.targetPosIncrements[idx] = np.array((-1000.0, -1000.0))

        if self.targetPosIncrements[idx][0] == -1000.0 or self.targetPosIncrements[idx][1] == -1000.0:
            self.targetPosIncrements[idx] = self.calculateIncrements(self.targetLocations[idx], 
                                                                        self.targetDestinations[idx], self.targetSpeed)       

        self.targetLocations[idx] += self.targetPosIncrements[idx]

        if self.targetLocations[idx][0] < 0:
            self.targetLocations[idx][0] = 0
        if self.targetLocations[idx][0] > self.gridWidth:
            self.targetLocations[idx][0] = self.gridWidth
        if self.targetLocations[idx][1] < 0:
            self.targetLocations[idx][1] = 0
        if self.targetLocations[idx][1] > self.gridHeight:
            self.targetLocations[idx][1] = self.gridHeight

        self.targetSteps[idx] -= 1


    def moveAgent(self, dest):
        self.agentPosition += self.calculateIncrements(self.agentPosition, dest, self.agentSpeed)

        if self.agentPosition[0] < 0:
            self.agentPosition[0] = 0
        if self.agentPosition[0] > self.gridWidth:
            self.agentPosition[0] = self.gridWidth
        if self.agentPosition[1] < 0:
            self.agentPosition[1] = 0
        if self.agentPosition[1] > self.gridHeight:
            self.agentPosition[1] = self.gridHeight

        if abs(dest[0] - self.agentPosition[0]) < 1 and abs(dest[1] - self.agentPosition[1]) < 1:
            return True
        else:
            return False

    
    def calculateIncrements(self, loc, dest, speed):
        dx = dest[0] - loc[0]
        dy = dest[1] - loc[1]

        theta = 0.0
        if abs(dx) > abs(dy):
            theta = abs(dx)
        else:
            theta = abs(dy)

        xInc = dx / theta
        yInc = dy / theta
        normalizer = sqrt(xInc**2 + yInc**2)

        xInc = (xInc / normalizer)*speed
        yInc = (yInc / normalizer)*speed

        return np.array((xInc, yInc))


    def render(self, mode='human'):
        screen_width = 600
        screen_height = 600

        #TODO - Optimize for sequential renders
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