$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$runtime = Join-Path $taskRoot 'runtime_build/nvgt/release/nvgt.exe'
if (!(Test-Path -LiteralPath $runtime)) { throw 'Build the project-local runtime first; see tools/native/README.md.' }
$tests = @{
    'reactphysics_capabilities.nvgt' = 'IW-reactphysics-capabilities-*'
    'reactphysics_core_regression.nvgt' = 'IW-reactphysics-core-*'
    'reactphysics_map_regression.nvgt' = 'IW-reactphysics-map-*'
    'reactphysics_actor_regression.nvgt' = 'IW-reactphysics-actor-*'
    'reactphysics_structure_regression.nvgt' = 'IW-reactphysics-structure-*'
    'reactphysics_simulation_regression.nvgt' = 'IW-reactphysics-simulation-*'
    '../../iwserver/iwserver.nvgt' = 'IW-physics-server-*'
}
foreach ($map in Get-ChildItem -LiteralPath (Join-Path $taskRoot 'iwserver/content/maps') -Directory) {
    foreach ($source in Get-ChildItem -LiteralPath $map.FullName -Filter '*.map') {
        & python (Join-Path $taskRoot 'tools/compile_physics_maps.py') $source.FullName (Join-Path $taskRoot "runtime_build/maps/$($map.Name).json")
        if ($LASTEXITCODE -ne 0) { throw "Map compilation failed: $($source.FullName)" }
    }
}
Push-Location -LiteralPath $taskRoot
try {
foreach ($test in $tests.Keys) {
    $before = @(Get-ChildItem -LiteralPath (Join-Path $env:LOCALAPPDATA 'Temp') -Directory -Filter $tests[$test] | ForEach-Object FullName)
    $arguments = '"{0}"' -f (Join-Path $PSScriptRoot $test)
    if ($test -eq '../../iwserver/iwserver.nvgt') { $arguments += ' -- --physics-integration-test' }
    $process = Start-Process -FilePath $runtime -ArgumentList $arguments -WindowStyle Hidden -PassThru
    if (!$process.WaitForExit(45000)) {
        $process.Kill()
        throw "$test exceeded 45 seconds; stopped this isolated test process. Inspect its newest checkpoint."
    }
    $process.Refresh()
    $exitCode = $process.ExitCode
    $created = @(Get-ChildItem -LiteralPath (Join-Path $env:LOCALAPPDATA 'Temp') -Directory -Filter $tests[$test] | Where-Object { $_.FullName -notin $before })
    if ($exitCode -ne 0 -or $created.Count -ne 1) { throw "$test failed or did not produce a fresh report (exit $exitCode)." }
    $report = Get-Content -LiteralPath (Join-Path $created[0].FullName 'results.txt') -Raw
    Write-Output $report
    if ($report -notmatch 'Failures: 0\r?\nStage: complete' -or $report -match '(?m)^FAIL ') { throw "$test did not pass: $($created[0].FullName)" }
}
} finally { Pop-Location }
