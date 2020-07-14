# -*- coding: utf-8 -*-
from warnings import simplefilter 
simplefilter(action='ignore', category=FutureWarning)

import numpy as np
from keras.models import Sequential
from keras.models import model_from_json
from keras.layers import Dense, Activation
from keras import optimizers
from keras import backend as K
import tensorflow as tf
from random import random, randrange


# Deep Q Network off-policy
class DQN: 
   
    def __init__(
            self,
            input_dim, #The number of inputs for the DQN network
            action_space, #The number of actions for the DQN network
            gamma = 0.99, #The discount factor
            epsilon = 1, #Epsilon - the exploration factor
            epsilon_min = 0.01, #The minimum epsilon 
            epsilon_decay = 0.999,#The decay epislon for each update_epsilon time
            learning_rate = 0.00025, #The learning rate for the DQN network
            tau = 0.125, #The factor for updating the DQN target network from the DQN network
            model = None, #The DQN model
            target_model = None, #The DQN target model 
            sess=None
            
    ):
      self.input_dim = input_dim
      self.action_space = action_space
      self.gamma = gamma
      self.epsilon = epsilon
      self.epsilon_min = epsilon_min
      self.epsilon_decay = epsilon_decay
      self.learning_rate = learning_rate
      self.tau = tau
            
      #Creating networks
      self.model        = self.create_model() #Creating the DQN model
      self.target_model = self.create_model() #Creating the DQN target model
      
      #Tensorflow GPU optimization
      config = tf.compat.v1.ConfigProto()
      config.gpu_options.allow_growth = True
      self.sess = tf.compat.v1.Session(config=config)
      K.set_session(sess)
      self.sess.run( tf.compat.v1.global_variables_initializer()) 
      
    def create_model(self):
      #Creating the network
      #Two hidden layers (300,300), their activation is ReLu
      #One output layer with action_space of nodes, activation is linear.
      model = Sequential()
      model.add(Dense(300, input_dim=self.input_dim))
      model.add(Activation('relu'))
      model.add(Dense(300))
      model.add(Activation('relu'))
      model.add(Dense(self.action_space))
      model.add(Activation('linear'))    
      #adam = optimizers.adam(lr=self.learning_rate)
      sgd = optimizers.SGD(lr=self.learning_rate, decay=1e-6, momentum=0.95)
      model.compile(optimizer = sgd,
              loss='mse')
      return model
  
    
    def act(self,state):
      #Get the index of the maximum Q values      
      a_max = np.argmax(self.model.predict(state.reshape(1,len(state))))      
      if (random() < self.epsilon):
        a_chosen = randrange(self.action_space)
      else:
        a_chosen = a_max      
      return a_chosen
    
    
    def replay(self,samples,batch_size):
      inputs = np.zeros((batch_size, self.input_dim))
      targets = np.zeros((batch_size, self.action_space))
      
      for i in range(0,batch_size):
        state = samples[0][i,:]
        action = samples[1][i]
        reward = samples[2][i]
        new_state = samples[3][i,:]
        done= samples[4][i]
        
        inputs[i,:] = state
        targets[i,:] = self.target_model.predict(state.reshape(1,len(state)))        
        if done:
          targets[i,action] = reward # if terminated, only equals reward
        else:
          Q_future = np.max(self.target_model.predict(new_state.reshape(1,len(new_state))))
          targets[i,action] = reward + Q_future * self.gamma
      #Training
      loss = self.model.train_on_batch(inputs, targets)  
    
    def target_train(self): 
      weights = self.model.get_weights()
      target_weights = self.target_model.get_weights()
      for i in range(0, len(target_weights)):
        target_weights[i] = weights[i] * self.tau + target_weights[i] * (1 - self.tau)
      
      self.target_model.set_weights(target_weights) 
    
    
    def update_epsilon(self):
      self.epsilon =  self.epsilon*self.epsilon_decay
      self.epsilon =  max(self.epsilon_min, self.epsilon)
    
    
    def save_model(self,path, model_name):
        # serialize model to JSON
        model_json = self.model.to_json()
        with open(path + model_name + ".json", "w") as json_file:
            json_file.write(model_json)
            # serialize weights to HDF5
            self.model.save_weights(path + model_name + ".h5")
            print("Saved model to disk")
 

