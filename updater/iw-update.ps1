# Infinite Warfare updater.
#
# The game checks GitHub's version.txt, asks the player, then starts this
# script and exits so none of its files are locked. This script:
#
#   1. Pins the branch to one commit and reads that commit's file list (the
#      git tree) from the GitHub API.
#   2. Compares every file the installation should have with what is on disk,
#      by git blob SHA-1, so only files that actually changed are downloaded.
#      A Windows checkout's CRLF line endings count as unchanged.
#   3. Downloads the changed files into a staging folder and verifies each one
#      against its SHA-1 before anything in the installation is touched.
#   4. Backs up every file it will replace or delete, then applies the update.
#      Files the game no longer ships (updater/retired_files.txt, and anything
#      this updater installed last time that has since gone) are deleted. If
#      any step fails, everything is put back as it was.
#   5. Writes updater/last_update.txt, which the game reads and announces on
#      its next start, and restarts the game.
#
# It replaces an updater that downloaded the whole repository as a zip and
# copied it over the installation: it never deleted anything, so moved or
# removed weapon and item files stayed behind and kept loading; it ignored
# copy failures and deleted its download anyway; and its restart from source
# passed "Infinite Warfare.nvgt" unquoted, so the game never came back.
#
# It must run under Windows PowerShell 5.1, which is what the game starts.

param(
    [Parameter(Mandatory = $true)][string]$Root,
    [string]$Restart = "",
    [ValidateSet("source", "compiled")][string]$Mode = "compiled",
    [string]$Repository = "shywolfee/infinite-warfare",
    [string]$Branch = "main",
    [string]$ApiBase = "https://api.github.com",
    [string]$RawBase = "https://raw.githubusercontent.com",
    [string]$ArchiveBase = "https://github.com",
    [int]$WaitSeconds = 30,
    [int]$ArchiveThreshold = 150,
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

$Root = (Resolve-Path -LiteralPath $Root).Path
$UpdaterDir = Join-Path $Root "updater"
$LogPath = Join-Path $UpdaterDir "last_update.log"
$ResultPath = Join-Path $UpdaterDir "last_update.txt"
$ManifestPath = Join-Path $UpdaterDir "installed_files.txt"
# Which commit this installation now matches; Repository status compares it
# with GitHub.
$CommitPath = Join-Path $UpdaterDir "installed_commit.txt"
$Utf8 = New-Object System.Text.UTF8Encoding($false)
# Windows PowerShell 5.1 refuses User-Agent and Accept in -Headers ("must be
# modified using the appropriate property"), so the agent goes in -UserAgent
# and GitHub's default JSON response is used.
$Agent = "InfiniteWarfareUpdater"

# Files the server writes for itself. An update never overwrites or deletes them.
$Protected = @("iwserver/admins.txt", "iwserver/motd.svr", "iwserver/currentmap.txt")

if (-not (Test-Path -LiteralPath $UpdaterDir)) { New-Item -ItemType Directory -Path $UpdaterDir -Force | Out-Null }
[IO.File]::WriteAllText($LogPath, "", $Utf8)

function Log([string]$text) {
    $line = (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "  " + $text
    Write-Host $text
    [IO.File]::AppendAllText($LogPath, $line + [Environment]::NewLine, $Utf8)
}

function Write-Result([string]$status, [string]$message, [hashtable]$extra) {
    $lines = @("status=$status", "message=$message")
    if ($extra) { foreach ($k in $extra.Keys) { $lines += "$k=$($extra[$k])" } }
    [IO.File]::WriteAllText($ResultPath, ($lines -join "`n") + "`n", $Utf8)
}

function Local-Path([string]$relative) {
    return Join-Path $Root ($relative -replace "/", [IO.Path]::DirectorySeparatorChar)
}

# git's blob id: SHA-1 of "blob <length>\0" followed by the file's bytes.
function Blob-Sha([byte[]]$bytes) {
    $sha = [Security.Cryptography.SHA1]::Create()
    try {
        $header = [Text.Encoding]::ASCII.GetBytes("blob " + $bytes.Length + [char]0)
        $all = New-Object byte[] ($header.Length + $bytes.Length)
        [Array]::Copy($header, 0, $all, 0, $header.Length)
        [Array]::Copy($bytes, 0, $all, $header.Length, $bytes.Length)
        return ([BitConverter]::ToString($sha.ComputeHash($all)) -replace "-", "").ToLowerInvariant()
    } finally { $sha.Dispose() }
}

# True when the file on disk already holds this blob. A checkout made by Git
# for Windows has CRLF line endings where the repository has LF; that is the
# same file, not a change.
function File-Matches([string]$path, [string]$sha) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return $false }
    $bytes = [IO.File]::ReadAllBytes($path)
    if ((Blob-Sha $bytes) -eq $sha) { return $true }
    if ([Array]::IndexOf($bytes, [byte]13) -lt 0) { return $false }
    # Latin-1 maps every byte to one character and back, so this is exact.
    $latin1 = [Text.Encoding]::GetEncoding(28591)
    return (Blob-Sha ($latin1.GetBytes($latin1.GetString($bytes).Replace("`r`n", "`n")))) -eq $sha
}

