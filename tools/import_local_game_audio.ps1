param([string]$Ffmpeg = "ffmpeg")
$ErrorActionPreference = "Stop"
$project = Split-Path -Parent $PSScriptRoot
$sounds = Join-Path $project "sounds"
$temp = Join-Path $PSScriptRoot "audio_import_temp"
$insZip = 'D:\insurgency_sandstorm_soundfiles_(main+1.12-1.13)\sandstorm_weapons.zip'
$bfZip = 'D:\battlefield2042\2042_20260213\2042\Common\Sound\Vehicles.zip'
if (-not (Test-Path -LiteralPath $insZip)) { throw "Insurgency weapon archive not found" }
if (-not (Test-Path -LiteralPath $bfZip)) { throw "Battlefield vehicle archive not found" }
New-Item -ItemType Directory -Path $temp -Force | Out-Null

$weaponMap = [ordered]@{
    '120mm_mortar'='Weapon_M79'; 'AK47'='Weapon_AKM'; 'awp_sniper_rifle'='Weapon_L96A1'
    'benelli_m4_shotgun'='Weapon_KSG'; 'beretta92fs_pistol'='Weapon_M9'; 'crossbow'='Weapon_Welrod'
    'desert_eagle'='Weapon_Deagle'; 'dragunov_svd'='Weapon_SVD'; 'famas_f1_assault_rifle'='Weapon_FAMAS'
    'fn_fal_battle_rifle'='Weapon_FnFal'; 'glock17'='Weapon_PF940'; 'hayvork'='Weapon_M1911'
    'hk_g36'='Weapon_G36K'; 'ks123shotgun'='Weapon_KS23'; 'm1garantBattleRifle'='Weapon_M1Garand'
    'm249_saw'='Weapon_M249'; 'm4a1_carbine'='Weapon_M4a1'; 'magnum_revolver'='Weapon_MR73'
    'mp5'='Weapon_MP5'; 'mp7'='Weapon_MP7'; 'p90_mp'='Weapon_P90'; 'rpk_lmg'='Weapon_RPK'
    'scar_h_battle_rifle'='Weapon_Mk17'; 'sg08_sniper_rifle'='Weapon_M24'
    'spas_12_shotgun'='Weapon_Model870'; 'tar_21_assault_rifle'='Weapon_Tavor'
    'taurus_model66_revolver'='Weapon_MR73'; 'uzi'='Weapon_UZI'
}

$manifest = New-Object System.Collections.Generic.List[string]
$manifest.Add('Infinite Warfare local personal-use audio import manifest')
$manifest.Add('Imported without synthesis or procedural variation; WAV sources were format-converted to OGG only.')
$manifest.Add('')
$insEntries = tar -tf $insZip

function Expand-One([string]$zip, [string]$entry) {
    & tar -xf $zip -C $temp $entry
    if ($LASTEXITCODE -ne 0) { throw "Could not extract $entry" }
    return Join-Path $temp ($entry.Replace('/','\'))
}
function Convert-One([string]$source, [string]$targetName) {
    $target = Join-Path $sounds $targetName
    & $Ffmpeg -nostdin -hide_banner -loglevel error -y -i $source -vn -c:a libvorbis -q:a 5 $target
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $target)) { throw "Could not convert $targetName" }
}

