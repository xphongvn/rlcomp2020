import sys
from DQNModel import DQN # A class of creating a deep q-learning model
from MinerEnv import MinerEnv # A class of creating a communication environment between the DQN model and the GameMiner environment (GAME_SOCKET_DUMMY.py)
from Memory import Memory # A class of creating a batch in order to store experiences for the training process

import pandas as pd
import datetime 
import numpy as np


HOST = "localhost"
PORT = 1111
if len(sys.argv) == 3:
    HOST = str(sys.argv[1])
    PORT = int(sys.argv[2])

# Create header for saving DQN learning file
now = datetime.datetime.now() #Getting the latest datetime
header = ["Ep", "Step", "Reward", "Total_reward", "Action", "Epsilon", "Done", "Termination_Code"] #Defining header for the save file
filename = "Data/data_" + now.strftime("%Y%m%d-%H%M") + ".csv" 
with open(filename, 'w') as f:
    pd.DataFrame(columns=header).to_csv(f, encoding='utf-8', index=False, header=True)

# Parameters for training a DQN model
N_EPISODE = 10000 #The number of episodes for training
MAX_STEP = 1000   #The number of steps for each episode
BATCH_SIZE = 32   #The number of experiences for each replay 
MEMORY_SIZE = 100000 #The size of the batch for storing experiences
SAVE_NETWORK = 100  # After this number of episodes, the DQN model is saved for testing later. 
INITIAL_REPLAY_SIZE = 1000 #The number of experiences are stored in the memory batch before starting replaying
INPUTNUM = 198 #The number of input values for the DQN model
ACTIONNUM = 6  #The number of actions output from the DQN model
MAP_MAX_X = 21 #Width of the Map
MAP_MAX_Y = 9  #Height of the Map

# Initialize a DQN model and a memory batch for storing experiences
DQNAgent = DQN(INPUTNUM, ACTIONNUM)
memory = Memory(MEMORY_SIZE)

# Initialize environment
minerEnv = MinerEnv(HOST, PORT) 
minerEnv.start()  # Connect to the game

train = False #
# Training
for episode_i in range(0, N_EPISODE):
    try:
        # Choosing a map in the list
        mapID = np.random.randint(1, 6)
        posID_x = np.random.randint(MAP_MAX_X)
        posID_y = np.random.randint(MAP_MAX_Y)
        request = ("map" + str(mapID) + "," + str(posID_x) + "," + str(posID_y) + ",50,1000")
        # mapID = np.random.randint(0, len(TRAING_MAP))
        # request = TRAING_MAP[mapID]
        minerEnv.send_map_info(request)

        # Getting the initial state
        minerEnv.reset()
        s = minerEnv.get_state()
        total_reward = 0
        terminate = False
        maxStep = minerEnv.state.mapInfo.maxStep
        for step in range(0, maxStep):
            action = DQNAgent.act(s)  # Getting an action from the model
            minerEnv.step(str(action))  # Performing the action in order to obtain the new state
            s_next = minerEnv.get_state()  # Getting a new state
            reward = minerEnv.get_reward()  # Getting a reward
            terminate = minerEnv.check_terminate()  # Checking the end status of the episode

            # Add transition to memory
            memory.push(s, action, reward, terminate, s_next)

            # Sample batch memory to train network
            if (memory.length > INITIAL_REPLAY_SIZE):
                batch = memory.sample(BATCH_SIZE)
                DQNAgent.replay(batch, BATCH_SIZE)
                train = True
            total_reward = total_reward + reward
            s = s_next

            # Saving data to file
            save_data = np.hstack(
                [episode_i + 1, step + 1, reward, total_reward, action, DQNAgent.epsilon, terminate]).reshape(1, 7)
            with open(filename, 'a') as f:
                pd.DataFrame(save_data).to_csv(f, encoding='utf-8', index=False, header=False)
            if terminate == True:
                break

        # Iteration to save the network architecture and weights
        if (np.mod(episode_i + 1, SAVE_NETWORK) == 0 and train == True):
            DQNAgent.target_train()  # Replace the learning weights for target model with soft replacement
            now = datetime.datetime.now()
            DQNAgent.save_model("TrainedModels/",
                                "DQNmodel_" + now.strftime("%Y%m%d-%H%M") + "_ep" + str(episode_i + 1))

            # update epsilon
        print(
            'Episode %d ends. Number of steps is: %d. Accumlated Reward = %.2f. Epsilon = %.2f .Termination code: %d' % (
            episode_i + 1, step + 1, total_reward, DQNAgent.epsilon, terminate))
        if train == True:
            DQNAgent.update_epsilon()

    except Exception as e:
        import traceback

        traceback.print_exc()
        # print("Finished.")
        break
