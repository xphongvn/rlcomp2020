import sys
import json
import math
from random import randrange
import socket

MAP = "[[0,0,-2,100,0,0,-1,-1,-3,0,0,0,-1,-1,0,0,-3,0,-1,-1,0],[-1,-1,-2,0,0,0,-3,-1,0,-2,0,0,0,-1,0,-1,0,-2,-1,0,0],[0,0,-1,0,0,0,0,-1,-1,-1,0,0,100,0,0,0,0,50,-2,0,0],[0,0,0,0,-2,0,0,0,0,0,0,0,-1,50,-2,0,0,-1,-1,0,0],[-2,0,200,-2,-2,300,0,0,-2,-2,0,0,-3,0,-1,0,0,-3,-1,0,0],[0,-1,0,0,0,0,0,-3,0,0,-1,-1,0,0,0,0,0,0,-2,0,0],[0,-1,-1,0,0,-1,-1,0,0,700,-1,0,0,0,-2,-1,-1,0,0,0,100],[0,0,0,500,0,0,-1,0,-2,-2,-1,-1,0,0,-2,0,-3,0,0,-1,0],[-1,-1,0,-2,0,-1,-2,0,400,-2,-1,-1,500,0,-2,0,-3,100,0,0,0]]"
POS_X = 0
POS_Y = 0
E = 50
MAX_STEP = 50
W = 21
H = 9

class ObstacleInfo:
    # initial energy for obstacles: Land (key = 0): -1, Forest(key = -1): 0 (random), Trap(key = -2): -10, Swamp (key = -3): -5
    types = {0: -1, -1: 0, -2: -10, -3: -5}

    def __init__(self):
        self.type = 0
        self.posx = 0
        self.posy = 0
        self.value = 0


class GoldInfo:
    def __init__(self):
        self.posx = 0
        self.posy = 0
        self.amount = 0

    def loads(self, data):
        golds = []
        for gd in data:
            g = GoldInfo()
            g.posx = gd["posx"]
            g.posy = gd["posy"]
            g.amount = gd["amount"]
            golds.append(g)
        return golds


class PlayerInfo:
    STATUS_PLAYING = 0
    STATUS_ELIMINATED_WENT_OUT_MAP = 1
    STATUS_ELIMINATED_OUT_OF_ENERGY = 2
    STATUS_ELIMINATED_INVALID_ACTION = 3
    STATUS_STOP_EMPTY_GOLD = 4
    STATUS_STOP_END_STEP = 5

    def __init__(self, id):
        self.playerId = id
        self.score = 0
        self.energy = E
        self.posx = POS_X
        self.posy = POS_Y
        self.lastAction = 0
        self.status = PlayerInfo.STATUS_PLAYING
        self.freeCount = 0


class GameInfo:
    def __init__(self):
        self.numberOfPlayers = 1
        self.width = W
        self.height = H
        self.steps = MAX_STEP
        self.golds = []
        self.obstacles = []

    def loads(self, data):
        m = GameInfo()
        m.width = data["width"]
        m.height = data["height"]
        m.golds = GoldInfo().loads(data["golds"])
        m.obstacles = data["obstacles"]
        m.numberOfPlayers = data["numberOfPlayers"]
        m.steps = data["steps"]
        return m


