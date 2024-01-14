import json
import random
import ability
import talent_handler


class Character: # this intialises all the items of a character and finds the relevant stat values
    def __init__(self, saved_data="none"):
        f = open("items.json")
        data = json.load(f)
        f.close()
        self.items = []
        self.item_types = ['head', 'neck', 'shoulder', 'back', 'chest', 'wrist', 'hands', 'waist', 'legs', 'feet',
                           'finger', 'finger1', 'trinket', 'trinket1', 'twohand']
        if saved_data == "none":
            self.from_new(data)
        else:
            self.from_save(data, saved_data)
        self.stats = {"agi": 34 + 8 + 4 + 3, "sta": 0, "stg": 48 + 8 + 3 + 4, "ap": 151 + 20 + 60 + 55, "speed": 0,
                      "mindmg": 3, "maxdmg": 3,
                      "crit": 0, "hit": 0, "sp": 25,"sp_crit":4.8,"int":47+5}  # base stats + all buffs should add global dmg modifer for world buffs
        self.get_stats()

    def from_new(self, data):  # dont think this works cba to check
        ids = []
        for i in self.item_types:
            id = input("id for " + i + "= ")
            while not self.check_item_valid(id, i, data):
                id = input("id for " + i + "= ")
            ids.append(id)
        inp = input("Save? (y/n): ")
        if inp == "y":
            self.save_char(ids)

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
        set_num = len(set([i["id"] for i in self.items]) & set([211505, 211504, 211504])) #check for tier
        if set_num >= 2:
            self.stats["ap"] += 12
        elif set_num == 3:
            self.stats["hit"] += 1
        talents = talent_handler.TalentHandler(self.stats)
        self.stats= talents[0]
        self.procs = {
            "soc": ability.Ability(0, lambda stats: 0.70 * stats["dmg"] + 8, 199999, "physical", proc_chance=100 * (
                    7 * self.stats[
                "speed"]) / 60)}  # soc proc chacne doesn't scale dynamically with haste think this adds crusader judge in right
        self.procs.update(
            wf=ability.Ability(0,
                               lambda stats: (((stats["mindmg"] + stats["maxdmg"]) / 2) / stats["speed"] + 1.2 * stats[
                                   "ap"] / 14) * stats["speed"], 199999, "aa", procs=[self.procs["soc"]],
                               proc_chance=20))
        self.abilities = {
            "judge": ability.Ability(8, lambda stats: 0.85 * random.randint(60, 64) + 50, 3, "physical"),
            # think this adds crusader judge in right
            "heavy dynamite": ability.Ability(60, lambda stats: random.randint(128, 172), 100, "spell"),
            "melee": ability.Ability(self.stats["speed"], lambda stats: stats["dmg"], 100, "aa",
                                     procs=[self.procs["wf"], self.procs["soc"]], gcd=0, on_gcd=False)}
        for i in talents[1]:
            self.abilities.update(i)
        self.stats["agi"] = 1.1 * self.stats["agi"]  # lion buff
        self.stats["stg"] = 1.1 * self.stats["stg"]  # lion buff
        self.stats["ap"] += self.stats["stg"] * 2
        dps = ((self.stats["mindmg"] + self.stats["maxdmg"]) / 2) / self.stats["speed"]
        self.stats["dmg"] = (dps + self.stats["ap"] / 14) * self.stats["speed"]
        self.stats["crit"] = self.stats["agi"] / 20 * 0.01

    def check_item_valid(self, id, i_type, data):
        if id == "0":
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

    def save_char(self, ids):
        name = input("Name to save as: ")
        with open("items.json", "w") as outfile:
            json.dump({name: ids}, outfile)
        outfile.close()


