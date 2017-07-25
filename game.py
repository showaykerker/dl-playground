"""
basic game for learning reinforcement learning
"""

import numpy as np
import gym

# basic implementation

env = gym.make("CartPole-v0")
best_params = [0 for _ in range(4)]
max_steps = 0

for times in range(1000):
	observation = env.reset()
	params = np.random.random(4)
	for step in range(200): 
		action = int(np.dot(params, observation) > 0)
		observation, reward, done, info = env.step(action)
		if done:
			break
	if step == 199:
		break

print(times)

params = np.random.random(4)
observation = env.reset()
for _ in range(1000):
	action = int(np.dot(best_params, observation) > 0)
	observation, _, _, _ = env.step(action)
	env.render()

print("Completed {} steps".format(steps))

# hill climbing

env = gym.make("CartPole-v0")
best_params = np.random.rand(4) * 2 - 1
previous_best_steps = 0

for times in range(1000):
	observation = env.reset()
	delta = np.random.rand(4) * 2 - 1
	params = best_params + delta
	for step in range(200):
		action = int(np.dot(params, observation) > 0)
		observation, rewards, done, _ = env.step(action)
		if done:
			break
	if step == 199:
		break
	if step > previous_best_steps:
		previous_best_steps = step
		best_params = params

print(times)

# deep learning version

from keras.models import Sequential
from keras.layers import Dense
from keras.utils import np_utils
import gym

env = gym.make("CartPole-v0")
observation = env.reset()

model = Sequential()
model.add(Dense(2, input_shape=(4)))
model.add(Dense(1, activation="softmax"))
model.compile(
	loss="mean_squared_error",
	optimizer="adam")

value_model = Sequential()
value_model.add(Dense(10, input_shape=(4)))
value_model.add(Dense(1))
value_model.compile(
	loss="mean_squared_error",
	optimizer="adam")

for _ in xrange(1000):
	pass