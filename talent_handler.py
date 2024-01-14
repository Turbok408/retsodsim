# returns a stats dict with the increase in stats from talents returns [new stats(dict),new abilitys (list)]
import ability
import re
import random

def TalentHandler(stats):
    seal = "righteousness"
    stats = stats
    modifers = []
    new_abilites = []
    talents = "--50230051_156p276sna6nx"
    chest = re.findall(r"156.{2}",talents.split("_")[1])[0][5-2:]
    hands = re.findall(r"6n.{1}", talents.split("_")[1])[0][2]
    legs = re.findall(r"76.{2}", talents.split("_")[1])[0][4-2:]
    if chest == "p2":
        new_abilites.append({"ds": ability.Ability(10, lambda stats: 1.1 * stats["dmg"], 0, "physical")})
    if hands == "x":
        new_abilites.append({"cs": ability.Ability(6, lambda stats: 0.75 * stats["dmg"], 1, "physical")})
    if legs == "sn":
        new_abilites.append({"exo": ability.Ability(15, lambda stats: random.uniform(90 + stats["sp"] * 0.429,
                                                                                     102 + stats["sp"] * 0.429), 2,
                                                    "spell", )})
    holy_talents, prot_talents, ret_talents = talents.split("_")[0].split("-")
    for i in range(len(holy_talents)):
        if i == 0:
            modifers.append(lambda stats: {"stg": stats["stg"] * 1 + (0.2 * float(holy_talents[0]))}) # this is cursed asf what time in the morning did i write this?
        elif i == 1:
            modifers.append(lambda stats: {"int": stats["int"] * 1 + (0.2 * float(holy_talents[1]))})
        elif i == 5:
            new_abilites.append({"consecation": ability.Dot(8, lambda stats: 8 + 0.042 * stats["sp"], 10, "spell", 8)})
    for i in range(len(prot_talents)):
        if i == 2:
            modifers.append(lambda stats: {"hit": stats["hit"] + float(prot_talents[2])})
    for i in range(len(ret_talents)):
        if i == 6:
            modifers.append(lambda stats: {"crit": stats["crit"] + float(ret_talents[6])})
        elif i == 7:
            pass
            #new_abilites.append({"soc": ability.Ability(0, lambda stats: 0.70 * stats["dmg"] + 8, 199999, "physical",proc_chance=100 * (7 * stats["speed"]) / 60)})  # soc proc chacne doesn't scale dynamically with haste think this adds crusader judge in right
    for i in modifers:
        stats.update(i(stats))
    return (stats, new_abilites)

# be able to reduce cds + add dmg modifers
# add runes

if __name__ == "__main__":
    print(TalentHandler({"agi": 34 + 8 + 4 + 3, "sta": 0, "stg": 48 + 8 + 3 + 4, "ap": 151 + 20 + 60 + 55, "speed": 0,
                      "mindmg": 3, "maxdmg": 3,
                      "crit": 0, "hit": 0, "sp": 25,"sp_crit":4.8,"int":47+5}))
# added talents but this is very very very slow now as int intit a char for each e