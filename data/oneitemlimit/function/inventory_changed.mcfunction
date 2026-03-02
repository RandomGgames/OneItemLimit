# Debug Message
tellraw @a[tag=DebugMessages] [{"text":"oneitemlimit:inventory_changed","color":"gray"}]

schedule clear oneitemlimit:reset_inventory_changed_advancement
schedule function oneitemlimit:reset_inventory_changed_advancement 1 append

execute as @s run function oneitemlimit:items/spruce_planks
