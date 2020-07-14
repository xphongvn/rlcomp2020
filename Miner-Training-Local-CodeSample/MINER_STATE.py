import json


def str_2_json(str):
    return json.loads(str, encoding="utf-8")


class MapInfo:
    def __init__(self):
        self.max_x = 0 #Width of the map
        self.max_y = 0 #Height of the map
        self.golds = [] #List of the golds in the map
        self.obstacles = []
        self.numberOfPlayers = 0
        self.maxStep = 0 #The maximum number of step is set for this map

    def init_map(self, gameInfo):
        #Initialize the map at the begining of each episode
        self.max_x = gameInfo["width"] - 1
        self.max_y = gameInfo["height"] - 1
        self.golds = gameInfo["golds"]
        self.obstacles = gameInfo["obstacles"]
        self.maxStep = gameInfo["steps"]
        self.numberOfPlayers = gameInfo["numberOfPlayers"]

    def update(self, golds, changedObstacles):
        #Update the map after every step
        self.golds = golds
        for cob in changedObstacles:
            newOb = True
            for ob in self.obstacles:
                if cob["posx"] == ob["posx"] and cob["posy"] == ob["posy"]:
                    newOb = False
                    #print("cell(", cob["posx"], ",", cob["posy"], ") change type from: ", ob["type"], " -> ",
                    #      cob["type"], " / value: ", ob["value"], " -> ", cob["value"])
                    ob["type"] = cob["type"]
                    ob["value"] = cob["value"]
                    break
            if newOb:
                self.obstacles.append(cob)
                #print("new obstacle: ", cob["posx"], ",", cob["posy"], ", type = ", cob["type"], ", value = ",
                #      cob["value"])

    def get_min_x(self):
        return min([cell["posx"] for cell in self.golds])

    def get_max_x(self):
        return max([cell["posx"] for cell in self.golds])

    def get_min_y(self):
        return min([cell["posy"] for cell in self.golds])

    def get_max_y(self):
        return max([cell["posy"] for cell in self.golds])

    def is_row_has_gold(self, y):
        return y in [cell["posy"] for cell in self.golds]

    def is_column_has_gold(self, x):
        return x in [cell["posx"] for cell in self.golds]

    def gold_amount(self, x, y): #Get the amount of golds at cell (x,y)
        for cell in self.golds:
            if x == cell["posx"] and y == cell["posy"]:
                return cell["amount"]
        return 0 

    def get_obstacle(self, x, y):  # Get the kind of the obstacle at cell(x,y)
        for cell in self.obstacles:
            if x == cell["posx"] and y == cell["posy"]:
                return cell["type"]
        return -1  # No obstacle at the cell (x,y)


class State:
    STATUS_PLAYING = 0
    STATUS_ELIMINATED_WENT_OUT_MAP = 1
    STATUS_ELIMINATED_OUT_OF_ENERGY = 2
    STATUS_ELIMINATED_INVALID_ACTION = 3
    STATUS_STOP_EMPTY_GOLD = 4
    STATUS_STOP_END_STEP = 5

    def __init__(self):
        self.end = False
        self.score = 0
        self.lastAction = None
        self.id = 0
        self.x = 0
        self.y = 0
        self.energy = 0
        self.mapInfo = MapInfo()
        self.players = []
        self.stepCount = 0
        self.status = State.STATUS_PLAYING

    def init_state(self, data): #parse data from server into object
        game_info = str_2_json(data)
        self.end = False
        self.score = 0
        self.lastAction = None
        self.id = game_info["playerId"]
        self.x = game_info["posx"]
        self.y = game_info["posy"]
        self.energy = game_info["energy"]
        self.mapInfo.init_map(game_info["gameinfo"])
        self.stepCount = 0
        self.status = State.STATUS_PLAYING
        self.players = [{"playerId": 2, "posx": self.x, "posy": self.y},
                        {"playerId": 3, "posx": self.x, "posy": self.y},
                        {"playerId": 4, "posx": self.x, "posy": self.y}]

    def update_state(self, data):
        new_state = str_2_json(data)
        for player in new_state["players"]:
            if player["playerId"] == self.id:
                self.x = player["posx"]
                self.y = player["posy"]
                self.energy = player["energy"]
                self.score = player["score"]
                self.lastAction = player["lastAction"]
                self.status = player["status"]

        self.mapInfo.update(new_state["golds"], new_state["changedObstacles"])
        self.players = new_state["players"]
        for i in range(len(self.players), 4, 1):
            self.players.append({"playerId": i, "posx": self.x, "posy": self.y})
        self.stepCount = self.stepCount + 1
