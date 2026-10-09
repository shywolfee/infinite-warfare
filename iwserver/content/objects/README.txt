# Dynamic object types

Each `.object` file describes one kind of object a map can place. Its filename
without the extension is its type ID. Lines are `key=value`; unknown keys are
ignored. Parsing and geometry live in `includes/dynamic_objects_core.nvgt`.

## Description

- `name`: the spoken object name.
- `description`: its player-facing description.
- `category`: the content category.

## Shape

Dimensions use tiles, about a metre each. Without `part=` lines the object is
one box of length (east-west), width (north-south) and height, standing on its
position.

- `length`, `width`, `height`: box dimensions.
- `material`: the tile it presents, such as `wallmetal`, `wallwood` or `tree`.
- `solid`: `true` or `false`.
- `part=x1,x2,y1,y2,z1,z2,material,solid`: a component relative to the centre;
  repeat this field for several components.

## Damage and destruction

- `health`: zero means the object cannot be destroyed.
- `bullet_factor`, `blast_factor`: how much of a hit it takes.
- `debris`: the type it becomes when destroyed; empty means it disappears.
- `respawn_ms`: how long until it is replaced; zero means never.
- `burn_ms`: how long it burns after being wrecked, before exploding.
- `explode_damage`, `explode_radius`, `explode_fragments`, `explode_payload`,
  `explode_cloud_ms`, `explode_cloud_radius`, `explode_sound`,
  `explode_distant`: the explosion when destroyed or after burning.
- `loot_on_destroy=true`: drop its stock or loot when destroyed.

## Fixture services

The content editor exposes these files under Fixtures and world-object
services. Reloading fixtures synchronizes their definitions to clients.

- `interaction=medical` uses `service=coagulate`, `ventilate` or `resuscitate`.
- `heal` sets resuscitation health; `stamina` sets breathing-treatment recovery.
- `stock`, `restock_ms` and `cooldown_ms` govern consumable service supplies.
- `interaction=news` opens announcements; `voice` opens voice rooms.
- `interaction=report` surveys detectable nearby movement, not the whole map.
- `interaction=atm` opens shared banking; `store` opens the marketplace.
- `interaction=vend` uses authored offers and physical-currency payment choices.

Dumpster deposits are a server-owned salvage dictionary on each object, not
generated stock. Searches consume real deposited entries before random loot.
Geometry/content reloads preserve those entries by object ID and origin type;
server restarts do not persist them.

## Sounds

Sounds come from the sound pack's `executioners_rage/<sound>/` folder.

- `sound`: the sound folder.
- `impact_sounds`: the number of `impactN` files.
- `contact_sound`, `destroy_sound`: contact and destruction sounds.

## Use and interaction

Set `use` to the interaction the object supports:

- `atm`: pay credit chips into the player's account.
- `vend`: buy `offer=` items; each offer is `item:price:product sound`.
- `store`: open the online store.
- `bed`: heal using `heal` and `heal_ceiling`.
- `dispense`: hand out one `item=` from stock.
- `search`: find one `loot=` item from stock.
- `report`: report friendly and hostile counts on the map.
- `team`: open the team directory.
- `light`, `toggle`: switch on and off.
- `hydrate`: restore `stamina=`.
- `charge`: charge a HyperComp at `charge_rate` percent a second.
- `door`: open and close.
- `flush`, `info`: describe the interaction.

`stock`, `restock_ms` and `cooldown_ms` define how much is available and how
often the interaction can be used.
