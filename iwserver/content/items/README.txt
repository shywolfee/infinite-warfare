Item definitions

Every item that is not a weapon is defined here, one file per item, in a
folder named for its category. The file name (without .item) is the item's
id. The client and the server both read these files at startup, so a change
here changes the item everywhere; nothing about an item is worked out from
the words in its id.

Each line is key=value. Lines starting with # are comments.

Every item
  name          what players hear it called
  category      Ammo, Armour, Armour Repair, Containers, Electronics,
                Equipment, Explosives, Healing, Team, Tools, Utility,
                Vehicle Supplies or Weapon Maintenance
  summary       one sentence for help and the Armoury
  give_amount   how many one grant or pickup gives

Armour
  armour_slot        head, torso, arm or leg; an item is armour only if this is set
  armour_rating      percent of each hit to that body region it stops
  armour_durability  how much damage it can absorb before it is spent
  armour_weight      equipment weight

Armour repair
  repairs       comma-separated ids of the armour this patch fits; it is
                applied to the most worn fitting piece you are wearing

Medication
  medication_form      liquid, pills or loose_pill
  capacity             fluid ounces or pills in a full container
  recommended_dose     ounces or pills in a normal dose
  loose_pill           for a pill bottle, the id of one of its loose pills
  dose_heal            health restored at once per ounce or pill
  dose_heal_over_time  further health per ounce or pill, spread over heal_seconds
  heal_seconds         how long that further healing takes
  dose_toxicity        percent toxicity added per ounce or pill
  stops_bleeding       true if it stops bleeding
  dose_stamina         stamina restored per ounce or pill
  dose_detox           percent toxicity removed per ounce or pill

Explosives
  thrown        true for grenades and other thrown explosives, whose fuse can be cooked
  launched      true for guided missiles and other fired munitions
  fuse_ms       milliseconds from throwing or firing to detonation
  blast_radius  tiles
  blast_damage  damage at the centre of the blast
  launch_speed  tiles a second, for launched and specially thrown ones
  launch_rise   upward speed at release

Any other key is kept and can be read by the game with item_prop().
Weapons are defined separately, in content/weapons.
