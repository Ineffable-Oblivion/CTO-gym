# CTO-gym
OpenAI environment for Cooperative Target Observation (CTO) domain


## Installation

Install the [OpenAI gym](https://gym.openai.com/docs/).

Then install this package via

```
pip install -e .
```

## Usage

```
import gym
import gym_cto

env = gym.make('CTO-v0')
env.initialize() #compulsory
```