execute store result score @s OneItemLimit run clear @s minecraft:brain_coral 0
scoreboard players operation @s OneItemLimit -= #Remaining OneItemLimit
execute if score @s OneItemLimit matches 1.. store result storage oneitemlimit:macro count int 1 run scoreboard players get @s OneItemLimit
execute if score @s OneItemLimit matches 1.. run data modify storage oneitemlimit:macro item set value "minecraft:brain_coral"
execute if score @s OneItemLimit matches 1.. run function oneitemlimit:clear_excess with storage oneitemlimit:macro
