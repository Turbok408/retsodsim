import json
import random


class Character:
    def __init__(self,saved_data="none"):
        f = open("items.json")
        data = json.load(f)
        self.items = []
        self.item_types = ['head', 'neck', 'shoulder', 'back', 'chest', 'wrist', 'hands', 'waist', 'legs', 'feet',
                           'finger', 'finger1', 'trinket', 'trinket1', 'twohand']
        if saved_data == "none":
            self.from_new(data)
        else:
            self.from_save(data, saved_data)
        self.stats = {"agi": 34 + 8 + 4 + 3, "sta": 0, "stg": 48 + 8 + 3 + 4, "ap": 151 + 20 + 60 + 55, "speed": 0,
                      "mindmg": 3, "maxdmg": 3,
                      "crit": 5 + 2, "hit": 3, "sp": 25}  # base stats + all buffs
        self.get_stats()
        self.stats["agi"] = 1.1 * self.stats["agi"]  # lion buff
        self.stats["stg"] = 1.1 * self.stats["stg"]  # lion buff
        self.stats["ap"] += self.stats["stg"] * 2
        dps = ((self.stats["mindmg"] + self.stats["maxdmg"]) / 2) / self.stats["speed"]
        self.stats["dmg"] = (dps + self.stats["ap"] / 14) * self.stats["speed"]
        self.stats["crit"] = self.stats["agi"] / 20 * 0.01 + 0.07
        print(self.stats)

    def from_new(self, data): # dont think this works cba to check
        for i in self.item_types:
            id = input("id for " + i + "= ")
            while not self.check_item_valid(id, i, data):
                id = input("id for " + i + "= ")

    def from_save(self, data, saved_data):
        for i in range(len(saved_data)):
            if self.check_item_valid(saved_data[i], self.item_types[i], data):
                self.items.append(data[saved_data[i]])
            else:
                print("corrupted save")

    def get_stats(self):
        pos_attributes = [i for i in self.stats.keys()]
        for i in range(len(self.items)):
            for key in self.items[i].keys():

                if key in pos_attributes:
                    self.stats[key] += self.items[i][key]

    def check_item_valid(self, id, i_type, data):
        if id =="0":
            return True
        else:
            try:
                if data[id]["slot"] == i_type or data[id]["slot"] == i_type + "1":  # see if item is in database stored
                    # as finger1 so has to check "finger"+"1"
                    return True
                else:
                    print("Item type wrong" + i_type)
                    return False
            except:  # this is kinda stupid but its honest work
                print("Item does not exist " + i_type)
                return False





class Ability:
    def __init__(self, cd, dmg_func, prio, school, procs=None, proc_chance=100, gcd=1.5,
                 on_gcd=True):  # no internal gcd for procs
        if procs is None:
            procs = []
        self.current_cd = 0
        self.cd = cd
        self.school = school
        self.prio = prio
        self.dmg_func = dmg_func
        self.procs = procs
        self.proc_chance = proc_chance
        self.ability_dmg_total = 0
        self.attacks = 0
        self.gcd = gcd
        self.on_gcd = on_gcd

    def do_dmg(self, stats):
        if random.uniform(0, 100) <= self.proc_chance:  # check if we procced
            self.current_cd = self.cd  # put back on cd
            hit_ratio = self.do_crit(stats)  # hit??? did we crit???
            self.ability_dmg_total += hit_ratio * self.dmg_func(stats)
            if hit_ratio > 0:  # if we hit do some procs
                for i in range(len(self.procs)):
                    self.procs[i].do_dmg(stats)
            self.attacks += 1

    def reduce_cd(self, time):
        self.current_cd -= time

    def do_crit(self,
                stats):  # this will break for having more than 5 assumes boss = +3lvls and you are humoon with
        # sword or mace spell crit has no int so values is 9%
        hit = stats["hit"]
        glance_chance = 10 + 2 * 3
        rating_dif = 140 - 130
        roll = random.uniform(0, 100)
        if self.school == "aa":
            attack_table = {(0, 5 - hit): 0,  ##5% chance to miss?
                            (5 - hit, 5 - hit + 6.5): 0,
                            (5 - hit + 6.5, glance_chance + 5 - hit + 6.5): random.uniform(
                                min(0.91, 1.3 - 0.05 * rating_dif), 1.2 - 0.03 * rating_dif),
                            (glance_chance + 5 - hit + 6.5, glance_chance + 5 - hit + 6.5 + stats["crit"]): 2,
                            (glance_chance + 5 - hit + 6.5 + stats["crit"], 100): 1}
        elif self.school == "physical":
            attack_table = {(0, 5 - hit): 0,  ##5% chance to miss?
                            (5 - hit, 5 - hit + 6.5): 0,
                            (+ 5 - hit + 6.5, + 5 - hit + 6.5 + stats["crit"]): 2,
                            (+ 5 - hit + 6.5 + stats["crit"], 100): 1}
        elif self.school == "spell":
            attack_table = {(0, 4): 0,  ##4% chance to miss?
                            (4, + 5 - hit + 6.5 + 9): 2,
                            (4 + stats["crit"], 100): 1}
        for key in attack_table:
            if key[0] < roll <= key[1]:
                return attack_table[key]

    def detailed_stats(self, time):
        if self.attacks > 0:
            return [self.attacks, 1.15 * self.ability_dmg_total, 1.15 * self.ability_dmg_total / time,
                1.15 * self.ability_dmg_total / self.attacks]
        else:
            return [0,0,0,0]


