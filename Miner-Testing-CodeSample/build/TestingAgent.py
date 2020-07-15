from warnings import simplefilter 
simplefilter(action='ignore', category=FutureWarning)

import sys
from keras.models import model_from_json
from MinerEnv import MinerEnv
import numpy as np

ACTION_GO_LEFT = 0
ACTION_GO_RIGHT = 1
ACTION_GO_UP = 2
ACTION_GO_DOWN = 3
ACTION_FREE = 4
ACTION_CRAFT = 5

HOST = "localhost"
PORT = 1111
if len(sys.argv) == 3:
    HOST = str(sys.argv[1])
    PORT = int(sys.argv[2])

# load json and create model
json_file = open('RLModelSample.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
DQNAgent = model_from_json(loaded_model_json)
# load weights into new model
DQNAgent.load_weights("RLModelSample.h5")
print("Loaded model from disk")
status_map = {0: "STATUS_PLAYING", 1: "STATUS_ELIMINATED_WENT_OUT_MAP", 2: "STATUS_ELIMINATED_OUT_OF_ENERGY",
                  3: "STATUS_ELIMINATED_INVALID_ACTION", 4: "STATUS_STOP_EMPTY_GOLD", 5: "STATUS_STOP_END_STEP"}
try:
    # Initialize environment
    minerEnv = MinerEnv(HOST, PORT)
    minerEnv.start()  # Connect to the game
    minerEnv.reset()
    s = minerEnv.get_state()  ##Getting an initial state
    while not minerEnv.check_terminate():
        try:
            action = np.argmax(DQNAgent.predict(s.reshape(1, len(s))))  # Getting an action from the trained model
            print("next action = ", action)
            minerEnv.step(str(action))  # Performing the action in order to obtain the new state
            s_next = minerEnv.get_state()  # Getting a new state
            s = s_next
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("Finished.")
            break
    print(status_map[minerEnv.state.status])
except Exception as e:
    import traceback
    traceback.print_exc()
print("End game.")
