"""
solving pendulum using actor-critic model
"""

import gym
import numpy as np 
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Input
from keras.layers.merge import Add
from keras.optimizers import Adam
import keras.backend as K

import random
from collections import deque

# determines how to assign values to each state, i.e. takes the state
# and action (two-input model) and determines the corresponding value
class ActorCritic:
	def __init__(self, env):
		self.env = env

		self.learning_rate = 0.001
		self.epsilon = 1.0
		self.epsilon_decay = .995
		self.gamma = .90
		self.tau   = .125

		self.memory = deque(maxlen=2000)
		self.actor_model = self.create_actor_model()
		self.target_actor_model = self.create_actor_model()

		self.critic_model = self.create_critic_model()
		self.target_critic_model = self.create_critic_model()

	def create_actor_model(self):
		model = Sequential()
		model.add(Dense(24, input_shape=self.env.observation_space.shape, activation="relu"))
		model.add(Dense(48, activation="relu"))
		model.add(Dense(24, activation="relu"))
		model.add(Dense(self.env.action_space.shape[0]))
		
		adam  = Adam(lr=0.001)
		model.compile(loss="mse", optimizer=adam)
		return model

	def create_critic_model(self):
		state_input  = Input(shape=self.env.observation_space.shape)
		state_h1 = Dense(24, activation='relu')(state_input)
		state_h2 = Dense(48)(state_h1)
		
		action_input = Input(shape=self.env.action_space.shape)
		action_h1    = Dense(48)(action_input)
		
		merged    = Add()([state_h2, action_h1])
		merged_h1 = Dense(24, activation='relu')(merged)
		final = Dense(1, activation='relu')(merged_h1)
		model = Model(input=[state_input,action_input], output=final)
		
		adam  = Adam(lr=0.001)
		model.compile(loss="mse", optimizer=adam)
		return model

	def remember(self, cur_state, action, reward, new_state, done):
		self.memory.append([cur_state, action, reward, new_state, done])

	def act(self, cur_state):
		self.epsilon *= self.epsilon_decay
		if np.random.random() < self.epsilon:
			return self.env.action_space.sample()
		return self.actor_model.predict(cur_state)

	def _train_actor(self, samples):
		for sample in samples:
			state = sample[0]
			actor_prediction  = self.actor_model.predict(state)
			critic_prediction = self.critic_model.predict([state, actor_prediction])
			critic_grad = K.gradients(critic_prediction, actor_prediction)
			print(critic_grad)
			# train on those critic gradients
			actor_grad = K.gradients(actor_prediction, state)
			
			if None in critic_grad or None in actor_grad:
				continue
			
			critic_grad = np.array(critic_grad)
			actor_grad  = np.array(actor_grad)

			weighted_actor_grad = actor_grad * critic_grad
			weights = self.actor_model.get_weights()
			grads = zip(actor_grad, weights)
			self.actor_model.optimizer.apply_gradients(grads)

	def _train_critic(self, samples):
		for sample in samples:
			cur_state, action, reward, new_state, done = sample
			if not done:
				target_action = self.target_actor_model.predict(new_state)
				future_reward = self.target_critic_model.predict(
					[new_state, target_action])[0][0]
				reward += self.gamma * future_reward
			self.critic_model.fit([cur_state, action], reward, verbose=0)
		
	def train(self):
		batch_size = 32
		if len(self.memory) < batch_size:
			return

		rewards = []
		samples = random.sample(self.memory, batch_size)
		self._train_actor(samples)
		self._train_critic(samples)

	def _update_actor_target(self):
		actor_model_weights  = self.actor_model.get_weights()
		actor_target_weights = self.target_critic_model.get_weights()
		
		for i in range(len(actor_target_weights)):
			actor_target_weights[i] = actor_model_weights[i]
		self.target_critic_model.set_weights(actor_target_weights)

	def _update_critic_target(self):
		critic_model_weights  = self.critic_model.get_weights()
		critic_target_weights = self.critic_target_model.get_weights()
		
		for i in range(len(critic_target_weights)):
			critic_target_weights[i] = critic_model_weights[i]
		self.critic_target_model.set_weights(critic_target_weights)		

	def update_target(self):
		self._update_actor_target()
		self._update_critic_target()

env = gym.make("Pendulum-v0")
actor_critic = ActorCritic(env)

num_trials = 10000
trial_len  = 500

for _ in range(num_trials):
	cur_state = env.reset()
	action = env.action_space.sample()
	for step in range(trial_len):
		env.render()
		cur_state = cur_state.reshape((1, env.observation_space.shape[0]))
		action = actor_critic.act(cur_state)
		action = action.reshape((1, env.action_space.shape[0]))

		new_state, reward, done, _ = env.step(action)
		new_state = new_state.reshape((1, env.observation_space.shape[0]))

		actor_critic.remember(cur_state, action, reward, new_state, done)
		actor_critic.train()

		cur_state = new_state
		if done:
			break
	print("Ended in: {} steps".format(step))