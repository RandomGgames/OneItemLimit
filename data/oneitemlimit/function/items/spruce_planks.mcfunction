# Debug Message
tellraw @a[tag=DebugMessages] [{"text":"oneitemlimit:items/spruce_planks","color":"gray"}]

execute store result score @s OneItemLimit run clear @s minecraft:spruce_planks 0
execute store result storage minecraft:oneitemlimit count int 1 run scoreboard players operation @s OneItemLimit -= #Remaining OneItemLimit
data modify storage oneitemlimit item set value "minecraft:spruce_planks"
function oneitemlimit:clear_all_but_1 with storage minecraft:oneitemlimit
