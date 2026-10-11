param([Parameter(Mandatory = $true)][string]$StatusPath)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$form = New-Object System.Windows.Forms.Form
$form.Text = 'Infinite Warfare Server'
$form.Size = New-Object System.Drawing.Size(680, 440)
$form.MinimumSize = New-Object System.Drawing.Size(520, 300)
$form.StartPosition = 'CenterScreen'

$heading = New-Object System.Windows.Forms.Label
$heading.Text = 'Server startup'
$heading.Font = New-Object System.Drawing.Font('Segoe UI', 15, [System.Drawing.FontStyle]::Bold)
$heading.AutoSize = $true
$heading.Location = New-Object System.Drawing.Point(16, 14)
$form.Controls.Add($heading)

$phase = New-Object System.Windows.Forms.Label
$phase.Text = 'Opening the server port'
$phase.AutoSize = $false
$phase.Location = New-Object System.Drawing.Point(18, 55)
$phase.Size = New-Object System.Drawing.Size(620, 38)
$phase.Anchor = 'Top,Left,Right'
$form.Controls.Add($phase)

$progress = New-Object System.Windows.Forms.ProgressBar
$progress.Location = New-Object System.Drawing.Point(18, 100)
$progress.Size = New-Object System.Drawing.Size(620, 22)
$progress.Anchor = 'Top,Left,Right'
$form.Controls.Add($progress)

$queue = New-Object System.Windows.Forms.Label
$queue.Text = '0 waiting'
$queue.Location = New-Object System.Drawing.Point(18, 135)
$queue.Size = New-Object System.Drawing.Size(620, 25)
$queue.Anchor = 'Top,Left,Right'
$form.Controls.Add($queue)

$history = New-Object System.Windows.Forms.TextBox
$history.Multiline = $true
$history.ReadOnly = $true
$history.ScrollBars = 'Vertical'
$history.Location = New-Object System.Drawing.Point(18, 168)
$history.Size = New-Object System.Drawing.Size(620, 180)
$history.Anchor = 'Top,Bottom,Left,Right'
$form.Controls.Add($history)

$stop = New-Object System.Windows.Forms.Button
$stop.Text = 'Stop server'
$stop.Location = New-Object System.Drawing.Point(18, 360)
$stop.Size = New-Object System.Drawing.Size(120, 30)
$stop.Anchor = 'Bottom,Left'
$stop.Add_Click({
    [System.IO.File]::WriteAllText("$StatusPath.stop", 'stop')
    $stop.Enabled = $false
    $phase.Text = 'Stop requested. Waiting for the current load step to finish.'
})
$form.Controls.Add($stop)

$script:lastHistory = ''
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 250
$timer.Add_Tick({
    try {
        if (-not [System.IO.File]::Exists($StatusPath)) { return }
        $raw = [System.IO.File]::ReadAllText($StatusPath).TrimEnd()
        $lines = [regex]::Split($raw, '\r?\n')
        $parts = $lines[0].Split('|', 4)
        if ($parts.Length -lt 4) { return }
        $amount = 0
        if (-not [int]::TryParse($parts[1], [ref]$amount)) { return }
        $progress.Value = [Math]::Max(0, [Math]::Min(100, $amount))
        if ($parts[0] -eq 'Stopped') { $heading.Text = 'Server stopped'; $stop.Enabled = $false }
        elseif ($parts[0] -eq 'Ready') { $heading.Text = 'Server ready' }
        else { $heading.Text = 'Server startup' }
        $phase.Text = "$amount% - $($parts[2])"
        $queue.Text = $parts[3]
        $newHistory = ($lines | Select-Object -Skip 1) -join "`r`n"
        if ($newHistory -ne $script:lastHistory) {
            $history.Text = $newHistory
            $history.SelectionStart = $history.Text.Length
            $history.ScrollToCaret()
            $script:lastHistory = $newHistory
        }
    } catch [System.IO.IOException] {
        # A read can overlap the server's short status-file write.
    }
})
$form.Add_Shown({ $timer.Start() })
$form.Add_FormClosed({ $timer.Stop(); $timer.Dispose() })
[System.Windows.Forms.Application]::Run($form)
