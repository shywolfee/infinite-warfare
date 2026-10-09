# Idempotent formatting migration: keep served filenames and historical prose.
param([string]$Root = (Split-Path $PSScriptRoot -Parent))
$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)
function Save-Markdown([string]$Path, [string]$Text) {
    [IO.File]::WriteAllText($Path, ($Text.TrimEnd() + "`n"), $utf8)
}
function Plain-Inline([string]$Text) {
    $Text = [regex]::Replace($Text, '<(?:code|kbd)\b[^>]*>(.*?)</(?:code|kbd)>', '`$1`')
    $Text = [regex]::Replace($Text, '<(?:strong|b)\b[^>]*>(.*?)</(?:strong|b)>', '**$1**')
    $Text = [regex]::Replace($Text, '<a\s+[^>]*href="([^"]+)"[^>]*>(.*?)</a>', '[$2]($1)')
    $Text = [regex]::Replace($Text, '<[^>]+>', '')
    return [Net.WebUtility]::HtmlDecode($Text).Trim()
}
$sections = '^(Controls|Player commands|Staff commands.*|Channels|Connection flow|Horizontal turning|Vertical aiming|Using a turbolift|Source-only Release Builder|Client Diagnostics|The editor''s main list|What is here|Build something|Describe what you want|Mark an area|Browse and edit everything on this map|This map|Every map|Content|Go somewhere|Notes|Every item|Armour|Armour repair|Medication|Explosives|Header fields.*|Tile definitions|Zone definitions|Ambience definitions|Ladder definitions|Point of interest definitions|Turbolift definitions|Transition definitions|Opening and navigation|Managing things while fighting|Shortcuts and conversations)$'
$files = @(Get-ChildItem -LiteralPath "$Root/iwserver/docs" -Filter '*.txt')
$files += Get-Item -LiteralPath "$Root/iwserver/content/items/README.txt"
$files += Get-Item -LiteralPath "$Root/iwserver/content/objects/README.txt"
foreach ($file in $files) {
    $source = [IO.File]::ReadAllText($file.FullName).Replace("`r", '')
    if ($source.StartsWith('# ')) { continue }
    $lines = $source.Split("`n")
    $output = New-Object 'Collections.Generic.List[string]'
    $output.Add('# ' + $lines[0].Trim())
    $output.Add('')
    for ($i = 1; $i -lt $lines.Count; $i++) {
        $line = $lines[$i].TrimEnd()
        $trim = $line.Trim()
        if ($trim.TrimEnd(':') -match $sections) {
            $output.Add(''); $output.Add('## ' + $trim.TrimEnd(':')); $output.Add(''); continue
        }
        if ($file.Name -eq 'controls.txt' -and $trim -match '^([^:]+): (.+)$') {
            $output.Add(''); $output.Add('## ' + $Matches[1]); $output.Add(''); $output.Add($Matches[2]); continue
        }
        if ($trim -match '^(/[^ ]+.*?) - (.+)$') {
            $output.Add('- `' + $Matches[1] + '`: ' + $Matches[2]); continue
        }
        if ($line -match '^\s{2,}([a-z_]+)\s{2,}(.+)$') {
            $output.Add('- `' + $Matches[1] + '`: ' + $Matches[2]); continue
        }
        if ($file.Name -in @('vehicles.txt','holsters.txt','support_tickets.txt') -and $line.StartsWith('  ')) {
            $output.Add('- ' + $trim); continue
        }
        if ($file.Name -eq 'turning_and_aiming.txt' -and $trim -match '^([A-Z][^:]*): (.+)$') {
            $output.Add('- `' + $Matches[1] + '`: ' + $Matches[2]); continue
        }
        # Preserve wrapped paragraphs and numbered steps, not accidental code blocks.
        $output.Add($line.TrimStart())
    }
    $text = [string]::Join("`n", $output)
    $text = [regex]::Replace($text, "`n{3,}", "`n`n")
    Save-Markdown $file.FullName $text
}
$changelogPath = "$Root/changes.txt"
$source = [IO.File]::ReadAllText($changelogPath).Replace("`r", '')
if (-not $source.StartsWith('# Infinite Warfare release notes')) {
    $output = New-Object 'Collections.Generic.List[string]'
    $output.Add('# Infinite Warfare release notes'); $output.Add('')
    foreach ($line in $source.Split("`n")) {
        $trim = $line.Trim()
        if ($trim -eq '') { continue }
        if ($trim -match '^(New in |Hotfix for )') {
            $output.Add(''); $output.Add('## ' + $trim); $output.Add(''); continue
        }
        $output.Add('- ' + ($trim -replace '^[-*]\s+', ''))
    }
    Save-Markdown $changelogPath ([string]::Join("`n", $output) -replace "`n{3,}", "`n`n")
}
# Produce a Markdown player manual, retaining headings, lists, links and tables.
$manualPath = "$Root/player_manual.md"
if (-not (Test-Path -LiteralPath $manualPath)) {
    $html = [IO.File]::ReadAllText("$Root/readme.html")
    $body = [regex]::Match($html, '(?s)<body>(.*?)</body>').Groups[1].Value
    $body = [regex]::Replace($body, '(?s)<nav\b.*?</nav>', '')
    $body = [regex]::Replace($body, '(?s)<table\b[^>]*>(.*?)</table>', {
        param($match)
        $rows = New-Object 'Collections.Generic.List[string]'
        foreach ($row in [regex]::Matches($match.Groups[1].Value, '(?s)<tr[^>]*>(.*?)</tr>')) {
            $cells = @([regex]::Matches($row.Groups[1].Value, '(?s)<t[dh][^>]*>(.*?)</t[dh]>') | ForEach-Object { (Plain-Inline $_.Groups[1].Value).Replace('|','\|').Replace("`n",' ') })
            $rows.Add('| ' + [string]::Join(' | ', $cells) + ' |')
            if ($rows.Count -eq 1) { $rows.Add('| ' + [string]::Join(' | ', @($cells | ForEach-Object {'---'})) + ' |') }
        }
        return "`n`n" + [string]::Join("`n", $rows) + "`n`n"
    })
    $body = [regex]::Replace($body, '(?s)<h([1-6])[^>]*>(.*?)</h\1>', { param($m) "`n`n" + ('#' * [int]$m.Groups[1].Value) + ' ' + (Plain-Inline $m.Groups[2].Value) + "`n`n" })
    $body = [regex]::Replace($body, '(?s)<ol[^>]*>(.*?)</ol>', { param($m) "`n`n" + [regex]::Replace($m.Groups[1].Value, '(?s)<li[^>]*>(.*?)</li>', {param($n) "`n1. " + (Plain-Inline $n.Groups[1].Value)}) + "`n`n" })
    $body = [regex]::Replace($body, '(?s)<li[^>]*>(.*?)</li>', { param($m) "`n- " + (Plain-Inline $m.Groups[1].Value) })
    $body = [regex]::Replace($body, '</?(?:p|ul|div|section|header|footer)[^>]*>', "`n`n")
    $body = Plain-Inline $body
    $body = [regex]::Replace($body.Replace("`r", ''), "`n[ \t]+", "`n")
    $body = [regex]::Replace($body, "`n{3,}", "`n`n")
    Save-Markdown $manualPath $body
}
Write-Output 'Formatted help topics, release notes and the Markdown manual'