class Instance:
    def __init__(self, time, character):
        self.time_to_sim = time
        self.save1 = character

    def start_instance(self):
        self.time = self.time_to_sim
        while self.time > 0:
            self.iterate()

    # noinspection PyUnboundLocalVariable
    def iterate(self):
        prio = 99999
        button_pressed = False
        for key in self.save1.abilities:
            if self.save1.abilities[key].current_cd <= 0:  # off cd?? then press it
                button_pressed = True
                if self.save1.abilities[key].prio < prio:  # find lowest prio button idk why the prios are backwards
                    ability = key
                    prio = self.save1.abilities[key].prio
        if button_pressed:
            self.save1.abilities[ability].do_dmg(self.save1.stats)
            if self.save1.abilities[ability].on_gcd:
                for key in self.save1.abilities:
                    self.save1.abilities[key].reduce_cd(1.5)
                self.time -= 1.5
                for key in self.save1.abilities:  #this cant create a gcd for abilities that are off gcd but make one THIS IS A REALLY STUPID WAY OF PRESSING MELEES OF GCD
                    # only really is here for melees
                    if not self.save1.abilities[key].on_gcd and self.save1.abilities[key].current_cd <= 0:  # go back in time and
                        # check if we couldve press a button off gcd
                        if self.time > 0:
                            cd_offset = self.save1.abilities[key].current_cd
                            self.save1.abilities[key].do_dmg(self.save1.stats)
                            self.save1.abilities[key].current_cd = self.save1.abilities[
                                                                 key].cd + cd_offset  # i think this works DONT CHANGE
        else:
            self.time -= 0.01  # could probaly make this bigger
            for key in self.save1.abilities:
                self.save1.abilities[key].reduce_cd(0.01)

    def calc_total_dmg(self):  # sum dmg from all abilities and procs
        dmg = 0
        for key in self.save1.abilities: # should use merge() here instead but scared ill make a proc the same name as ability
            dmg += self.save1.abilities[key].ability_dmg_total
        for key in self.save1.procs:
            dmg += self.save1.procs[key].ability_dmg_total
        return dmg

    def detailed_breakdown(self):
        detailed = {}
        for key in self.save1.abilities: # should use merge() here instead but scared ill make a proc the same name as ability
            detailed.update({key: [0, 0, 0, 0]})
            for i in range(len(detailed[key])):
                detailed[key][i] += self.save1.abilities[key].detailed_stats(self.time_to_sim)[i]
        for key in self.save1.procs:
            detailed.update({key: [0, 0, 0, 0]})
            for i in range(len(detailed[key])):
                detailed[key][i] += self.save1.procs[key].detailed_stats(self.time_to_sim)[i]
        return detailed


class Sim:
    def __init__(self): # should make it so you cant input nonsense into this but i cba
        # assume full buffs and hooman with sword or mace and armour s is 0
        inp = input("from save (y/n) ")
        if inp == "n":
            self.saved_data = "none"
        elif inp == "y":
            f = open("saves.json")
            data = json.load(f)
            f.close()
            self.saved_data = data[input("select save: " + str(data.keys()))]
        self.runs = int(input("How many runs? "))

    def run_sims(self):
        total = 0
        time = int(input("How long to run for (s)? "))
        for i in range(0, self.runs):
            character = Character(saved_data=self.saved_data)
            running = Instance(time,character)
            running.start_instance()
            total += 1.15 * running.calc_total_dmg() / time
            if i == 0:
                detailed = running.detailed_breakdown()
            else:
                c_detailed = running.detailed_breakdown()
                for key in detailed:
                    for j in range(len(detailed[key])):
                        detailed[key][j] += c_detailed[key][j]
        for key in detailed:
            for i in range(len(detailed[key])):
                detailed[key][i] = detailed[key][i] / self.runs
            print(key, ":", detailed[key][0], "presses,", detailed[key][1], "total dmg,", detailed[key][2], "dps,",
                  detailed[key][3], "avg dmg per cast")
        print(total / self.runs, "dps")


if __name__ == "__main__":
    sim1 = Sim()
    sim1.run_sims()
    input("press enter to exit")

# change how cahrecters are stored chraceter class is an init function for a charecter object that can recalulate stats on the fly
# change abilitys to be stored in chareceter 2.7x slower