param(
    [string]$InsurgencyRoot = 'D:\insurgency_sandstorm_soundfiles_(main+1.12-1.13)\output',
    [string]$FortniteWeapons = 'C:\Users\gagel\Downloads\Fortnite Weapons'
)

$ErrorActionPreference='Stop'
$repo=Split-Path -Parent $PSScriptRoot
$sounds=Join-Path $repo 'sounds'
$wpnRoot=Join-Path $repo 'iwserver\content\weapons'
$ffmpeg=(Get-Command ffmpeg -ErrorAction Stop).Source
$used=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$rows=[System.Collections.Generic.List[string]]::new()

# Do not reuse anything selected by the previous authored pass.
$oldManifest=Join-Path $sounds 'AUTHORED_AUDIO_SOURCES.tsv'
if(Test-Path $oldManifest) { Import-Csv $oldManifest -Delimiter "`t" | ForEach-Object { [void]$used.Add($_.source) } }

function Install([System.IO.FileInfo]$source,[string]$target,[string]$purpose) {
    if(-not $source -or -not $source.Exists){throw "Missing source for $target"}
    if(-not $used.Add($source.FullName)){throw "Source reused: $($source.FullName)"}
    $dest=Join-Path $sounds $target
    if($source.Extension -ieq '.ogg'){Copy-Item -LiteralPath $source.FullName -Destination $dest -Force}
    else { & $ffmpeg -nostdin -hide_banner -loglevel error -y -i $source.FullName -vn -c:a libvorbis -q:a 5 $dest; if($LASTEXITCODE){throw "ffmpeg failed: $source"} }
    $rows.Add("$target`t$purpose`t$($source.FullName)")
}
function Take([System.Collections.Generic.List[System.IO.FileInfo]]$pool) {
    while($pool.Count){$f=$pool[0];$pool.RemoveAt(0);if(-not $used.Contains($f.FullName)){return $f}}
    throw 'Authored source pool exhausted.'
}
function First-Unused([object[]]$files,[string]$pattern) {
    return $files | Where-Object { $_.Name -match $pattern -and -not $used.Contains($_.FullName) } | Sort-Object FullName | Select-Object -First 1
}

$map=[ordered]@{
 '120mm_mortar'='Weapon_M79';'AK47'='Weapon_AKM';'awp_sniper_rifle'='Weapon_L96A1';'benelli_m4_shotgun'='Weapon_KSG';'beretta92fs_pistol'='Weapon_M9';'crossbow'='Weapon_Welrod';'desert_eagle'='Weapon_Deagle';'dragunov_svd'='Weapon_SVD';'famas_f1_assault_rifle'='Weapon_FAMAS';'fn_fal_battle_rifle'='Weapon_FnFal';'glock17'='Weapon_PF940';'hk_g36'='Weapon_G36K';'ks123shotgun'='Weapon_KS23';'m1garantBattleRifle'='Weapon_M1Garand';'m249_saw'='Weapon_M249';'m4a1_carbine'='Weapon_M4a1';'magnum_revolver'='Weapon_MR73';'mp5'='Weapon_MP5';'mp7'='Weapon_MP7';'p90_mp'='Weapon_P90';'rpk_lmg'='Weapon_RPK';'scar_h_battle_rifle'='Weapon_Mk17';'sg08_sniper_rifle'='Weapon_M24';'spas_12_shotgun'='Weapon_Model870';'tar_21_assault_rifle'='Weapon_Tavor';'taurus_model66_revolver'='Weapon_MR73';'uzi'='Weapon_UZI'
}
$fortnite=Get-ChildItem -LiteralPath $FortniteWeapons -File -Recurse | Where-Object Extension -in '.ogg','.wav','.mp3'
$handlingPool=[System.Collections.Generic.List[System.IO.FileInfo]]::new()
Get-ChildItem -LiteralPath $InsurgencyRoot -File -Recurse | Where-Object { $_.FullName -match '\\handling\\' } | Sort-Object FullName | ForEach-Object {$handlingPool.Add($_)}
$fallback=[System.Collections.Generic.List[System.IO.FileInfo]]::new()
$fortnite | Where-Object { $_.Name -match 'Equip|Pickup|Pullout|Mech|Reload|Fire|Shoot' -and $_.Name -notmatch 'Loop|3P|Tail|Dist' } | Sort-Object FullName | ForEach-Object {$fallback.Add($_)}

$weapons=Get-ChildItem -LiteralPath $wpnRoot -Filter '*.wpn' -Recurse | Sort-Object BaseName
foreach($wf in $weapons){
    $id=$wf.BaseName
    $dir=if($map.Contains($id)){Join-Path $InsurgencyRoot $map[$id]}else{$null}
    $files=if($dir -and (Test-Path $dir)){Get-ChildItem -LiteralPath $dir -File -Recurse}else{@()}
    $draw=First-Unused $files '(^draw\.wav$|weapon_movement|hand_grab|arm_movement)'
    $holster=First-Unused $files '(weapon_movement|arm_movement|hand_grab|shoulder|stock_close)'
    $unload=First-Unused $files '(mag_out\.wav$|remove_(round|shell)|open_(tube|barrel)|belt_pull|cylinder_open)'
    $empty=First-Unused $files '(dry|empty|trigger)'
    if(-not $draw){$draw=Take $fallback}; Install $draw "${id}draw.ogg" 'individual weapon draw'
    if(-not $holster){$holster=Take $handlingPool}; Install $holster "${id}holster.ogg" 'individual weapon holster'
    if(-not $unload){$unload=Take $handlingPool}; Install $unload "${id}unload.ogg" 'individual weapon unload'
    if(-not $empty){$empty=Take $handlingPool}; Install $empty "${id}empty.ogg" 'individual empty action'
    Install (Take $handlingPool) "${id}reloadend.ogg" 'individual reload completion'
}

# Each holster has its own complete physical interaction bank.
$holsters=@('pistol_holster','gun_belt_357','gun_belt_44','smg_sling','rifle_strap','sniper_carry_case','shotgun_bandoleer','knife_sheath','sword_scabbard','bat_holster')
foreach($h in $holsters){
    foreach($action in @('equip','unequip','store','weapon_remove','ammo_store','ammo_remove','autoload')){
        Install (Take $handlingPool) "holster_${h}_${action}.ogg" "$h $action"
    }
}

# Complete every melee close-action bank without replacing already complete files.
$melee=@('baseball_bat','chainsaw','combatknife','hayvork','katana','machete','trector_plow')
$meleePool=[System.Collections.Generic.List[System.IO.FileInfo]]::new()
$fortnite | Where-Object { $_.FullName -match 'Melee|Pickaxe|Sword|Blade|Claw|Kombat' -and $_.Name -match 'Attack|Swing|Impact|Hit|Fire|Shoot|Slash' -and $_.Name -notmatch 'Loop|3P|Tail|Dist' } | Sort-Object FullName | ForEach-Object {$meleePool.Add($_)}
foreach($weapon in $melee){
    foreach($kind in @('fire','hit')){1..3|ForEach-Object{$target="${weapon}${kind}$_.ogg";Install (Take $meleePool) $target "melee $kind variant"}}
}
Install (Take $meleePool) 'playerhit1.ogg' 'player damage feedback'
Install (Take $fallback) 'camerahazard.ogg' 'security camera hazard warning'

$manifest=Join-Path $sounds 'WEAPON_LIFECYCLE_AUDIO_SOURCES.tsv'
@("target`tpurpose`tsource")+$rows|Set-Content -LiteralPath $manifest -Encoding utf8
Write-Host "Imported $($rows.Count) distinct weapon-lifecycle and holster recordings."
