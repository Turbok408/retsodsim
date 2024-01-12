# Current Issues:
no int stat in data set \
cant go oom\
set bonuses have to be added manually in character class\
no dots\
no procs from items\
flat crit rate for spells\
cant save character after creating it\
add temporary stat buffs\
add haste\
assumes you have all buffs + enchants\
assumes target has no armour\
assumes you have wowhead bis talents and runes\
judge is on gcd and doesnt get rid off seal of command (this is probably barely even a dps difference)

# To Use
easiest way to use is just add ids in saves.json in format:\
"format":[
    "head", "neck", "shoulder", "back", "chest", "wrist", "hands", "waist", "legs", "feet", "finger", "finger1", "trinket", "trinket1", "twohand"]\
use id 0 if slot is empty and run sim.py 
