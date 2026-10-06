Dynamic object types

Each file here describes one kind of object a map can place (see
includes/dynamic_objects_core.nvgt). The file name, without .object, is the
type's id. Lines are key=value; unknown keys are ignored.

Description
  name, description, category

Shape (tiles; about a metre each). Without part= lines the object is one box
of length (east-west) by width (north-south) by height, standing on its
position.
  length, width, height, material (the tile it presents: wallmetal,
  wallwood, tree, ...), solid (true/false)
  part=x1,x2,y1,y2,z1,z2,material,solid   relative to the centre, repeatable

Damage
  health        0 means it cannot be destroyed
  bullet_factor, blast_factor   how much of a hit it takes
  debris        type it turns into when destroyed (empty: it disappears)
  respawn_ms    how long until it is put back (0: never)
  burn_ms       burns this long after being wrecked, then explodes
  explode_damage, explode_radius, explode_fragments, explode_payload,
  explode_cloud_ms, explode_cloud_radius, explode_sound, explode_distant
                an explosion when it is destroyed (or after burning)
  loot_on_destroy=true   drops its stock or loot when destroyed

Sounds, from the sound pack's executioners_rage/<sound>/ folder
  sound, impact_sounds (how many impactN files), contact_sound, destroy_sound

Use (interaction)
  atm       pay credit chips into your account
  vend      buy offer= items (offer=item:price:product sound)
  store     open the online store
  bed       heal (heal, heal_ceiling)
  dispense  hand out one item= from stock
  search    find one of loot= from stock
  report    friendly and hostile counts on the map
  team      the team directory
  light, toggle   switch on and off
  hydrate   restore stamina=
  charge    charge a HyperComp at charge_rate percent a second
  door      open and close
  flush, info   a description
  stock, restock_ms, cooldown_ms   how often, and how much
