execute store result score @s OneItemLimit run clear @s minecraft:rabbit_hide 0
scoreboard players operation @s OneItemLimit -= #Remaining OneItemLimit
execute if score @s OneItemLimit matches 1.. store result storage oneitemlimit:macro count int 1 run scoreboard players get @s OneItemLimit
execute if score @s OneItemLimit matches 1.. run data modify storage oneitemlimit:macro item set value "minecraft:rabbit_hide"
execute if score @s OneItemLimit matches 1.. run function oneitemlimit:clear_excess with storage oneitemlimit:macro
