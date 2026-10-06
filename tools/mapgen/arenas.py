"""The four automatic-arena maps.

Each arena used to be the same empty eighty-by-eighty box with a different
floor sound: no cover, no structure, nothing about it suited to its rules, and
a "central objective" landmark that was not an objective. These are laid out
for the fight each ruleset produces, and every one has a raised spectator
gallery behind a railing, where spectators are placed (the server looks for
the "Spectator gallery" landmark), with a stair so the map stays connected.

  Open Arsenal      rifles, a sidearm and a grenade: a walled yard with a
                    fortified command post in the middle, a barracks and a
                    warehouse on the flanks and low cover across open ground.
  Sidearm Showdown  pistols: a frontier main street with eight buildings
                    whose front and back doors open onto the street and the
                    back alleys, so every fight is short and around corners.
  Close Quarters    melee: a three-by-three grid of rooms joined by doors and
                    narrow corridors, with no sightline longer than a room.
  Demolition Ring   grenades: a ring of broken walls to bank throws off, a
                    raised mound in the centre and a bunker in each corner.

Arenas carry no loot; every combatant is issued the arena's loadout.
"""
from .builder import Map

GALLERY = "Spectator gallery"


def _gallery(m, deck, z, stair, stair_axis="y", railing=None, material="steel grating"):
    """A raised viewing deck reached by a stair, with a railing on the arena
    side. `stair` is the stair's rectangle; it climbs from the ground to the
    deck along `stair_axis` and must end beside the deck."""
    m.deck(deck, z, GALLERY, material=material, kind="platform")
    m.stair(stair, 0, z, "Gallery stair", axis=stair_axis, material="steel stairs",
            support="steel wall")
    if railing:
        m.tile(railing, z + 1, z + 2, "railing wall")
    x1, x2, y1, y2 = deck
    m.poi((x1 + x2) // 2, (y1 + y2) // 2, z, GALLERY)


def open_arsenal():
    m = Map("arena_open", "Open Arsenal", 120, 120, height=16, listed=False)
    m.area((1, 119, 1, 119), "Open Arsenal yard", "packed dirt", kind="open")
    m.quarters((1, 119, 1, 119), 0, "Open Arsenal yard")
    # The command post: thick-walled, a door on every side, a stair to its roof.
    m.room((50, 70, 50, 70), 0, "Command post", floor="concrete floor", height=5,
           wall="concrete wall")
    for r, side in (((59, 61, 50, 50), "south"), ((59, 61, 70, 70), "north"),
                    ((50, 50, 59, 61), "west"), ((70, 70, 59, 61), "east")):
        m.door(r, 0, f"Command post, {side} door", floor="concrete floor")
    m.stair((71, 72, 52, 58), 0, 5, "Command post roof stair", material="concrete stairs")
    m.poi(60, 60, 0, "Command post")
    # Flanking buildings.
    m.room((10, 30, 45, 75), 0, "Barracks", floor="floorboards", height=4, wall="brick wall")
    m.door((30, 30, 58, 61), 0, "Barracks, east door", floor="floorboards")
    m.door((10, 10, 58, 61), 0, "Barracks, west door", floor="floorboards")
    m.door((18, 21, 75, 75), 0, "Barracks, north door", floor="floorboards")
    m.room((90, 110, 45, 75), 0, "Warehouse", floor="warehouse floor", height=6,
           wall="steel wall", kind="warehouse")
    m.door((90, 90, 57, 62), 0, "Warehouse, loading door", floor="warehouse floor")
    m.door((110, 110, 58, 61), 0, "Warehouse, east door", floor="warehouse floor")
    m.door((98, 101, 45, 45), 0, "Warehouse, south door", floor="warehouse floor")
    # Low cover: sandbag walls and container stacks, too tall to step onto.
    for i, r in enumerate([(35, 40, 20, 21), (80, 85, 20, 21), (20, 21, 30, 35),
                           (98, 99, 30, 35), (35, 40, 98, 99), (80, 85, 98, 99),
                           (56, 64, 35, 36), (56, 64, 84, 85), (38, 39, 55, 65),
                           (81, 82, 55, 65)]):
        m.block(r, 0, 2, f"Cover wall {i + 1}", wall="concrete wall", roof="concrete pavement")
    for i, r in enumerate([(14, 18, 12, 15), (102, 106, 12, 15), (14, 18, 104, 107),
                           (102, 106, 104, 107)]):
        m.block(r, 0, 3, f"Container stack {i + 1}", wall="steel wall", roof="steel plate")
    m.poi(16, 13, 0, "South-west containers")
    m.poi(104, 106, 0, "North-east containers")
    for x, y in [(6, 6), (60, 6), (114, 6), (6, 40), (114, 40), (6, 80), (114, 80),
                 (6, 106), (40, 104), (80, 104), (30, 25), (90, 25)]:
        m.spawn(x, y, 0)
    _gallery(m, (40, 85, 112, 118), 6, (84, 85, 104, 111), railing=(40, 83, 112, 112))
    return m.finish()


def sidearm_showdown():
    m = Map("arena_sidearms", "Sidearm Showdown", 72, 72, height=16, listed=False)
    m.area((1, 71, 1, 71), "Showdown town", "packed dirt", kind="open")
    m.path("West back alley", (1, 11, 1, 66), "dry dirt", kind="alley")
    m.path("East back alley", (61, 71, 1, 66), "dry dirt", kind="alley")
    m.path("Main Street", (29, 43, 1, 66), "packed dirt", kind="street")
    west = [("Saloon", 4, 18), ("General store", 22, 34), ("Bank", 38, 48), ("Sheriff's office", 52, 64)]
    east = [("Hotel", 4, 18), ("Livery stable", 22, 34), ("Blacksmith", 38, 48), ("Undertaker", 52, 64)]
    for name, y1, y2 in west:
        m.room((12, 28, y1, y2), 0, name, floor="old boards", height=4, wall="timber wall")
        mid = (y1 + y2) // 2
        m.door((28, 28, mid - 1, mid + 1), 0, f"{name}, front door", floor="old boards")
        m.door((12, 12, mid - 1, mid), 0, f"{name}, back door", floor="old boards")
        m.poi(20, mid, 0, name)
    for name, y1, y2 in east:
        m.room((44, 60, y1, y2), 0, name, floor="old boards", height=4, wall="timber wall")
        mid = (y1 + y2) // 2
        m.door((44, 44, mid - 1, mid + 1), 0, f"{name}, front door", floor="old boards")
        m.door((60, 60, mid - 1, mid), 0, f"{name}, back door", floor="old boards")
        m.poi(52, mid, 0, name)
    # Cover in the street: troughs to crouch behind, wagons to stand behind.
    for i, r in enumerate([(33, 35, 12, 13), (37, 39, 30, 31), (33, 35, 46, 47), (37, 39, 58, 59)]):
        m.block(r, 0, 2, f"Wagon {i + 1}", wall="timber wall", roof="old boards")
    for i, r in enumerate([(31, 32, 22, 24), (40, 41, 40, 42)]):
        m.block(r, 0, 1, f"Water trough {i + 1}", wall="timber wall", roof="old boards")
    for x, y in [(36, 3), (36, 64), (6, 6), (6, 36), (6, 60), (66, 6), (66, 36), (66, 60),
                 (20, 11), (52, 11), (20, 58), (52, 58)]:
        m.spawn(x, y, 0)
    _gallery(m, (30, 63, 67, 71), 5, (62, 63, 58, 66), railing=(30, 61, 67, 67),
             material="timber decking")
    return m.finish()


def close_quarters():
    m = Map("arena_melee", "Close Quarters", 48, 48, height=16, listed=False)
    m.area((1, 47, 1, 47), "Close Quarters corridors", "warehouse floor", kind="corridor")
    names = [["Locker room", "Armoury", "Mess hall"],
             ["Office", "Training hall", "Showers"],
             ["Storage", "Workshop", "Briefing room"]]
    cols = [(3, 13), (17, 27), (31, 41)]
    rows = [(3, 13), (17, 27), (31, 37)]
    for ri, (y1, y2) in enumerate(rows):
        for ci, (x1, x2) in enumerate(cols):
            name = names[ri][ci]
            m.room((x1, x2, y1, y2), 0, name, floor="linoleum", height=4, wall="concrete wall")
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            m.door((mx - 1, mx, y1, y1), 0, f"{name}, south door", floor="linoleum")
            m.door((mx - 1, mx, y2, y2), 0, f"{name}, north door", floor="linoleum")
            m.door((x1, x1, my - 1, my), 0, f"{name}, west door", floor="linoleum")
            m.door((x2, x2, my - 1, my), 0, f"{name}, east door", floor="linoleum")
            m.poi(mx, my, 0, name)
    for x, y in [(5, 5), (11, 11), (19, 5), (25, 11), (33, 5), (39, 11),
                 (5, 19), (39, 25), (5, 33), (39, 35), (15, 15), (29, 29)]:
        m.spawn(x, y, 0)
    _gallery(m, (28, 46, 40, 46), 5, (44, 45, 31, 39), railing=(28, 43, 40, 40))
    return m.finish()


def demolition_ring():
    m = Map("arena_explosives", "Demolition Ring", 90, 90, height=16, listed=False)
    m.area((1, 89, 1, 89), "Demolition Ring", "gravel", kind="open")
    m.quarters((1, 89, 1, 79), 0, "Demolition Ring")
    # The broken inner ring: walls to bank throws off, with gaps to run through.
    for r in [(22, 40, 22, 22), (50, 68, 22, 22), (22, 40, 68, 68), (50, 68, 68, 68),
              (22, 22, 26, 40), (22, 22, 50, 64), (68, 68, 26, 40), (68, 68, 50, 64)]:
        m.tile(r, 0, 2, "concrete wall")
    # The central mound, with a ramp up each side.
    m.plateau((38, 52, 38, 52), "Central mound", "packed dirt", 2, side="earth wall")
    m.ramp((44, 46, 35, 37), 0, 2, "Mound, south ramp", axis="y", material="packed dirt")
    m.ramp((44, 46, 53, 55), 2, 0, "Mound, north ramp", axis="y", material="packed dirt")
    m.ramp((35, 37, 44, 46), 0, 2, "Mound, west ramp", axis="x", material="packed dirt")
    m.ramp((53, 55, 44, 46), 2, 0, "Mound, east ramp", axis="x", material="packed dirt")
    m.poi(45, 45, 2, "Central mound")
    # A bunker in each corner with its door toward the centre.
    for name, r, door in [("South-west bunker", (6, 16, 6, 16), (16, 16, 10, 12)),
                          ("South-east bunker", (74, 84, 6, 16), (74, 74, 10, 12)),
                          ("North-west bunker", (6, 16, 62, 72), (16, 16, 66, 68)),
                          ("North-east bunker", (74, 84, 62, 72), (74, 74, 66, 68))]:
        m.room(r, 0, name, floor="concrete floor", height=3, wall="concrete wall")
        m.door(door, 0, f"{name} door", floor="concrete floor")
        x1, x2, y1, y2 = r
        m.poi((x1 + x2) // 2, (y1 + y2) // 2, 0, name)
    for x, y in [(4, 30), (4, 45), (4, 56), (86, 30), (86, 45), (86, 56),
                 (30, 4), (45, 4), (60, 4), (30, 76), (60, 76), (45, 30)]:
        m.spawn(x, y, 0)
    _gallery(m, (25, 68, 82, 88), 6, (67, 68, 74, 81), railing=(25, 66, 82, 82))
    return m.finish()


TARGETS = {
    "open/arena_open.map": open_arsenal,
    "sidearms/arena_sidearms.map": sidearm_showdown,
    "melee/arena_melee.map": close_quarters,
    "explosives/arena_explosives.map": demolition_ring,
}
