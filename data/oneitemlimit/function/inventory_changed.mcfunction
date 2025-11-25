# Debug Message
tellraw @a[tag=DebugMessages] [{"text":"oneitemlimit:inventory_changed","color":"gray"}]

tellraw @s {"text":"Your inventory changed!"}
advancement revoke @s only oneitemlimit:inventory_changed