# Where a repository file belongs in this installation, or $null if it does
# not belong in it. A source checkout mirrors the repository. A release
# folder (built by "Compress release build") holds the executable, its
# libraries, the client's content folders and the documents beside it.
function Map-Path([string]$repoPath, [string]$layout) {
    if ($Protected -contains $repoPath) { return $null }
    if ($layout -eq "source") { return $repoPath }
    $rootFiles = @("Infinite Warfare.exe", "changes.txt", "readme.html", "player_manual.md", "README.md", "developers.txt", "rules.txt", "version.txt")
    if ($rootFiles -contains $repoPath) { return $repoPath }
    if ($repoPath.StartsWith("lib/") -or $repoPath.StartsWith("updater/")) { return $repoPath }
    foreach ($folder in @("weapons", "items", "editor")) {
        $prefix = "iwserver/content/$folder/"
        if ($repoPath.StartsWith($prefix)) { return "content/$folder/" + $repoPath.Substring($prefix.Length) }
    }
    return $null
}

function Escape-RepoPath([string]$path) {
    return (($path -split "/") | ForEach-Object { [Uri]::EscapeDataString($_) }) -join "/"
}

function Get-Json([string]$url) {
    try { return Invoke-RestMethod -UseBasicParsing -Uri $url -UserAgent $Agent }
    catch {
        $detail = $_.Exception.Message
        if ($detail -match "403|rate limit") { $detail += " GitHub limits how often an address may ask; try again in an hour." }
        throw "Could not read $url : $detail"
    }
}

function Download([string]$url, [string]$destination) {
    $dir = Split-Path -Parent $destination
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $last = $null
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        try { Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $destination -UserAgent $Agent; return }
        catch { $last = $_.Exception.Message; Start-Sleep -Seconds $attempt }
    }
    throw "Could not download $url : $last"
}

# Waits for the game to let go of a file it had open.
function Wait-Unlocked([string]$path) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return }
    $deadline = (Get-Date).AddSeconds($WaitSeconds)
    while ($true) {
        try { $s = [IO.File]::Open($path, "Open", "ReadWrite", "None"); $s.Close(); return }
        catch {
            if ((Get-Date) -gt $deadline) { throw "$path is still in use. Close Infinite Warfare and anything else using it, then update again." }
            Start-Sleep -Milliseconds 500
        }
    }
}

function Start-Game {
    if ($Restart -eq "" -or $CheckOnly) { return }
    try {
        if ($Mode -eq "source") {
            # Quoted, because the path always contains a space.
            Start-Process -FilePath $Restart -ArgumentList ('"' + (Join-Path $Root "Infinite Warfare.nvgt") + '"') -WorkingDirectory $Root
        } else {
            Start-Process -FilePath $Restart -WorkingDirectory $Root
        }
    } catch { Log "Could not restart the game: $($_.Exception.Message). Start it yourself." }
}

