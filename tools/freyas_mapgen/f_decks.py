"""The seven decks of Freya's Ascent, from Deck 1 (storage, with the airlock)
up to Deck 7 (the bridge)."""
from lib import ROOM_TOP
import structures as S
import config as C
from f_common import deck


def build(m):
    m.section("DECK 1 - Storage and EVA (airlock deck)")
    deck(m, C.DECK1, "Deck 1",
         [("Deck 1 forward cargo bay", "cargo crates"),
          ("Deck 1 storage bay two", "storage racks"),
          ("Deck 1 storage bay three", "storage racks"),
          ("Deck 1 EVA locker room", "suit lockers")],
         [("Deck 1 quartermaster's office", "desk"),
          ("Deck 1 storage bay four", "storage racks"),
          ("Deck 1 storage bay five", "storage racks"),
          ("Deck 1 environmental control", "console")])

    m.section("DECK 2 - Engineering")
    deck(m, C.DECK2, "Deck 2",
         [("Deck 2 reactor monitoring", "console"),
          ("Deck 2 coolant bay", "coolant tanks"),
          ("Deck 2 machine shop", "workbench"),
          ("Deck 2 parts store", "parts racks")],
         [("Deck 2 main engineering", "reactor console"),
          ("Deck 2 drive control", "console"),
          ("Deck 2 capacitor bay", "capacitor banks"),
          ("Deck 2 fuel monitoring", "console")])

    m.section("DECK 3 - Crew quarters")
    deck(m, C.DECK3, "Deck 3",
         [("Deck 3 crew berth A", "bunks"),
          ("Deck 3 crew berth B", "bunks"),
          ("Deck 3 crew berth C", "bunks"),
          ("Deck 3 crew berth D", "bunks")],
         [("Deck 3 crew berth E", "bunks"),
          ("Deck 3 crew berth F", "bunks"),
          ("Deck 3 crew head", "washbasins"),
          ("Deck 3 laundry", "laundry units")])

    m.section("DECK 4 - Mess and recreation")
    deck(m, C.DECK4, "Deck 4",
         [("Deck 4 galley", "galley range"),
          ("Deck 4 mess hall", "mess tables"),
          ("Deck 4 cold storage", "cold lockers"),
          ("Deck 4 pantry", "pantry shelves")],
         [("Deck 4 crew lounge", "lounge seating"),
          ("Deck 4 gymnasium", "exercise machines"),
          ("Deck 4 observation lounge", "lounge seating"),
          ("Deck 4 games room", "games tables")])

    m.section("DECK 5 - Medical and science")
    deck(m, C.DECK5, "Deck 5",
         [("Deck 5 medbay", "biobeds"),
          ("Deck 5 surgery", "surgical table"),
          ("Deck 5 quarantine ward", "biobeds"),
          ("Deck 5 pharmacy", "medicine racks")],
         [("Deck 5 science lab one", "lab benches"),
          ("Deck 5 science lab two", "lab benches"),
          ("Deck 5 cryo store", "cryo pods"),
          ("Deck 5 specimen store", "specimen racks")])

    m.section("DECK 6 - Officers and security")
    deck(m, C.DECK6, "Deck 6",
         [("Deck 6 first officer's cabin", "desk"),
          ("Deck 6 officers' cabin two", "bunk"),
          ("Deck 6 officers' cabin three", "bunk"),
          ("Deck 6 briefing room", "briefing table")],
         [("Deck 6 armoury", "weapon racks"),
          ("Deck 6 security office", "desk"),
          ("Deck 6 brig", "cell bunks"),
          ("Deck 6 tactical store", "equipment racks")])
    m.at_level(C.DECK6)
    m.ispawn(C.SPINE_EW + 2, C.SX2 - 3, 500, 560, 0, 0, 4500, 3,
             ["frag_grenade", "smoke_bomb", "semtex_pack", "bomb_vest", "AK47_ammo_10_50"])
    m.at_level(0)

    m.section("DECK 7 - The bridge")
    deck(m, C.DECK7, "Deck 7",
         [("Deck 7 communications room", "comms console"),
          ("Deck 7 sensor suite", "sensor console"),
          ("Deck 7 ready room", "desk"),
          ("Deck 7 wardroom", "wardroom table")],
         [("Deck 7 navigation office", "nav console"),
          ("Deck 7 captain's quarters", "desk"),
          ("Deck 7 conference room", "conference table"),
          ("Deck 7 signals office", "console")])
    # the bridge occupies the forward junction of the top deck
    m.at_level(C.DECK7)
    m.zone(C.SX1 + 1, C.SX2 - 1, C.NJ_Y1, C.NJ_Y2 - 1, 0, ROOM_TOP, "the bridge of Freya's Ascent")
    m.furniture(430, 450, C.NJ_Y2 - 8, C.NJ_Y2 - 5, 3, "the captain's chair", "metal2")
    m.furniture(360, 380, C.NJ_Y1 + 6, C.NJ_Y1 + 9, 3, "the helm console", "metal2")
    m.furniture(500, 520, C.NJ_Y1 + 6, C.NJ_Y1 + 9, 3, "the operations console", "metal2")
    m.poi(440, C.NJ_Y2 - 6, 0, "the bridge of Freya's Ascent")
    m.at_level(0)
