import numpy as np
import random

class Memory:
        
    capacity = None
    
    
    def __init__(
            self,
            capacity,
            length = None,
            states = None,
            actions = None,
            rewards = None,
            dones = None,
            states2 = None,       
    ):
        self.capacity = capacity
        self.length = 0
        self.states = states
        self.actions = actions
        self.rewards = rewards
        self.dones = dones
        self.states2 = states2

    def push(self, s, a, r, done, s2):
        if self.states is None:
            self.states = s
            self.actions = a
            self.rewards = r
            self.dones = done
            self.states2 = s2
        else:
            self.states = np.vstack((self.states,s))
            self.actions = np.vstack((self.actions,a))
            self.rewards = np.vstack((self.rewards, r))
            self.dones = np.vstack((self.dones, done))
            self.states2 = np.vstack((self.states2,s2))
        
        self.length = self.length + 1
            
        if (self.length > self.capacity): 
            self.states = np.delete(self.states,(0), axis = 0)
            self.actions = np.delete(self.actions,(0), axis = 0)
            self.rewards = np.delete(self.rewards,(0), axis = 0)
            self.dones = np.delete(self.dones,(0), axis = 0)
            self.states2 = np.delete(self.states2,(0), axis = 0)           
            self.length = self.length - 1
            
        
    def sample(self,batch_size):
        if (self.length >= batch_size):
            idx = random.sample(range(0,self.length),batch_size)
            s = self.states[idx,:]
            a = self.actions[idx,:]
            r = self.rewards[idx,:]
            d = self.dones[idx,:]
            s2 = self.states2[idx,:]
                
            return list([s,a,r,s2,d])
                    