foreach ($iw in $weaponMap.Keys) {
    $sourceWeapon = $weaponMap[$iw]
    $base = "output/$sourceWeapon"
    $drawEntry = "$base/draw.wav"
    $fireEntry = "$base/fire.wav"
    $reloadEntry = "$base/reload.wav"
    if ($insEntries -notcontains $drawEntry) { $drawEntry = $insEntries | Where-Object { $_ -like "$base/handling/*.wav" } | Select-Object -First 1 }
    if ($insEntries -notcontains $reloadEntry) { $reloadEntry = $insEntries | Where-Object { $_ -like "$base/handling/*.wav" } | Select-Object -Last 1 }
    if ($insEntries -notcontains $fireEntry) { throw "No fire sound found for $sourceWeapon" }
    if (-not $drawEntry -or -not $reloadEntry) { throw "No handling fallback found for $sourceWeapon" }
    $draw = Expand-One $insZip $drawEntry
    $fire = Expand-One $insZip $fireEntry
    $reload = Expand-One $insZip $reloadEntry
    Convert-One $draw "${iw}draw.ogg"
    1..3 | ForEach-Object { Convert-One $fire "${iw}fire$_.ogg" }
    Convert-One $reload "${iw}reload.ogg"
    $suppressedEntry = "$base/fire_suppressed.wav"
    if ($insEntries -contains $suppressedEntry) {
        $suppressed = Expand-One $insZip $suppressedEntry
        1..3 | ForEach-Object { Convert-One $suppressed "${iw}supressedfire$_.ogg" }
    }
    $manifest.Add("WEAPON $iw <= Insurgency Sandstorm $sourceWeapon (draw, fire, reload$(if($insEntries -contains $suppressedEntry){', suppressed fire'}else{''}))")
}

$bfEntries = tar -tf $bfZip
$vehicleMap = [ordered]@{
    'jeep'='WillysJeep'; 'humvee'='M1114'; 'pickup'='PickupTruck'; 'apc'='M3A3Bradley'
    'buggy'='VDVBuggy'; 'sedan'='TukTuk'; 'tank'='M1Abrams'; 'van'='GAZ-Vodnik'
}
foreach ($iw in $vehicleMap.Keys) {
    $sourceVehicle = $vehicleMap[$iw]
    $prefix = "Vehicles/$sourceVehicle/"
    $candidates = $bfEntries | Where-Object { $_.StartsWith($prefix) -and $_.EndsWith('.wav') }
    $idleEntry = $candidates | Where-Object { $_ -match 'Engine-Idle|Idle_Loop|Engine-Low_Loop|Interior_Loop' } | Select-Object -First 1
    $startEntry = $candidates | Where-Object { $_ -match 'Ignition|Startup' } | Select-Object -First 1
    if (-not $idleEntry) { $idleEntry = $candidates | Where-Object { $_ -match 'Engine|Interior|Movement' } | Select-Object -First 1 }
    if (-not $idleEntry) { $idleEntry = $candidates | Select-Object -First 1 }
    if (-not $idleEntry) { throw "No Battlefield vehicle audio found for $sourceVehicle" }
    if (-not $startEntry) { $startEntry = $idleEntry }
    Convert-One (Expand-One $bfZip $idleEntry) "vehicle_${iw}_engine.ogg"
    Convert-One (Expand-One $bfZip $startEntry) "vehicle_${iw}_start.ogg"
    $manifest.Add("VEHICLE $iw <= Battlefield 2042 $sourceVehicle (engine, start)")
}

$doorOpenEntry = $bfEntries | Where-Object { $_ -match '^Vehicles/Condor/.*RearHatchDoorOpen-Stop.*\.wav$' } | Select-Object -First 1
$doorCloseEntry = $bfEntries | Where-Object { $_ -match '^Vehicles/Condor/.*RearHatchDoorClose-Stop.*\.wav$' } | Select-Object -First 1
if ($doorOpenEntry -and $doorCloseEntry) {
    Convert-One (Expand-One $bfZip $doorOpenEntry) 'vehicle_door_open.ogg'
    Convert-One (Expand-One $bfZip $doorCloseEntry) 'vehicle_door_close.ogg'
    $manifest.Add('VEHICLE shared doors <= Battlefield 2042 Condor rear hatch')
}

$manifest.Add('')
$manifest.Add('Fortnite: no Fortnite-named local archive or directory was found on D: during this import.')
$manifest | Set-Content -LiteralPath (Join-Path $sounds 'LOCAL_GAME_AUDIO_SOURCES.txt') -Encoding UTF8
Write-Output "Imported $($weaponMap.Count) weapon mappings and $($vehicleMap.Count) vehicle mappings."
