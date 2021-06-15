import requests
import time
from enum import Enum
import numpy as np
import json

DONNEE = "large"
JSON_LINK = "http://localhost:8080/"+DONNEE

'''
Class Requester : to send request
'''
class Requester:
    def __init__(self, link):
        self.link = link
        self.r = requests.get(self.link).json()["tortoises"]

    def get_tortues(self):
        return self.r

    def get_top(self):
        return self.r[0]["top"]

    def get_positions(self):
        positions = []
        for pos in self.r:
            positions.append(pos["position"])
        return positions


class Turtle_type(Enum):
    PENDING = 0
    REGULAR = 1
    CYCLIC = 2
    RANDOM = 3
    TIRED = 4


class Turtle:
    def __init__(self, initial_position, ident):
        self.id = ident
        self.last_position = initial_position
        self.type = Turtle_type.PENDING
        self.parametres = {}
        self.history_speed = []
        self.random_visited = []

    def get_turtle(self):
        return {"id": self.id, "type": self.type.name, "parametres": self.parametres}

    def set_type(self, turtle_type):
        self.type = turtle_type

    def get_type(self):
        return self.type

    def reset(self, position):
        self.last_position = position
        self.history_speed = []
        self.random_visited = []

    def update_position(self, position):
        self.history_speed.append(position - self.last_position)
        self.last_position = position

    def get_speeds(self):
        return self.history_speed

    def is_random(self):
        doubling = detected_doubling(self.history_speed, self.random_visited)
        if doubling != None:
            first_index, second_index = doubling
            taille = min(second_index - first_index, len(self.history_speed) - second_index)
            acc = {}
            for i in range(1,len(self.history_speed)):
                diff = abs(self.history_speed[i] - self.history_speed[i-1])
                if diff not in acc:
                    acc[diff] = None
            if len(acc.keys()) > 2 and self.history_speed[first_index : first_index + taille] != self.history_speed[second_index : second_index + taille]:
                if self.id == 117:
                    print(f"{self.history_speed[first_index : first_index + taille]} {self.history_speed[second_index : second_index + taille]}")
                self.type = Turtle_type.RANDOM
                self.parametres = {"max": max(self.history_speed), "min": min(self.history_speed)}
                self.history_speed = []
                return True
            else:
                self.random_visited.append(self.history_speed[first_index])
                return False
        return False

    def is_cyclic(self):
        try:
            first = self.history_speed[0]
            index_second_cycle = self.history_speed[1:].index(first) + 1
            if len(self.history_speed) >= 2*index_second_cycle + 1:
                no_repeated = all(self.history_speed[0:index_second_cycle].count(element) == 1 for element in self.history_speed[0:index_second_cycle])
                if no_repeated and index_second_cycle >= 2 and self.history_speed[0:index_second_cycle] == self.history_speed[index_second_cycle:2*index_second_cycle] and self.history_speed[2*index_second_cycle] == first:# == self.history_speed[2*index_second_cycle:3*(index_second_cycle)]:
                    self.type = Turtle_type.CYCLIC
                    self.parametres = {"cycle": self.history_speed[0:index_second_cycle]}
                    self.history_speed = []
                    return True
                else :
                    return False
            else:
                return False
        except:
            return False

    def is_regular(self):
        first = self.history_speed[0]
        for speed in self.history_speed[1:]:
            if speed != first:
                return False
        self.type = Turtle_type.REGULAR
        self.parametres = {"vitesse": first}
        self.history_speed = []
        return True

    def is_tired(self):
        if self.history_speed.count(0) >= 2:
            value_max = max(self.history_speed)
            index_first_zero = self.history_speed.index(0)
            index_second_zero = index_first_zero + self.history_speed[index_first_zero + 1:].index(0)
            # print(f"{self.history_speed[index_first_zero:index_second_zero+1]}")
            # print(f"{index_first_zero} {index_second_zero}")
            if index_first_zero != len(self.history_speed) - 1:
                diff = abs(
                    self.history_speed[index_first_zero] - self.history_speed[index_first_zero + 1])
                for i in range(index_first_zero + 1, index_second_zero):
                    if self.history_speed[i + 1] != value_max:
                        if diff != abs(self.history_speed[i] - self.history_speed[i+1]):
                            return False
                self.type = Turtle_type.TIRED
                self.parametres = {"vitesse_intial": value_max, "rythme": diff}
                self.history_speed = []
                return True

    def test_type(self):
        # if self.id == 117:
        #     print(self.type.name," ",self.history_speed)
        if self.type == Turtle_type.PENDING:
            if(not(self.is_regular())):
                if(not(self.is_tired())):
                    if(not(self.is_cyclic())):
                        self.is_random()
       
        if self.type == Turtle_type.PENDING:
            print(f"{self.id} - {self.type}")
        


