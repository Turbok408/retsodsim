import random


class Ability: # generalise ablity class should prob make melees its own inhereited class instead of using this
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
        rating_dif = 140 - 130 # assumes you are human boss is +3lvls
        roll = random.uniform(0, 100)
        if self.school == "aa": # should make this attack table static
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
                            (4, + 5 - hit + 6.5 + 9): 2, # i think these values are wrong but idk
                            (4 + stats["crit"], 100): 1}
        for key in attack_table:
            if key[0] < roll <= key[1]:
                return attack_table[key]

    def detailed_stats(self, time):
        if self.attacks > 0:
            return [self.attacks, 1.15 * self.ability_dmg_total, 1.15 * self.ability_dmg_total / time,
                    1.15 * self.ability_dmg_total / self.attacks]
        else:
            return [0, 0, 0, 0]

class Dot(Ability): ##this just doesa all dmg at once
    def __init__(self, cd, dmg_func, prio,school,ticks):
        self.ticks = ticks
        self.time_until_next_dmg = 0
        Ability.__init__(self,cd, dmg_func, prio, school, procs=None, proc_chance=100, gcd=1.5,
                 on_gcd=True)

    def do_dmg(self, stats):
        if random.uniform(0, 100) <= self.proc_chance:
            self.current_cd = self.cd
            for i in range(self.ticks):
                hit_ratio = self.do_crit(stats)
                self.ability_dmg_total += hit_ratio * self.dmg_func(stats)
                self.attacks += 1

