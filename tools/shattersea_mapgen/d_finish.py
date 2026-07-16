"""Finishing pass: underground bunkers, citywide item spawns, the deploy point
and global ambience."""
from lib import GROUND_TOP, ROOM_TOP
import config as C


CITY_LOOT = [
    "empty_bucket", "frag_grenade", "smoke_bomb", "semtex_pack", "health_potion",
    "energetic_potion_red", "energetic_potion_blue", "bomb_vest", "bunker_key",
    "AK47_ammo_10_50", "glock17_ammo_10_40", "beretta92fs.pistol_ammo_10_40",
    "hk.g36_ammo_20_50", "benelli.m4.shotgun_ammo_10_40",
    "magnum.revolver_ammo_5_40", "sg08.sniper.rifle_ammo_1_10",
    "tar.21.assault.rifle_ammo_10_30", "famas.f1.assault.rifle_ammo_10_20",
]


def build(m):
    m.section("UNDERGROUND BUNKERS (one beneath each district)")
    _bunker(m, "Bunker North", 664, 900, "under Meridian Plaza",
            ["bunker_key", "frag_grenade", "health_potion", "bomb_vest"])
    _bunker(m, "Bunker South", 588, 480, "under Elm Road",
            ["bunker_key", "smoke_bomb", "semtex_pack", "health_potion"])
    _bunker(m, "Bunker East", 1000, 800, "under Kensington Drive",
            ["bunker_key", "frag_grenade", "bomb_vest"])
    _bunker(m, "Bunker West", 300, 400, "under Oceanfront Drive",
            ["bunker_key", "health_potion", "life_injection", "smoke_bomb"])

    m.section("CITYWIDE ITEM SPAWNS AND AMBIENCE")
    # A broad citywide loot spread across Meridian's streets and squares.
    m.ispawn(C.ISL_X1, C.ISL_X2, C.ISL_Y1, C.ISL_Y2, 0, 0, 800, 120, CITY_LOOT)
    # gulls and a distant sea over the whole island
    m.src(C.ISL_X1, C.ISL_X2, C.ISL_Y1, C.ISL_Y2, 0, GROUND_TOP, "birds5.ogg", -14)

    m.section("DEPLOY POINT")
    m.poi((C.SPAWN_X1 + C.SPAWN_X2) // 2, (C.SPAWN_Y1 + C.SPAWN_Y2) // 2, 0,
          "the Meridian Plaza deploy point")


def _bunker(m, name, x, y, where, loot):
    """A small sealed bunker below the street, reached by a hatch ladder."""
    x1, x2, y1, y2 = x - 20, x + 20, y - 15, y + 15
    depth = 12
    bz = -depth
    m.comment(name + " (" + where + ")")
    m.tile(x1, x2, y1, y2, bz, bz, "concrete10")
    m.tile(x1 - 1, x1 - 1, y1, y2, bz, -1, "wallstone")
    m.tile(x2 + 1, x2 + 1, y1, y2, bz, -1, "wallstone")
    m.tile(x1, x2, y1 - 1, y1 - 1, bz, -1, "wallstone")
    m.tile(x1, x2, y2 + 1, y2 + 1, bz, -1, "wallstone")
    m.zone(x1, x2, y1, y2, bz, bz + ROOM_TOP, name)
    # hatch ladder from the street down into the bunker
    m.tile(x, x, y, y, bz, 0, "ladder1")
    m.zone(x, x, y, y, bz, 0, "the ladder into " + name)
    m.zone_raw(x, x, y - 1, y - 1, 0, GROUND_TOP, "the hatch to " + name)
    # control panel
    m.tile(x1 + 2, x1 + 2, y1 + 2, y1 + 2, bz, bz, "metal4")
    m.zone_raw(x1 + 2, x1 + 4, y1 + 2, y1 + 4, bz, bz + 6, name + " control panel")
    m.src(x1, x2, y1, y2, bz, bz + ROOM_TOP, "rumble.ogg", -12)
    m.ispawn(x1 + 1, x2 - 1, y1 + 1, y2 - 1, bz, bz, 5000, 3, loot)
    m.bunker(x, y, bz, name)
    m.poi(x, y, bz, name)