class Turtles:
    def __init__(self, initial_positions):
        self.turtles = []
        self.turtles_num = len(initial_positions)
        for i in range(self.turtles_num):
            self.turtles.append(Turtle(initial_positions[i], i))

    def get_json_object(self):
        return True

    def update_positions(self, new_positions):
        for i in range(self.turtles_num):
            if self.turtles[i].get_type() == Turtle_type.PENDING:
                self.turtles[i].update_position(new_positions[i])

    def reset_positions(self, new_positions):
        for i in range(self.turtles_num):
            if self.turtles[i].get_type() == Turtle_type.PENDING:
                self.turtles[i].reset(new_positions[i])

    def test_types(self):
        for i in range(self.turtles_num):
            self.turtles[i].test_type()

    def having_all_types(self):
        for i in range(self.turtles_num):
            if self.turtles[i].get_type() == Turtle_type.PENDING:
                return False
        return True
    
    def parse_json(self, filename):
        results = {"Stat": {},"results" : []}
        for i in range(self.turtles_num):
            results["results"].append(self.turtles[i].get_turtle())
            if self.turtles[i].type.name not in results["Stat"]:
                results["Stat"][self.turtles[i].type.name] = {}
                results["Stat"][self.turtles[i].type.name]["count"] = 1
                results["Stat"][self.turtles[i].type.name]["id_list"] = [self.turtles[i].id]
            else:
                results["Stat"][self.turtles[i].type.name]["count"] += 1
                results["Stat"][self.turtles[i].type.name]["id_list"].append(self.turtles[i].id)
        # for type_turt in results["Stat"]:
            # results["Stat"][type_turt]["pourcentage"] = self.turtles_num / results["Stat"][type_turt]["count"] * 100
        # print(results)
        f = open(filename + DONNEE +  "0021.json", "w")
        f.write(json.dumps(results))
        f.close()

def detected_doubling(list_speed, stop_list = []):
    hist = {}
    for i in range(len(list_speed)):
        if list_speed[i] not in stop_list:
            if list_speed[i] in hist:
                return (hist[list_speed[i]], i)
            else :
                hist[list_speed[i]] = i
    return None

'''
Read JSON every 3 seconds
'''
def request_json(link):
    before = round(time.time() * 100000)
    req = Requester(link)
    prec_top = req.get_top()
    turtles_list = Turtles(req.get_positions())
    # print(turtles_list.turtles[0].last_position,'\n')
    after = round(time.time() * 100000)
    time.sleep(3 - (after - before)/100000)
    cp = 0
    nb_rq = 0
    while(True):
        before = round(time.time() * 100000)
        req = Requester(link)
        if req.get_top() == prec_top + 1:
            prec_top = req.get_top()
            turtles_list.update_positions(req.get_positions())
            cp += 1
            if cp % 10 == 0:
                turtles_list.test_types()
                if turtles_list.having_all_types():
                    turtles_list.parse_json("res")
                    print("nb Requetes : ", nb_rq)
                    break
                if cp % 50 == 0:
                    turtles_list.parse_json("res")
            after = round(time.time() * 100000)
            print(3 - (after - before)/100000)
            if (3 - (after - before)/100000) < 0:
                print("Erreur sleep")
                before = round(time.time() * 100000)
                req = Requester(link)
                prec_top = req.get_top()
                turtles_list.reset_positions(req.get_positions())
                after = round(time.time() * 100000)
                time.sleep(3 - (after - before)/100000)
                cp = 0
            else:
                time.sleep(3 - (after - before)/100000)

        else: # En cas de tops ratés 
            print("Top raté ", prec_top, " -> ", req.get_top())
            before = round(time.time() * 100000)
            req = Requester(link)
            prec_top = req.get_top()
            turtles_list.reset_positions(req.get_positions())
            after = round(time.time() * 100000)
            time.sleep(3 - (after - before)/100000)
            cp = 0
        nb_rq += 1



request_json(JSON_LINK)
