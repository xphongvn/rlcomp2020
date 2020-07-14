from MINER_STATE import State
import numpy as np


class PlayerInfo:
    def __init__(self, id):
        self.playerId = id
        self.score = 0
        self.energy = 0
        self.posx = 0
        self.posy = 0
        self.lastAction = -1
        self.status = 0
        self.freeCount = 0


class Bot2:
    ACTION_GO_LEFT = 0
    ACTION_GO_RIGHT = 1
    ACTION_GO_UP = 2
    ACTION_GO_DOWN = 3
    ACTION_FREE = 4
    ACTION_CRAFT = 5

    def __init__(self, id):
        self.state = State()
        self.info = PlayerInfo(id)

    def next_action(self):
        if self.state.mapInfo.gold_amount(self.info.posx, self.info.posy) > 0:
            if self.info.energy >= 6:
                return self.ACTION_CRAFT
            else:
                return self.ACTION_FREE
        if self.info.energy < 5:
            return self.ACTION_FREE
        else:
            action = np.random.randint(0, 4)
            return action

    def new_game(self, data):
        try:
            self.state.init_state(data)
        except Exception as e:
            import traceback
            traceback.print_exc()

    def new_state(self, data):
        # action = self.next_action();
        # self.socket.send(action)
        try:
            self.state.update_state(data)
        except Exception as e:
            import traceback
            traceback.print_exc()