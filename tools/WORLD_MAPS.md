# Authoring the world maps

`tools/build_maps.py` builds every map; `tools/validate_maps.py` checks the
result. Edit the layout modules under `tools/mapgen/`, never the `.map` files,
because the next build overwrites them.

```
tools/mapgen/builder.py    the primitives: street, junction, room, door, stair,
                           ladder, bridge, deck, plateau, ambience, lift
tools/mapgen/palette.py    every surface a map may name, and the recording it
                           plays; every acoustic kind; every ambience bed;
                           every destructible preset and interactive service
tools/mapgen/ghost_town.py       Ghost Town
tools/mapgen/shattersea.py       Shattersea
tools/mapgen/freyas_ascent.py    Freya's Ascent
tools/mapgen/coruscant.py        Coruscant
```

## What the primitives are for

Nobody writes ten thousand colon-separated rectangles by hand and keeps them
consistent. The primitives exist so that the rules which get forgotten on the
fortieth room of a map cannot be forgotten at all:

* `room()` writes a floor, four walls, a roof, a named interior zone **and** an
  acoustic space. A room with no acoustic space sounds like open ground.
* `door()` writes the hole in the wall, the portal sound travels through **and**
  a zone of its own. All three or none: a portal with no hole is a wall you can
  hear through, and a hole with no portal is a door you cannot find by ear.
  Doors are deferred to the end of the build so a wall written after the room
  cannot silently seal one.
* `window()` writes a portal with no hole, and marks it so the checker knows
  not to expect one.
* `street()` writes the carriageway, both pavements and a kerb zone on each
  side, named by the stretch you are standing on. Stepping off a kerb is
  exactly the sort of thing you cannot see.
* `junction()` exists because walking out of one street into another with
  nothing in between means the moment where you could have turned passes
  unannounced.
* `stair()` is a stack of one-unit treads, which is what makes it something you
  walk up rather than something you operate. It carves its own headroom,
  because a stair cut into a hillside is a hole through solid ground.
* `ladder()` lays a climbable column. Any material whose name contains ladder,
  rungs, netting, scaffold or climb is a climb: the automatic one-unit step
  refuses to take it sideways and the up and down keys work on it.
* `bridge()` has a deck, rails and piers, so you can walk under it.
* `deck()` is a floor in the air held up by whatever is already there.
  `plateau()` fills everything beneath it, which is right for a headland and
  catastrophic for a gallery round a lighthouse. `plateau(base=)` matters on a
  map with levels underneath.
* `quarters()` writes bearings onto a large open area, because a four-hundred
  square island with one zone on it tells you which island and nothing else.

## Surfaces

A map names its surfaces in English and the palette says what each one sounds
like. Adding a surface is a change in one place: `palette.py`. The builder
refuses a material that is not in the palette, and emits a `surface:` line for
every material the map actually uses, so the client never guesses.

Anything with `wall` in the name is something you walk into rather than onto.
Both halves of the game test for that exact word.

## Placement

Landmarks, services, loot and spawns are not placed by eye. `finish()`
rasterizes the completed map exactly as the game reads it, floods it from a
spawn point — taking one-unit steps, climbing climbable columns and riding
lifts — and settles each one on a square that is both standable and genuinely
connected. Anything that cannot be settled fails the build by name. Loot is
scattered as separate single-square spawns through a rectangle rather than
heaped on one tile.

## Checking

`validate_maps.py` rasterizes the emitted file in declaration order, which is
the only way to catch a doorway sealed by a later wall, a stair with a two-unit
riser in it, a spawn inside a building, an island nobody can reach, or a patch
of floor with no zone on it. Rectangle-union coverage passes all of those. It
also checks that every material has a surface line, every ambience bed and
object sound exists in the pack, every loot item is registered, and every
service type has a sound directory.

None of it replaces walking the map with the sound on.
