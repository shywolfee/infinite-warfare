"""Install Redspot items whose server mechanics are implemented in IW.

The remaining Redspot definitions must be added alongside their gameplay
mechanics; listing an inert item in the shop would mislead players.
"""
from pathlib import Path
from import_redspot_content import AMMO_PACKS

ROOT = Path(__file__).resolve().parents[1]
ITEMS = ROOT / "iwserver/content/items/redspot"
OFFERS = ROOT / "iwserver/content/marketplace/redspot"

# ID: name, category, Redspot description adapted to IW, shop price, pack yield.
CONTENT = {
    "stored_health": ("Stored Health", "Medical", "Restore 70 to 110 health instantly.", 10, ""),
    "antibiotic": ("Antibiotic", "Medical", "Restore health gradually over 45 seconds.", 50, ""),
    "poison_drink": ("Poison Drink", "Medical", "Cure poison and restore 300 to 500 health.", 25, ""),
    "food": ("Food", "Medical", "Eat to restore a little health.", 5, ""),
    "cold_food": ("Cold Food", "Medical", "Eat to restore more health than ordinary food.", 10, ""),
    "water": ("Water", "Medical", "Pour over yourself to extinguish an active burn.", 5, ""),
    "shield": ("Shield", "Defense", "Equip one to fifteen charges that absorb ordinary hits.", 30, ""),
    "air_tank": ("Air Tank", "Defense", "Refill a worn gas mask with forty to seventy seconds of air.", 50, ""),
    "gas_mask": ("Gas Mask", "Defense", "Wear it to resist poison until its air supply runs out.", 75, ""),
    "stored_quad": ("Stored Quad", "Boosts", "Deal four times as much combat damage for thirty seconds.", 75, ""),
    "invisibility_shield": ("Invisibility Shield", "Boosts", "Hide from nearby-player reports and tracking for thirty seconds.", 50, ""),
    "bike": ("Bike", "Mobility", "Ride forward up to ten tiles on solid ground.", 75, ""),
    "horn": ("Horn", "Utility", "Blast a loud horn that nearby players can hear.", 5, ""),
    "wood_pack": ("Wood Pack", "Packages", "Open for fifteen pieces of base-building wood.", 50, "wood:15"),
    "food_pack": ("Food Pack", "Packages", "Open for ten portions of food.", 100, "food:10"),
    "cold_food_pack": ("Cold Food Pack", "Packages", "Open for ten portions of cold food.", 200, "cold_food:10"),
    "water_pack": ("Water Pack", "Packages", "Open for ten bottles of water.", 10, "water:10"),
    "spring_coil_pack": ("Spring Coil Pack", "Packages", "Open for ten coils for spring boots.", 30, "spring_coil:10"),
    "poison_dart": ("Poison Dart", "Thrown", "Throw a ballistic dart that poisons a hit opponent.", 10, ""),
    "antibiotic_dart": ("Antibiotic Dart", "Thrown", "Throw a ballistic dart that heals a teammate.", 50, ""),
    "throwing_star": ("Throwing Star", "Thrown", "Throw a fast star that hits hard without a shield.", 10, ""),
    "fire_ball": ("Fire Ball", "Thrown", "Throw an incendiary ball that burns a hit target.", 25, ""),
    "paintball": ("Paintball", "Thrown", "Tag a player so the thrower can track them.", 5, ""),
    "small_projectile": ("Small Projectile", "Thrown", "Launch a homing projectile at the nearest hostile.", 10, ""),
    "poisoned_small_projectile": ("Poisoned Small Projectile", "Thrown", "Launch a homing projectile that poisons its target.", 50, ""),
    "tasing_small_projectile": ("Tasing Small Projectile", "Thrown", "Launch a homing projectile that slows its target.", 25, ""),
    "tasing_poisoned_small_projectile": ("Tasing Poisoned Small Projectile", "Thrown", "Launch a homing projectile that poisons and slows.", 75, ""),
    "stat_pingger": ("Stat Pingger", "Thrown", "Tag a player for a report of their current combat status.", 25, ""),
    "medal": ("Medal", "Bases", "Reinforce a nearby base computer with metal.", 25, ""),
    "gas_can": ("Gas Can", "Bases", "Add five minutes of fuel to a nearby base generator.", 45, ""),
    "empty_gas_can": ("Empty Gas Can", "Bases", "Siphon five minutes of fuel from a nearby base.", 0, ""),
    "tools": ("Tools", "Bases", "Repair a nearby base computer.", 125, ""),
    "tool_box": ("Tool Box", "Bases", "Repair a nearby base computer more strongly.", 300, ""),
    "base_lock_booster": ("Base Lock Booster", "Bases", "Add two more timed pins to a base door, up to five boosters.", 350, ""),
    "base_generator_booster": ("Base Generator Booster", "Bases", "Reduce a base generator's fuel consumption, up to ten boosters.", 1000, ""),
    "sandbag": ("Sandbag", "Structures", "Build a tall defensive sandbag wall in front of you.", 50, ""),
    "ladder": ("Ladder", "Structures", "Build a climbable ladder in front of you.", 20, ""),
    "medal_pack": ("Medal Pack", "Packages", "Open for ten base-reinforcing metal pieces.", 250, "medal:10"),
    "empty_health_pod": ("Empty Health Pod", "Medical", "Store up to two hundred of your own health for later use or transfer.", 5, ""),
    "candy": ("Candy", "Boosts", "Run and jump faster for thirty seconds.", 10, ""),
    "frequency_scrambler": ("Frequency Scrambler", "Boosts", "Hide from hostile Redspot robots for thirty seconds.", 55, ""),
    "bomb_defuser": ("Bomb Defuser", "Utility", "Disarm nearby explosives except barricade bombs.", 50, ""),
    "health_mover": ("Health Mover", "Medical", "Transfer health to a teammate standing beside you.", 100, ""),
    "robot": ("Robot", "Companions", "Launch a five-minute hunter robot with inaccurate gunfire.", 100, ""),
    "fire_ball_box": ("Fire Ball Box", "Packages", "Open for ten fireballs.", 105, "fire_ball:10"),
    "throwing_star_volley": ("Throwing Star Volley", "Packages", "Open for twelve throwing stars.", 105, "throwing_star:12"),
    "matchbox": ("Matchbox", "Packages", "Open for fifteen matches.", 25, "match:15"),
    "paintball_pack": ("Paintball Pack", "Packages", "Open for ten paintballs.", 10, "paintball:10"),
    "empty_health_pod_pack": ("Empty Health Pod Pack", "Packages", "Open for ten empty health pods.", 100, "empty_health_pod:10"),
    "bitcoin": ("Bitcoin", "Currency", "Scan at a base or store to credit a variable market value.", 275, ""),
    "health_boost": ("Health Boost", "Medical", "A found health boost restores health immediately.", 0, ""),
    "food_cooler": ("Food Cooler", "Utility", "Keeps carried cold food from warming into ordinary food.", 3, ""),
    "item_grabber": ("Item Grabber", "Utility", "Pressurize and pull nearby loose items to your position.", 120, ""),
    "corpse_bomb": ("Corpse Bomb", "Explosives", "Wear it to destroy your body and belongings when killed.", 75, ""),
    "base_fridge_coolant": ("Base Fridge Coolant", "Bases", "Cool a powered base fridge for five minutes.", 100, ""),
    "base_fridge_coolant_extractor": ("Base Fridge Coolant Extractor", "Bases", "Siphon five minutes of coolant from a nearby base fridge.", 50, ""),
    "rocket_battery": ("Rocket Battery", "Explosives", "Power up and launch five ballistic rockets in a fan around you.", 50, ""),
    "stp429_mini_missile": ("STP429 Mini Missile", "Explosives", "Launch a fast ballistic mini missile with a short warning.", 100, ""),
    "claymore_remote": ("Claymore Remote", "Explosives", "Detonate the oldest armed Redspot claymore you own.", 10, ""),
    "bullet_bomb_locater": ("Bullet Bomb Locater", "Explosives", "Report nearby bullet bombs placed by you or your team.", 10, ""),
    "satellite_bomb_remote": ("Satellite Bomb Remote", "Explosives", "Transmit a launch code to detonate matching satellite bombs.", 10, ""),
    "dynamite_set": ("Dynamite Set", "Packages", "Open for dynamite and a shootable detonator.", 100, ""),
    "sm2_missile_set": ("SM2 Missile Set", "Packages", "Open for a placed missile and its pressure plate.", 50, ""),
    "item_carying_projectile": ("Item Carrying Projectile", "Delivery", "Send one physical item to map coordinates, optionally activating it on arrival.", 30, ""),
    "spy_camera": ("Spy Camera", "Surveillance", "Place a shootable remote camera with a stun zapper and a battery.", 100, ""),
    "spy_camera_controller": ("Spy Camera Controller", "Surveillance", "Connect to cameras you own to photograph, zap, or destroy them.", 20, ""),
    "battery_pack": ("Battery Pack", "Surveillance", "Recharge a nearby spy camera or deliver it there by item carrier.", 15, ""),
}
for ammo, (size, price) in AMMO_PACKS.items():
    CONTENT[f"ammo_{ammo}_pack"] = (
        f"{ammo.replace('_', ' ').title()} Pack", "Ammunition",
        f"Open for {size} compatible Redspot rounds.", price,
        f"ammo_{ammo}:{size}")