$stage = Join-Path $Root ".iw-update"
$applied = New-Object System.Collections.ArrayList   # @{ path; backup } in order applied
$exitCode = 0
try {
    $layout = "compiled"
    if ((Test-Path -LiteralPath (Join-Path $Root "Infinite Warfare.nvgt")) -or (Test-Path -LiteralPath (Join-Path $Root "iwserver"))) { $layout = "source" } else { $layout = "release" }
    Log "Infinite Warfare updater. Installation: $Root ($layout layout)."

    $commit = Get-Json "$ApiBase/repos/$Repository/commits/$Branch"
    $sha = [string]$commit.sha
    if ($sha -notmatch "^[0-9a-f]{40}$") { throw "GitHub did not return a commit for branch $Branch." }
    Log "Latest commit on $Branch is $($sha.Substring(0, 10))."
    $tree = Get-Json "$ApiBase/repos/$Repository/git/trees/$sha`?recursive=1"
    $useArchive = [bool]$tree.truncated

    # Every file this installation should hold, keyed by its local path.
    $wanted = @{}
    foreach ($entry in $tree.tree) {
        if ($entry.type -ne "blob" -or $entry.mode -eq "120000") { continue }
        $dest = Map-Path ([string]$entry.path) $layout
        if ($dest) { $wanted[$dest] = @{ repo = [string]$entry.path; sha = [string]$entry.sha } }
    }
    if ($wanted.Count -eq 0) { throw "The commit has no files for this installation." }

    $changed = New-Object System.Collections.ArrayList
    foreach ($dest in ($wanted.Keys | Sort-Object)) {
        if (-not (File-Matches (Local-Path $dest) $wanted[$dest].sha)) { [void]$changed.Add($dest) }
    }

    # What to delete: files the game has retired, and files this updater put
    # here last time that the new version no longer has.
    $retired = New-Object System.Collections.ArrayList
    $retiredSource = $null
    foreach ($dest in $wanted.Keys) { if ($wanted[$dest].repo -eq "updater/retired_files.txt") { $retiredSource = $wanted[$dest] } }
    $candidates = @()
    if ($retiredSource) {
        $listPath = Join-Path ([IO.Path]::GetTempPath()) ("iw-retired-" + [Guid]::NewGuid().ToString("N") + ".txt")
        Download "$RawBase/$Repository/$sha/updater/retired_files.txt" $listPath
        $candidates += Get-Content -LiteralPath $listPath | ForEach-Object { Map-Path ($_.Trim()) $layout }
        Remove-Item -LiteralPath $listPath -Force
    }
    if (Test-Path -LiteralPath $ManifestPath) { $candidates += Get-Content -LiteralPath $ManifestPath | ForEach-Object { $_.Trim() } }
    foreach ($dest in ($candidates | Where-Object { $_ } | Sort-Object -Unique)) {
        if ($dest.Contains("..") -or $wanted.ContainsKey($dest) -or $Protected -contains $dest) { continue }
        if (Test-Path -LiteralPath (Local-Path $dest) -PathType Leaf) { [void]$retired.Add($dest) }
    }

    Log "$($changed.Count) files to download, $($retired.Count) old files to remove."
    if ($CheckOnly) {
        foreach ($d in $changed) { Log "  update $d" }
        foreach ($d in $retired) { Log "  remove $d" }
        Write-Result "checked" "$($changed.Count) files would be updated and $($retired.Count) removed." @{ commit = $sha; changed = $changed.Count; removed = $retired.Count }
        exit 0
    }
    if ($changed.Count -eq 0 -and $retired.Count -eq 0) {
        [IO.File]::WriteAllText($CommitPath, $sha + "`n", $Utf8)
        Write-Result "current" "Every file already matches the latest version." @{ commit = $sha }
        Log "Nothing to do."
        Start-Game
        exit 0
    }

    # Download and verify everything before touching the installation.
    if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
    $files = Join-Path $stage "files"
    $backup = Join-Path $stage "backup"
    New-Item -ItemType Directory -Path $files -Force | Out-Null
    New-Item -ItemType Directory -Path $backup -Force | Out-Null
    if ($changed.Count -gt $ArchiveThreshold) { $useArchive = $true }
    if ($useArchive) {
        Log "Downloading the whole version as one archive."
        $zip = Join-Path $stage "update.zip"
        Download "$ArchiveBase/$Repository/archive/$sha.zip" $zip
        $unzipped = Join-Path $stage "archive"
        Expand-Archive -LiteralPath $zip -DestinationPath $unzipped -Force
        $top = Get-ChildItem -LiteralPath $unzipped -Directory | Select-Object -First 1
        if (-not $top) { throw "The downloaded archive was empty." }
        foreach ($dest in $changed) {
            $from = Join-Path $top.FullName ($wanted[$dest].repo -replace "/", [IO.Path]::DirectorySeparatorChar)
            $to = Join-Path $files ($dest -replace "/", [IO.Path]::DirectorySeparatorChar)
            New-Item -ItemType Directory -Path (Split-Path -Parent $to) -Force | Out-Null
            if (-not (Test-Path -LiteralPath $from -PathType Leaf)) { throw "The archive is missing $($wanted[$dest].repo)." }
            Copy-Item -LiteralPath $from -Destination $to -Force
        }
    } else {
        $n = 0
        foreach ($dest in $changed) {
            $n++
            Log "Downloading $n of $($changed.Count): $dest"
            Download "$RawBase/$Repository/$sha/$(Escape-RepoPath $wanted[$dest].repo)" (Join-Path $files ($dest -replace "/", [IO.Path]::DirectorySeparatorChar))
        }
    }
    foreach ($dest in $changed) {
        $staged = Join-Path $files ($dest -replace "/", [IO.Path]::DirectorySeparatorChar)
        if ((Blob-Sha ([IO.File]::ReadAllBytes($staged))) -ne $wanted[$dest].sha) { throw "$dest did not download correctly." }
    }
    Log "All downloads verified."

    # Apply, keeping a backup of everything replaced or removed.
    foreach ($dest in $changed) {
        $target = Local-Path $dest
        Wait-Unlocked $target
        $saved = $null
        if (Test-Path -LiteralPath $target -PathType Leaf) {
            $saved = Join-Path $backup ($dest -replace "/", [IO.Path]::DirectorySeparatorChar)
            New-Item -ItemType Directory -Path (Split-Path -Parent $saved) -Force | Out-Null
            Copy-Item -LiteralPath $target -Destination $saved -Force
        }
        [void]$applied.Add(@{ path = $target; backup = $saved })
        New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
        Copy-Item -LiteralPath (Join-Path $files ($dest -replace "/", [IO.Path]::DirectorySeparatorChar)) -Destination $target -Force
    }
    foreach ($dest in $retired) {
        $target = Local-Path $dest
        Wait-Unlocked $target
        $saved = Join-Path $backup ($dest -replace "/", [IO.Path]::DirectorySeparatorChar)
        New-Item -ItemType Directory -Path (Split-Path -Parent $saved) -Force | Out-Null
        Copy-Item -LiteralPath $target -Destination $saved -Force
        [void]$applied.Add(@{ path = $target; backup = $saved })
        Remove-Item -LiteralPath $target -Force
        Log "Removed $dest"
    }

    [IO.File]::WriteAllText($ManifestPath, (($wanted.Keys | Sort-Object) -join "`n") + "`n", $Utf8)
    [IO.File]::WriteAllText($CommitPath, $sha + "`n", $Utf8)
    $version = ""
    $versionFile = Local-Path "version.txt"
    if (Test-Path -LiteralPath $versionFile) { $version = (Get-Content -LiteralPath $versionFile -Raw).Trim() }
    Write-Result "updated" "Updated to version ${version}: $($changed.Count) files updated, $($retired.Count) removed." @{ commit = $sha; version = $version; changed = $changed.Count; removed = $retired.Count }
    Log "Update complete."
    Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
}
catch {
    $exitCode = 1
    $reason = $_.Exception.Message
    Log "Update failed: $reason"
    if ($applied.Count -gt 0) {
        Log "Putting back the $($applied.Count) files already changed."
        for ($i = $applied.Count - 1; $i -ge 0; $i--) {
            $item = $applied[$i]
            try {
                if ($item.backup) { Copy-Item -LiteralPath $item.backup -Destination $item.path -Force }
                elseif (Test-Path -LiteralPath $item.path) { Remove-Item -LiteralPath $item.path -Force }
            } catch { Log "Could not restore $($item.path): $($_.Exception.Message). A copy is in $stage" ; $reason += " Some files could not be restored; copies are in $stage." }
        }
    }
    Write-Result "failed" "The update failed and your installation was left as it was. $reason" @{}
}
Start-Game
exit $exitCode
