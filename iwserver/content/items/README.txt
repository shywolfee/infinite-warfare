# Item definitions

Every item that is not a weapon is defined here, one file per item, in a
folder named for its category. The file name (without .item) is the item's
id. The client and the server both read these files at startup, so a change
here changes the item everywhere; nothing about an item is worked out from
the words in its id.

Each line is key=value. Lines starting with # are comments.

## Every item

- `name`: what players hear it called
- `category`: Ammo, Armour, Armour Repair, Containers, Electronics,
  Equipment, Explosives, Healing, Team, Tools, Utility or Vehicle Supplies.
- `summary`: one sentence for help and the Armoury
- `give_amount`: how many one grant or pickup gives

## Physical currency and discarded containers

- `currency_kind`: chip, stored, bank, credit or empty.
- `currency_value`: the credit value of a chip or new stored-value stick.
- `currency_capacity`: maximum stored balance or shared account credit limit.
- `currency_fee_percent`: payment or refill surcharge, rounded up to credits.
- `currency_refillable`: whether the stick can be reloaded through banking.
- `card_issue_price`: checking-account price for issuing a payment device.
- `disposable`: whether a carried item may be placed in dumpster salvage.
- `empty_container`: item left after fully consuming a bottle or provision.
- `economy_drop_weight`: relative chance in the periodic physical-supply drop.
- `market_excluded`: refuse sale of this item through supply offers.

Stored-value inventory IDs retain their balance as `base__value__N`. The
shared item reader resolves the base definition and rejects invalid balances;
the server issues the replacement item after payment. Do not author a separate
item file for each remaining balance.

## Purpose-built devices and supply offers

- `device_profile`: identifies hardware with a dedicated device launcher.
- `device_actions`: comma-separated native server tools: bank, market, c4,
  bunkers, navigation, weather, scanner or medical.
- `device_extensible`: permits compatible downloadable modules.
- `device_storage`: base module capacity in GB.
- `device_scan_range`: contact receiver range in tiles.

Memory items use `use_kind=terminal_storage` and `storage_gb`; they expand
the tablet or handset selected by the player, not the tactical HyperComp.
Module definitions in content/device_modules have name, devices, handler,
feature, size and price. Only scanner, ballistics and vehicle_diagnostics
are optional module handlers. Devices is a comma-separated hardware-id list.

Supply offers in content/marketplace/category/id.offer define name, category,
summary, item, quantity, price, max_order and enabled. Quantity is inventory
units per pack; max_order is packs per cart. Currency and market-excluded
items cannot be sold. Reload the appropriate content type after editing.

## Armour

- `armour_slot`: head, torso, arm or leg; an item is armour only if this is set
- `armour_rating`: percent of each hit to that body region it stops
- `armour_durability`: how much damage it can absorb before it is spent
- `armour_weight`: equipment weight

## Armour repair

- `repairs`: comma-separated ids of the armour this patch fits; it is
  applied to the most worn fitting piece you are wearing.

## Medication

- `medication_form`: liquid, pills or loose_pill
- `capacity`: fluid ounces or pills in a full container
- `recommended_dose`: ounces or pills in a normal dose
- `loose_pill`: for a pill bottle, the id of one of its loose pills
- `dose_heal`: health restored at once per ounce or pill
- `dose_heal_over_time`: further health per ounce or pill, spread over heal_seconds
- `heal_seconds`: how long that further healing takes
- `dose_toxicity`: percent toxicity added per ounce or pill
- `stops_bleeding`: true if it stops bleeding
- `dose_stamina`: stamina restored per ounce or pill
- `dose_detox`: percent toxicity removed per ounce or pill

## Explosives

- `thrown`: true for grenades and other thrown explosives, whose fuse can be cooked
- `launched`: true for guided missiles and other fired munitions
- `fuse_ms`: milliseconds from pulling a thrown grenade's pin, or firing a launched munition, to detonation
- `blast_radius`: tiles
- `blast_damage`: damage at the centre of the blast
- `launch_speed`: tiles a second, for launched and specially thrown ones
- `launch_rise`: upward speed at release
- `sticky`: true if a thrown charge sticks to the first person or
surface it touches
- `vehicle_only`: true if a mine is set off only by vehicles, not people on foot

Audio properties are editable in the content editor. `pin_sound` plays at
preparation; `throw_sound` plays only at release. `bounce_sound` and
`landing_sound` are separate collision cues. `flight_loop` is a short,
quiet, loopable positional recording, not a detonation or launch sound.
`explosion_sound` is the close detonation; `distant_sound` is its distant
report. Placed charges also have `place_sound`. Author these explicitly:
an absent property otherwise builds a filename from `sound_prefix` or the
item ID, which must actually exist in the sound pack.

For these explosive properties, filenames are relative to `sounds/`; short
names use `.ogg` implicitly, while `flight_loop` and `distant_sound` include
their extension. `companion_sound` is a folder below
`sounds/executioners_rage/`, containing `activate.wav`, `fly.wav` and
`impact1.wav` through `impact3.wav` for a drone.

Any other key is kept and can be read by the game with item_prop().
Momentum explosives use `momentum_rolling=true`: range is controlled by
`rolling_range_min` and `rolling_range_max` (tiles of travelled path),
`rolling_acceleration` (tiles/second squared), `rolling_max_speed`,
`rolling_landing_retention` (fraction of horizontal speed retained), and
`rolling_distance_damage_bonus` / `rolling_speed_damage_bonus` (additional
damage multipliers at full range / maximum speed). Their ordinary grenade
fuse is disabled; contacts and range exhaustion trigger detonation.
Companion acquisition and weapon reach are separate: `companion_attack_range`
selects targets, while `companion_weapon_range` controls actual firing reach.
Health, speed, follow distance, damage and attack cooldown keep their existing
`companion_*` properties. They are all editable in the content editor.
Weapons are defined separately, in content/weapons.