class Instance:
    def __init__(self, time,character):
        self.time_to_sim = time
        self.save1 = character
        self.procs = {"soc": Ability(0, lambda stats: 0.70 * stats["dmg"]+8, 199999, "physical", proc_chance=100 * (
                7 * self.save1.stats["speed"]) / 60)}  # soc proc chacne doesn't scale dynamically with haste think this adds crusader judge in right
        self.procs.update(
            wf=Ability(0, lambda stats: (((stats["mindmg"] + stats["maxdmg"]) / 2) / stats["speed"] + 1.2*stats["ap"] / 14) * stats["speed"], 199999, "aa", procs=[self.procs["soc"]], proc_chance=20))
        self.abilities = {"ds": Ability(10, lambda stats: 1.1 * stats["dmg"], 0, "physical"),
                          "cs": Ability(6, lambda stats: 0.75 * stats["dmg"], 1, "physical"),
                          "judge": Ability(8, lambda stats: 0.85 * random.randint(60, 64)+50, 3, "physical"),# think this adds crusader judge in right
                          "heavy dynamite": Ability(60, lambda stats:  random.randint(128, 172), 100, "spell"),
                          "exo": Ability(15, lambda stats: random.uniform(90 + stats["sp"] * 0.429,
                                                                         102 + stats["sp"] * 0.429), 2, "spell", ),
                          "melee": Ability(self.save1.stats["speed"], lambda stats: stats["dmg"], 100, "aa",
                                           procs=[self.procs["wf"], self.procs["soc"]], gcd=0, on_gcd=False)}
    def start_instance(self):
        self.time = self.time_to_sim
        while self.time > 0:
            self.iterate()

    # noinspection PyUnboundLocalVariable
    def iterate(self):
        prio = 99999
        button_pressed = False
        for key in self.abilities:
            if self.abilities[key].current_cd <= 0:  # off cd?? then press it
                button_pressed = True
                if self.abilities[key].prio < prio:  # find lowest prio button idk why the prios are backwards
                    ability = key
                    prio = self.abilities[key].prio
        if button_pressed:
            self.abilities[ability].do_dmg(self.save1.stats)
            if self.abilities[ability].on_gcd:
                for key in self.abilities:
                    self.abilities[key].reduce_cd(1.5)
                self.time -= 1.5
                for key in self.abilities:  # #this cant create a gcd for abilities that are off gcd but make one
                    # only really is here for melees
                    if not self.abilities[key].on_gcd and self.abilities[key].current_cd <= 0:  # go back in time and
                        # check if we couldve press a button off gcd
                        if self.time > 0:
                            cd_offset = self.abilities[key].current_cd
                            self.abilities[key].do_dmg(self.save1.stats)
                            self.abilities[key].current_cd = self.abilities[
                                                                 key].cd + cd_offset  # i think this works DONT CHANGE
        else:
            self.time -= 0.01  # probabily doesnt need to be smaller
            for key in self.abilities:
                self.abilities[key].reduce_cd(0.01)

    def calc_total_dmg(self):  # sum dmg from all abilities and procs
        dmg = 0
        for key in self.abilities:
            dmg += self.abilities[key].ability_dmg_total
        for key in self.procs:
            dmg += self.procs[key].ability_dmg_total
        return dmg

    def detailed_breakdown(self):
        detailed = {}
        for key in self.abilities:
            detailed.update({key: [0, 0, 0, 0]})
            for i in range(len(detailed[key])):
                detailed[key][i] += self.abilities[key].detailed_stats(self.time_to_sim)[i]
        for key in self.procs:
            detailed.update({key: [0, 0, 0, 0]})
            for i in range(len(detailed[key])):
                detailed[key][i] += self.procs[key].detailed_stats(self.time_to_sim)[i]
        return detailed

class Sim:
    def __init__(self):
        # assume full buffs and hooman with sword or mace and armour s is 0
        inp = input("from save (y/n) ")
        if inp == "n":
            self.character = Character()
        elif inp == "y":
            f = open("saves.json")
            data = json.load(f)
            inp1=input("select save: "+str(data.keys()))
            self.character = Character(saved_data=data[inp1])
        self.runs = int(input("How many runs? "))

    def run_sims(self):
        total=0
        time = int(input("How long to run for? "))
        for i in range(0, self.runs):
            running = Instance(time,self.character)
            running.start_instance()
            total += 1.15 * running.calc_total_dmg() / time
            if i == 0:
                detailed = running.detailed_breakdown()
            else:
                c_detailed = running.detailed_breakdown()
                for key in detailed:
                    for j in range(len(detailed[key])):
                        detailed[key][j] += c_detailed[key][j]  # wtf is this doing huhu

        for key in detailed:
            for i in range(len(detailed[key])):
                detailed[key][i] = detailed[key][i] / self.runs
            print(key,":", detailed[key][0], "presses,", detailed[key][1], "total dmg,", detailed[key][2], "dps,",
                  detailed[key][3], "avg dmg per cast")
        print(total / self.runs,"dps")


if __name__ == "__main__":
    sim1 = Sim()
    sim1.run_sims()


