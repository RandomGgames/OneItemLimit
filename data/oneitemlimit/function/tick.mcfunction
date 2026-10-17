scoreboard players add .Timer OneItemLimit 1

execute if score .Timer OneItemLimit matches 1 as @a run function oneitemlimit:clear/diamond

execute if score .Timer OneItemLimit matches 2 run scoreboard players set .Timer OneItemLimit 0
