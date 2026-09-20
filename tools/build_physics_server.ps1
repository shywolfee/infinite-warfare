$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$runtime = Join-Path $projectRoot 'runtime_build\nvgt\release\nvgt.exe'
$serverSource = Join-Path $projectRoot 'iwserver\iwserver.nvgt'
$mapSourceRoot = Join-Path $projectRoot 'iwserver\content\maps'
$physicsMapRoot = Join-Path $projectRoot 'iwserver\physics_maps'

if (!(Test-Path -LiteralPath $runtime)) {
    throw 'The pinned ReactPhysics NVGT runtime is missing. See tools/native/README.md to build it once.'
}

New-Item -ItemType Directory -Path $physicsMapRoot -Force | Out-Null
foreach ($mapFolder in Get-ChildItem -LiteralPath $mapSourceRoot -Directory) {
    $sources = @(Get-ChildItem -LiteralPath $mapFolder.FullName -Filter '*.map')
    if ($sources.Count -ne 1) { throw "Expected exactly one map source in $($mapFolder.FullName)." }
    $output = Join-Path $physicsMapRoot ($mapFolder.Name + '.json')
    & python (Join-Path $projectRoot 'tools\compile_physics_maps.py') $sources[0].FullName $output
    if ($LASTEXITCODE -ne 0) { throw "Physics-map compilation failed for $($mapFolder.Name)." }
}

Push-Location -LiteralPath $projectRoot
try {
    # Produce the directly runnable server executable, not NVGT's default ZIP
    # bundle. The game already keeps its server data beside this executable.
    & $runtime $serverSource -c -s build.output_basename=iwserver/iwserver_physics -s build.windows_bundle=0
    if ($LASTEXITCODE -ne 0) { throw "Native server compilation failed with exit code $LASTEXITCODE." }
} finally {
    Pop-Location
}

$serverExecutable = Join-Path $projectRoot 'iwserver\iwserver_physics.exe'
if (!(Test-Path -LiteralPath $serverExecutable)) { throw 'Compilation reported success but did not produce iwserver_physics.exe.' }
$bootReport = Join-Path $env:LOCALAPPDATA 'Temp\InfiniteWarfare-physics-boot.txt'
Remove-Item -LiteralPath $bootReport -Force -ErrorAction SilentlyContinue
$bootTest = Start-Process -FilePath $serverExecutable -ArgumentList '--physics-boot-test' -WorkingDirectory (Join-Path $projectRoot 'iwserver') -WindowStyle Hidden -PassThru
if (!$bootTest.WaitForExit(20000)) { $bootTest.Kill(); throw 'The compiled server did not finish its native-physics boot test within twenty seconds.' }
if (!(Test-Path -LiteralPath $bootReport)) { throw 'The compiled server did not create its native-physics boot report.' }
$bootStatus = Get-Content -LiteralPath $bootReport -Raw
Remove-Item -LiteralPath $bootReport -Force
if ($bootStatus -notmatch '^Native server physics: enabled automatically\.') { throw "Native-physics boot validation failed: $bootStatus" }
Write-Output "Native physics server ready: $serverExecutable"
Write-Output $bootStatus
Write-Output 'Run iwserver_physics.exe for ReactPhysics. The separate iwserver.exe remains the regular server.'