THROWN = {
    "poison_dart": ("poison", 65, 20, 35, 55, "bolt"),
    "antibiotic_dart": ("heal", 75, 0, 0, 55, "bolt"),
    "throwing_star": ("", 20, 300, 500, 75, "bolt"),
    "fire_ball": ("burn", 28, 85, 145, 23, "flame"),
    "paintball": ("tracking", 45, 3, 8, 36, "bolt"),
    "small_projectile": ("", 65, 140, 240, 37, "bolt"),
    "poisoned_small_projectile": ("poison", 65, 100, 190, 37, "bolt"),
    "tasing_small_projectile": ("slow", 65, 100, 190, 37, "bolt"),
    "tasing_poisoned_small_projectile": ("poison,slow", 65, 90, 170, 37, "bolt"),
    "stat_pingger": ("stat_ping", 80, 1, 1, 60, "bolt"),
}


def install() -> None:
    ITEMS.mkdir(parents=True, exist_ok=True)
    OFFERS.mkdir(parents=True, exist_ok=True)
    for identifier, (name, category, summary, price, contents) in CONTENT.items():
        props = [f"name={name}", f"category={category}", f"summary={summary}",
                 "give_amount=1", "disposable=true", "use_kind=redspot_item"]
        if contents:
            props.append(f"pack_contents={contents}")
        if identifier in THROWN:
            props.append(f"throw_weapon=redspot_{identifier}_projectile")
        if identifier == "robot":
            props = [f"name={name}", "category=Companions", f"summary={summary}",
                     "give_amount=1", "disposable=true", "use_kind=companion",
                     "companion_kind=robot", "companion_health=500",
                     "companion_speed=5", "companion_follow_distance=3",
                     "companion_attack_range=25", "companion_weapon_range=12",
                     "companion_damage_min=35", "companion_damage_max=95",
                     "companion_attack_cooldown_ms=1700",
                     "companion_lifetime_ms=300000",
                     "companion_sound=redspot_robot"]
        if identifier == "item_carying_projectile":
            props = [f"name={name}", "category=Delivery", f"summary={summary}",
                     "give_amount=1", "disposable=true", "use_kind=redspot_cargo"]
        if identifier in {"spy_camera", "spy_camera_controller", "battery_pack"}:
            props = [f"name={name}", "category=Surveillance", f"summary={summary}",
                     "give_amount=1", "disposable=true", "use_kind=redspot_camera"]
        (ITEMS / f"{identifier}.item").write_text("\n".join(props) + "\n", encoding="utf-8")
        if identifier in {"horn", "empty_gas_can", "health_boost"}:
            continue
        offer = [f"name={name}", f"category={category}", f"summary={summary}",
                 f"item={identifier}", "quantity=1", f"price={price}",
                 "max_order=20", "enabled=true"]
        (OFFERS / f"{identifier}.offer").write_text("\n".join(offer) + "\n", encoding="utf-8")
    weapons = ROOT / "iwserver/content/weapons/archery"
    for identifier, (effect, reach, low, high, velocity, kind) in THROWN.items():
        props = [f"name={CONTENT[identifier][0]}", "wclass=archery",
                 f"projectile_kind={kind}", f"range={reach}",
                 f"min_damage={low}", f"max_damage={high}",
                 f"muzzle_velocity={velocity}", "gravity=9.81", "drag=0.025",
                 "collision_radius=0.5", f"sound_profile=redspot_{identifier}_projectile"]
        if effect:
            props.append(f"on_hit={effect}")
        if effect == "heal":
            props.append("support_amount=500")
        if "slow" in effect:
            props.append("effect_ms=10000")
        (weapons / f"redspot_{identifier}_projectile.wpn").write_text(
            "\n".join(props) + "\n", encoding="utf-8")


if __name__ == "__main__":
    install()
