# World-map authoring

`rebuild_world_maps.py` is the canonical builder. Layouts are authored individually
in `world_layouts.py`; editable object presets live in
`iwserver/content/object_presets.json`. Run the builder, then
`python tools/validate_exploration_maps.py`. Generated files go under
`iwserver/content/maps/`. Keep the client and server updated together.

The design references were City of Division's main map, building guide and
furniture/object documentation, and Fireteam Requiem's map-format/design guides
and maps. The layouts are original. The useful principles are connected rooms,
rear/service routes, actual floor and wall geometry, shaped furniture, physical
stairs, and separate navigation, acoustic-space and doorway-portal layers.
No old map geometry is imported by the builder.

## Geometry and navigation

Coordinates are feet. Tile records are ordered: later records replace earlier
ones. `blank` carves air; it is not a floor. Rooms have floor, walls and roof,
and door cuts are emitted after adjoining rooms so a shared wall cannot silently
seal a doorway. Each opening has a matching zone and acoustic portal. Stairs
and slopes are successive one-unit surfaces. Bridges use elevated deck tiles
and supports rather than filling their whole bounding box with rock.

Use compact, useful outdoor districts and individually laid-out buildings.
Do not multiply a generic building template across a grid to inflate map size.
POIs are navigable destinations, not fixture-placement hints. Keep room-sized
acoustic spaces indoors; exterior navigation zones do not imply enclosure.

`spawn:x:y:z` declares a safe arrival. Each shipped map has twelve. The server
uses these instead of coordinates in code. `fixtures:authored` disables the
legacy POI-name inference. `fixture:type:x:y:z:label` places a supported service
exactly; it must have a floor, headroom and a reachable interaction position.
Use existing service types such as `atm`, `vending_machine`, `hospital_bed`,
`table` and `kiosk`, not invented names without handlers.

## Object presets

A preset contains health, bullet/blast damage multipliers, existing packed
sound paths, and normalized component boxes. Each component is
`[x1,x2,y1,y2,z1,z2,material,solid]` in a unit box. `Map.object` scales the box
to the authored dimensions and optionally turns it by a quarter turn. Use
separate backs, legs, seats and tops rather than one solid furniture cube.
Solid components win over surfaces, so keep a walkable top outside the solid
body. Put useful tops at whole-unit heights. Place objects clear of doors,
spawn points and the required circulation route.

The builder emits these shared runtime records:

```text
object:id:health:bulletMultiplier:blastMultiplier:hitSound:breakSound:label
objectpart:id:x1:x2:y1:y2:z1:z2:material:solid
```

IDs must be unique within a map, with each declaration before its parts.
Object parts use absolute fractional coordinates. The client converts them to
centre-local dynamic map elements; the server keeps matching world-space boxes.
Damage is authoritative. Material resistance and blast distance/terrain shielding
are applied on the server. Only destruction changes collision state across the
network, and late joiners receive the destroyed IDs in bounded reliable packets.
Impact sounds are limited to ten per second per object. Furniture does not
respawn or award loot during a session; a map reload or server restart restores
it. Interactive services retain their separate stock and cooldown rules.

The validator checks emitted collision, not just overlapping rectangle coverage.
Runtime tests in `tests/world_objects_regression.nvgt` additionally check
client/server geometry, damage and late-join synchronization. These checks do
not replace a multiplayer navigation and listening playtest.