class UserMatch:
    def __init__(self):
        self.playerId = 1
        self.posx = POS_X
        self.posy = POS_Y
        self.energy = E
        self.gameinfo = GameInfo()

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class StepState:
    def __init__(self):
        self.players = []
        self.golds = []
        self.changedObstacles = []

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class GameSocket:
    bog_energy_chain = {-5: -20, -20: -40, -40: -100, -100: -100}

    def __init__(self):
        self.stepCount = 0
        self.maxStep = MAX_STEP
        self.userMatch = UserMatch()
        self.user = PlayerInfo(1)
        self.stepState = StepState()
        self.map = json.loads(MAP)  # running map info: 0->Land, -1->Forest, -2->Trap, -3:Swamp, >0:Gold
        self.energyOnMap = json.loads(MAP)  # self.energyOnMap[x][y]: <0, amount of energy which player will consume if it move into (x,y)
        self.E = E
        self.stepCount = 0
        self.craftUsers = []  # players that craft at current step - for calculating amount of gold
        self.craftMap = {}  # cells that players craft at current step, key: x_y, value: number of players that craft at (x,y)

    def setup(self):
        self.init_map()
        self.maxStep = self.userMatch.gameinfo.steps

        # init data for players
        self.stepState.players = [self.user]
        self.E = self.userMatch.energy

    def init_map(self):  # load map info
        i = 0
        while i < len(self.map):
            j = 0
            while j < len(self.map[i]):
                if self.map[i][j] > 0:  # gold
                    g = GoldInfo()
                    g.posx = j
                    g.posy = i
                    g.amount = self.map[i][j]
                    self.userMatch.gameinfo.golds.append(g)
                else:  # obstacles
                    o = ObstacleInfo()
                    o.posx = j
                    o.posy = i
                    o.type = -self.map[i][j]
                    o.value = ObstacleInfo.types[self.map[i][j]]
                    self.userMatch.gameinfo.obstacles.append(o)
                j += 1
            i += 1
        self.stepState.golds = self.userMatch.gameinfo.golds
        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if self.map[x][y] > 0:  # gold
                    self.energyOnMap[x][y] = -4
                else:  # obstacles
                    self.energyOnMap[x][y] = ObstacleInfo.types[self.map[x][y]]

    def get_game_info(self):
        data = self.userMatch.to_json()
        print("send: ", data)
        return data

    def get_step(self):  # send data to player (simulate player's receive request)
        self.stepCount = self.stepCount + 1
        if self.stepCount >= self.maxStep:
            for player in self.stepState.players:
                player.status = PlayerInfo.STATUS_STOP_END_STEP
        data = self.stepState.to_json()
        return data

    def receive(self, message):  # receive message from player (simulate send request from player)
        self.stepState.changedObstacles = []
        action = int(message)
        # print("Action = ", action)
        self.user.lastAction = action
        self.craftUsers = []
        self.step_action(self.user, action)
        self.action_5_craft()
        for c in self.stepState.changedObstacles:
            self.map[c["posy"]][c["posx"]] = -c["type"]
            self.energyOnMap[c["posy"]][c["posx"]] = c["value"]

    def step_action(self, user, action):
        switcher = {
            0: self.action_0_left,
            1: self.action_1_right,
            2: self.action_2_up,
            3: self.action_3_down,
            4: self.action_4_free,
            5: self.action_5_craft_pre
        }
        func = switcher.get(action, self.invalid_action)
        func(user)

    def action_5_craft_pre(self, user):  # collect players who craft at current step
        user.freeCount = 0
        if self.map[user.posy][user.posx] <= 0:  # craft at the non-gold cell
            user.energy -= 10
            if user.energy <= 0:
                user.status = PlayerInfo.STATUS_ELIMINATED_OUT_OF_ENERGY
                user.lastAction = 6 #eliminated
        else:
            user.energy -= 5
            if user.energy > 0:
                self.craftUsers.append(user)
                key = str(user.posx) + "_" + str(user.posy)
                if key in self.craftMap:
                    count = self.craftMap[key]
                    self.craftMap[key] = count + 1
                else:
                    self.craftMap[key] = 1
            else:
                user.status = PlayerInfo.STATUS_ELIMINATED_OUT_OF_ENERGY
                user.lastAction = 6 #eliminated

    def action_0_left(self, user):  # user go left
        user.freeCount = 0
        user.posx = user.posx - 1
        if user.posx < 0:
            user.status = PlayerInfo.STATUS_ELIMINATED_WENT_OUT_MAP
            user.lastAction = 6 #eliminated
        else:
            self.go_to_pos(user)

    def action_1_right(self, user):  # user go right
        user.freeCount = 0
        user.posx = user.posx + 1
        if user.posx >= self.userMatch.gameinfo.width:
            user.status = PlayerInfo.STATUS_ELIMINATED_WENT_OUT_MAP
            user.lastAction = 6 #eliminated
        else:
            self.go_to_pos(user)

    def action_2_up(self, user):  # user go up
        user.freeCount = 0
        user.posy = user.posy - 1
        if user.posy < 0:
            user.status = PlayerInfo.STATUS_ELIMINATED_WENT_OUT_MAP
            user.lastAction = 6 #eliminated
        else:
            self.go_to_pos(user)

    def action_3_down(self, user):  # user go right
        user.freeCount = 0
        user.posy = user.posy + 1
        if user.posy >= self.userMatch.gameinfo.height:
            user.status = PlayerInfo.STATUS_ELIMINATED_WENT_OUT_MAP
            user.lastAction = 6 #eliminated
        else:
            self.go_to_pos(user)

    def action_4_free(self, user):  # user free
        user.freeCount += 1
        if user.freeCount == 1:
            user.energy += int(self.E / 4)
        elif user.freeCount == 2:
            user.energy += int(self.E / 3)
        elif user.freeCount == 3:
            user.energy += int(self.E / 2)
        else:
            user.energy = self.E
        if user.energy > self.E:
            user.energy = self.E

    def action_5_craft(self):
        craftCount = len(self.craftUsers)
        # print ("craftCount",craftCount)
        if (craftCount > 0):
            for user in self.craftUsers:
                x = user.posx
                y = user.posy
                key = str(user.posx) + "_" + str(user.posy)
                c = self.craftMap[key]
                m = min(math.ceil(self.map[y][x] / c), 50)
                user.score += m
                # print ("user", user.playerId, m)
            for user in self.craftUsers:
                x = user.posx
                y = user.posy
                key = str(user.posx) + "_" + str(user.posy)
                if key in self.craftMap:
                    c = self.craftMap[key]
                    del self.craftMap[key]
                    m = min(math.ceil(self.map[y][x] / c), 50)
                    self.map[y][x] -= m * c
                    if self.map[y][x] < 0:
                        self.map[y][x] = 0
                        self.energyOnMap[y][x] = ObstacleInfo.types[0]
                    for g in self.stepState.golds:
                        if g.posx == x and g.posy == y:
                            g.amount = self.map[y][x]
                            if g.amount == 0:
                                self.stepState.golds.remove(g)
                                self.add_changed_obstacle(x, y, 0, ObstacleInfo.types[0])
                                if len(self.stepState.golds) == 0:
                                    for player in self.stepState.players:
                                        player.status = PlayerInfo.STATUS_STOP_EMPTY_GOLD
                            break;
            self.craftMap = {}

    def invalid_action(self, user):
        user.status = PlayerInfo.STATUS_ELIMINATED_INVALID_ACTION
        user.lastAction = 6 #eliminated

    def go_to_pos(self, user):  # player move to cell(x,y)
        if self.map[user.posy][user.posx] == -1:
            user.energy -= randrange(16) + 5
        elif self.map[user.posy][user.posx] == 0:
            user.energy += self.energyOnMap[user.posy][user.posx]
        elif self.map[user.posy][user.posx] == -2:
            user.energy += self.energyOnMap[user.posy][user.posx]
            self.add_changed_obstacle(user.posx, user.posy, 0, ObstacleInfo.types[0])
        elif self.map[user.posy][user.posx] == -3:
            user.energy += self.energyOnMap[user.posy][user.posx]
            self.add_changed_obstacle(user.posx, user.posy, 3,
                                      self.bog_energy_chain[self.energyOnMap[user.posy][user.posx]])
        else:
            user.energy -= 4
        if user.energy <= 0:
            user.status = PlayerInfo.STATUS_ELIMINATED_OUT_OF_ENERGY
            user.lastAction = 6 #eliminated

    def add_changed_obstacle(self, x, y, t, v):
        added = False
        for o in self.stepState.changedObstacles:
            if o["posx"] == x and o["posy"] == y:
                added = True
                break
        if not added:
            o = {}
            o["posx"] = x
            o["posy"] = y
            o["type"] = t
            o["value"] = v
            self.stepState.changedObstacles.append(o)


if __name__ == "__main__":

    HOST = "localhost"
    PORT = int(sys.argv[1])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('# Socket created')

    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print('# Bind failed. ')
        sys.exit()
    s.listen(10)
    conn, addr = s.accept()
    print('# Connected to ' + addr[0] + ':' + str(addr[1]))

    game = GameSocket()
    game.setup()
    conn.send(bytes(game.get_game_info(),"utf-8"))
    while game.user.status == 0:
        data = conn.recv(1024)
        game.receive(data)
        conn.send(bytes(game.get_step(), "utf-8"))

    s.close()
    print("Player score: ", game.user.score)