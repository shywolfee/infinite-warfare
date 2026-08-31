param(
 [string]$VehicleZip='D:\battlefield2042\2042_20260213\2042\Common\Sound\Vehicles.zip',
 [string]$InsurgencyRoot='D:\insurgency_sandstorm_soundfiles_(main+1.12-1.13)\output',
 [string]$FortniteItems='C:\Users\gagel\Downloads\Fortnite Items'
)
$ErrorActionPreference='Stop'
$repo=Split-Path -Parent $PSScriptRoot;$sounds=Join-Path $repo 'sounds';$ffmpeg=(Get-Command ffmpeg).Source
$temp=Join-Path $PSScriptRoot 'vehicle_reload_temp';New-Item -ItemType Directory -Force -Path $temp|Out-Null
$used=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase);$rows=[System.Collections.Generic.List[string]]::new()
foreach($mf in @('AUTHORED_AUDIO_SOURCES.tsv','WEAPON_LIFECYCLE_AUDIO_SOURCES.tsv')){$p=Join-Path $sounds $mf;if(Test-Path $p){Import-Csv $p -Delimiter "`t"|%{[void]$used.Add($_.source)}}}
function Convert([string]$src,[string]$target,[string]$purpose,[string]$sourceLabel){
 if(-not $used.Add($sourceLabel)){throw "Source reused: $sourceLabel"};$dst=Join-Path $sounds $target
 if([IO.Path]::GetExtension($src) -ieq '.ogg'){Copy-Item -LiteralPath $src -Destination $dst -Force}else{& $ffmpeg -nostdin -hide_banner -loglevel error -y -i $src -vn -c:a libvorbis -q:a 5 $dst;if($LASTEXITCODE){throw "Conversion failed: $src"}}
 $rows.Add("$target`t$purpose`t$sourceLabel")
}
function TakeFile([System.Collections.Generic.List[System.IO.FileInfo]]$pool){while($pool.Count){$f=$pool[0];$pool.RemoveAt(0);if(-not $used.Contains($f.FullName)){return $f}};throw 'Source pool exhausted'}

$entries=& tar -tf $VehicleZip
$allVehicleEntries=@($entries|?{$_.StartsWith('Vehicles/')-and $_.EndsWith('.wav')})
$vehicleMap=[ordered]@{jeep='WillysJeep';humvee='M1114';pickup='PickupTruck';apc='M3A3Bradley';buggy='VDVBuggy';sedan='TukTuk';tank='M1Abrams';van='GAZ-Vodnik'}
$actionPatterns=[ordered]@{door_open='DoorOpen|Hatch.*Open|Open.*Door';door_close='DoorClose|Hatch.*Close|Close.*Door';enter='Enter|Mount|GetIn|Interior';exit='Exit|Dismount|GetOut';seat_switch='Seat|Movement|Suspension|Gear';window_open='Window.*Open|Hatch.*Open|DoorOpen';window_close='Window.*Close|Hatch.*Close|DoorClose';accelerate='Accel|Throttle|Rev|Engine-High';decelerate='Decel|Engine-Low|Brake';stop='Shutdown|Engine-Stop|Stop';turn='Turn|Steer|Suspension';crash='Impact|Collision|Damage';destroy='Destroy|Explosion|Critical'}
$zipUsed=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach($vid in $vehicleMap.Keys){
 $prefix="Vehicles/$($vehicleMap[$vid])/";$candidates=@($entries|?{$_.StartsWith($prefix)-and $_.EndsWith('.wav')})
 foreach($action in $actionPatterns.Keys){
  $entry=$candidates|?{-not $zipUsed.Contains($_)-and $_ -match $actionPatterns[$action]}|Select-Object -First 1
  if(-not $entry){$entry=$candidates|?{-not $zipUsed.Contains($_)}|Select-Object -First 1}
  if(-not $entry){$entry=$allVehicleEntries|?{-not $zipUsed.Contains($_)-and $_ -match $actionPatterns[$action]}|Select-Object -First 1}
  if(-not $entry){$entry=$allVehicleEntries|?{-not $zipUsed.Contains($_)}|Select-Object -First 1}
  if(-not $entry){throw "No remaining vehicle source for $vid $action"};[void]$zipUsed.Add($entry)
  & tar -xf $VehicleZip -C $temp $entry;if($LASTEXITCODE){throw "Could not extract $entry"};$src=Join-Path $temp ($entry.Replace('/','\'))
  Convert $src "vehicle_${vid}_${action}.ogg" "$vid $action" "$VehicleZip::$entry"
 }
}

$map=@{'120mm_mortar'='Weapon_M79';'ballista'='Weapon_Crossbow';'crossbow'='Weapon_Welrod';'magnum_revolver'='Weapon_MR73';'taurus_model66_revolver'='Weapon_MR73';'benelli_m4_shotgun'='Weapon_KSG';'ks123shotgun'='Weapon_KS23';'spas_12_shotgun'='Weapon_Model870'}
$allHandling=[System.Collections.Generic.List[System.IO.FileInfo]]::new();Get-ChildItem $InsurgencyRoot -File -Recurse|?{$_.FullName -match '\\handling\\'}|Sort-Object FullName|%{$allHandling.Add($_)}
foreach($weapon in $map.Keys){
 $dir=Join-Path $InsurgencyRoot $map[$weapon];$specific=if(Test-Path $dir){@(Get-ChildItem $dir -File -Recurse)}else{@()}
 foreach($stage in @('open','insert','close','cycle')){
  $pat=switch($stage){'open'{'open|mag_release|bolt_back|cylinder_open'};'insert'{'insert|fetch|mag_in|load|round|shell'};'close'{'close|mag_hit|cylinder_close'};'cycle'{'pump|lever|bolt|charging|slide_release'}}
  $src=$specific|?{$_.Name -match $pat -and -not $used.Contains($_.FullName)}|Sort-Object FullName|Select-Object -First 1;if(-not $src){$src=TakeFile $allHandling}
  Convert $src.FullName "${weapon}reload_${stage}.ogg" "$weapon reload $stage" $src.FullName
 }
}

$ui=[System.Collections.Generic.List[System.IO.FileInfo]]::new();Get-ChildItem $FortniteItems -File -Recurse|?{$_.Extension -in '.ogg','.wav','.mp3' -and $_.Length -lt 1500000 -and $_.Name -notmatch 'Loop|Music|Preview'}|Sort-Object Length,FullName|%{$ui.Add($_)}
foreach($pair in @(@('menumove.ogg','replacement menu movement'),@('menuopen.ogg','replacement menu opening'),@('headshot_indicator.ogg','confirmed headshot indicator'))){$src=TakeFile $ui;Convert $src.FullName $pair[0] $pair[1] $src.FullName}

$manifest=Join-Path $sounds 'VEHICLE_RELOAD_AUDIO_SOURCES.tsv';@("target`tpurpose`tsource")+$rows|Set-Content $manifest -Encoding utf8
Write-Host "Imported $($rows.Count) distinct vehicle, staged-reload, UI, and headshot recordings."
