param(
    [string]$FortniteWeapons = 'C:\Users\gagel\Downloads\Fortnite Weapons',
    [string]$FortniteItems = 'C:\Users\gagel\Downloads\Fortnite Items'
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$soundDir = Join-Path $repo 'sounds'
$weaponDir = Join-Path $repo 'iwserver\content\weapons'
$ffmpeg = (Get-Command ffmpeg -ErrorAction Stop).Source
$used = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$rows = [System.Collections.Generic.List[string]]::new()

function Install-Audio([System.IO.FileInfo]$source, [string]$target, [string]$purpose) {
    if (-not $source -or -not $source.Exists) { throw "Missing source for $target" }
    if ($target.IndexOfAny([System.IO.Path]::GetInvalidFileNameChars()) -ge 0) { throw "Illegal target filename: <$target>" }
    if (-not $used.Add($source.FullName)) { throw "Source recording reused: $($source.FullName)" }
    $dest = Join-Path $soundDir $target
    if ($source.Extension -ieq '.ogg') {
        Copy-Item -LiteralPath $source.FullName -Destination $dest -Force
    } else {
        & $ffmpeg -hide_banner -loglevel error -y -i $source.FullName -vn -c:a libvorbis -q:a 5 $dest
        if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed for $($source.FullName)" }
    }
    $rows.Add("$target`t$purpose`t$($source.FullName)")
}

function Take([System.Collections.Generic.List[System.IO.FileInfo]]$pool) {
    while ($pool.Count -gt 0) {
        $f = $pool[0]; $pool.RemoveAt(0)
        if (-not $used.Contains($f.FullName)) { return $f }
    }
    throw 'An authored source pool was exhausted.'
}

$fw = Get-ChildItem -LiteralPath $FortniteWeapons -File -Recurse | Where-Object Extension -in '.ogg','.wav','.mp3'
$fi = Get-ChildItem -LiteralPath $FortniteItems -File -Recurse | Where-Object Extension -in '.ogg','.wav','.mp3'
$downloads = Split-Path -Parent $FortniteWeapons

# Every selectable mode receives its own physical/mechanical switching cue.
$modePool = [System.Collections.Generic.List[System.IO.FileInfo]]::new()
$fw | Where-Object Name -match 'Equip|Mech|Aiming - (In|Out)|ADS|Charge - (Start|End)|Overheat - (Start|End)' | Sort-Object FullName | ForEach-Object { $modePool.Add($_) }
$modeNames = @{ semi='semi-automatic'; burst='burst'; auto='full automatic'; scattershot='scattershot'; focused='focused' }
Get-ChildItem -LiteralPath $weaponDir -Filter '*.wpn' -Recurse | Sort-Object BaseName | ForEach-Object {
    $props = @{}; Get-Content -LiteralPath $_.FullName | Where-Object { $_ -match '=' } | ForEach-Object { $a=$_ -split '=',2; $props[$a[0]]=$a[1] }
    $modes = @(); if ($props.fire_modes) { $modes += $props.fire_modes -split ',' }
    if ($props.wclass -eq 'shotgun') { $modes += 'scattershot' }
    if ($props.wclass -eq 'energy') { $modes += 'focused' }
    if ($modes.Count -gt 1) { foreach ($mode in $modes) { Install-Audio (Take $modePool) "$($_.BaseName)mode_$($modeNames[$mode]).ogg" "unique $mode selector" } }
}

# Suppressed reports: three genuinely different recordings for every supported gun.
$suppressed = @('glock17','beretta92fs_pistol','desert_eagle','mp5','uzi','mp7','p90_mp','hk_g36','AK47','tar_21_assault_rifle','famas_f1_assault_rifle','m4a1_carbine','scar_h_battle_rifle','fn_fal_battle_rifle','sg08_sniper_rifle','awp_sniper_rifle','dragunov_svd')
$suppPool = [System.Collections.Generic.List[System.IO.FileInfo]]::new()
$fw | Where-Object { $_.FullName -match 'Suppress|Silenc' -and $_.Name -match 'Shoot|Fire' -and $_.Name -notmatch 'Loop|3P|Tail|Dist' } | Sort-Object FullName | ForEach-Object { $suppPool.Add($_) }
foreach ($weapon in $suppressed) { 1..3 | ForEach-Object { Install-Audio (Take $suppPool) "${weapon}supressedfire$_.ogg" 'unique suppressed report' } }

# Revoice all five energy weapons from Fortnite's science-fiction banks.
$laserPool = [System.Collections.Generic.List[System.IO.FileInfo]]::new()
$fw | Where-Object { $_.FullName -match 'Star Wars|Overwatch|Fallout|Power Rangers|Energy Rifle|Pulse Rifle|Ray Gun' -and $_.Name -match 'Shoot|Fire|Equip|Reload|Overheat' -and $_.Name -notmatch '3P|Tail|Dist|Loop' } | Sort-Object FullName | ForEach-Object { $laserPool.Add($_) }
foreach ($weapon in @('laser_pistol','laser_smg','laser_rifle','laser_sniper','laser_cannon')) {
    Install-Audio (Take $laserPool) "${weapon}draw.ogg" 'science-fiction weapon draw'
    Install-Audio (Take $laserPool) "${weapon}reload.ogg" 'science-fiction weapon reload/overheat'
    1..3 | ForEach-Object { Install-Audio (Take $laserPool) "${weapon}fire$_.ogg" 'science-fiction weapon report' }
}

# Shotgun scattershot and energy focused shots are distinct from normal fire.
$altFirePool = [System.Collections.Generic.List[System.IO.FileInfo]]::new()
$fw | Where-Object { $_.Name -match 'Shoot|Fire|Shot' -and $_.Name -notmatch 'Loop|3P|Tail|Dist|Suppress|Silenc' } | Sort-Object FullName | ForEach-Object { $altFirePool.Add($_) }
foreach ($weapon in @('benelli_m4_shotgun','ks123shotgun','spas_12_shotgun')) { 1..3 | ForEach-Object { Install-Audio (Take $altFirePool) "${weapon}scattershotfire$_.ogg" 'scattershot report' }; Install-Audio (Take $altFirePool) "${weapon}scattershotdist.ogg" 'scattershot distant report' }
foreach ($weapon in @('laser_cannon','laser_pistol','laser_rifle','laser_smg','laser_sniper')) { 1..3 | ForEach-Object { Install-Audio (Take $altFirePool) "${weapon}focusedfire$_.ogg" 'focused energy report' }; Install-Audio (Take $altFirePool) "${weapon}focuseddist.ogg" 'focused distant report' }

# Four suppressor families have different fit and removal recordings.
$attachPool = [System.Collections.Generic.List[System.IO.FileInfo]]::new()
($fi + $fw) | Where-Object Name -match 'Attach|Equip|Pickup|Pullout|Mech' | Sort-Object FullName | ForEach-Object { $attachPool.Add($_) }
foreach ($attachment in @('pistol_suppressor','smg_suppressor','rifle_suppressor','sniper_suppressor')) {
    Install-Audio (Take $attachPool) "attachment_${attachment}_attach.ogg" "$attachment installation"
    Install-Audio (Take $attachPool) "attachment_${attachment}_remove.ogg" "$attachment removal"
}

# Replace the principal UI palette with short, distinct authored interface/event sounds.
$uiPool = [System.Collections.Generic.List[System.IO.FileInfo]]::new()
$fi | Where-Object { $_.FullName -match 'sound_effects' -and $_.Name -notmatch 'Loop|Music|Preview|Ambience' -and $_.Length -lt 1500000 } | Sort-Object Length,FullName | ForEach-Object { $uiPool.Add($_) }
$uiTargets = @('menumove.ogg','menuenter.ogg','menuopen.ogg','menuclick.ogg','menuedge.ogg','chat.ogg','online.ogg','offline.ogg','notify.ogg','pm.ogg','newmotd.ogg','welcome.ogg','killalert.ogg','pingstart.ogg','pingstop.ogg','bufferswitch.ogg','buffermove.ogg','invmove.ogg','inv1.ogg','ban.ogg','dc.ogg','admin.ogg','dev.ogg')
foreach ($target in $uiTargets) { Install-Audio (Take $uiPool) $target 'replacement interface cue' }

# Consumables, equipment, and HyperComp actions now have concrete cues.
$items = @('health_potion','ultra_health_potion','bomb_vest','energetic_potion_red','energetic_potion_blue','energetic_potion_green','energetic_potion_rainbow','translocator','translocator_cell','adrenaline_syringe','nanomatic_multitool','nanomatic_components','biomonitor_bracelet','wirenet','c4','hypercomp')
foreach ($item in $items) { Install-Audio (Take $uiPool) "${item}use.ogg" "$item use" }
foreach ($item in @('bomb_vest','biomonitor_bracelet','wirenet')) { Install-Audio (Take $attachPool) "${item}equip.ogg" "$item equip"; Install-Audio (Take $attachPool) "${item}unequip.ogg" "$item unequip" }
foreach ($name in @('open','status','monitor','c4','alarm')) { Install-Audio (Take $uiPool) "hypercomp_$name.ogg" "HyperComp $name" }

# Dedicated continuous-weapon recordings found elsewhere in the local extracted libraries.
$continuous = Get-ChildItem -LiteralPath $downloads -File -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Extension -match '^\.(ogg|wav|mp3)$' -and $_.FullName -notlike "$repo*" }
$flamePool = [System.Collections.Generic.List[System.IO.FileInfo]]::new()
$continuous | Where-Object { $_.Name -match 'flame.?thrower.*fire' } | Sort-Object FullName | ForEach-Object { $flamePool.Add($_) }
1..3 | ForEach-Object { Install-Audio (Take $flamePool) "flamethrowerfire$_.ogg" 'flamethrower stream/action' }
$sawPool = [System.Collections.Generic.List[System.IO.FileInfo]]::new()
$continuous | Where-Object { $_.Name -match 'chainsaw.*(fire|loop|hit)' } | Sort-Object FullName | ForEach-Object { $sawPool.Add($_) }
1..3 | ForEach-Object { Install-Audio (Take $sawPool) "chainsawfire$_.ogg" 'chainsaw motor/cutting action' }

$manifest = Join-Path $soundDir 'AUTHORED_AUDIO_SOURCES.tsv'
@("target`tpurpose`tsource") + $rows | Set-Content -LiteralPath $manifest -Encoding utf8
Write-Host "Imported $($rows.Count) distinct authored recordings. Manifest: $manifest"
