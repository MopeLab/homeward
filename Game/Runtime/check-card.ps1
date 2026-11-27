param([Parameter(Mandatory)][string]$InstanceId,[Parameter(Mandatory)][string]$RuntimeId,
      [ValidateSet('Tin','Basin','Desk','Replay','SecondOrder')][string]$Stage,
      [switch]$ContinueFromWindow)
$ErrorActionPreference='Stop'
$folder=Join-Path $PSScriptRoot '../Evidence'
function Invoke-Rain([string[]]$Command) {
    $raw = & douyin-world --instance $InstanceId runtime @Command --runtime-id $RuntimeId
    if ($LASTEXITCODE -ne 0) { throw "CLI failed for $Command" }
    $response = $raw | ConvertFrom-Json
    if ($response.ok -eq $false) { throw ($response | ConvertTo-Json -Depth 6) }
    return $response
}
function Observe([string]$Step) {
    $data=(Invoke-Rain @('js','eval','--file',(Join-Path $PSScriptRoot 'observe.js'))).result
    [pscustomobject]@{step=$Step; runtime=$RuntimeId; state=$data} | ConvertTo-Json -Compress -Depth 10 | Add-Content -LiteralPath (Join-Path $folder "input-$RuntimeId.jsonl")
    Write-Host "$Step -> $($data.labels | ConvertTo-Json -Compress)"
    return $data
}
function Tap([double[]]$Point) {
    if ($Point.Count -ne 2) { throw 'Missing visible button' }
    $x=$Point[0].ToString('0.####',[cultureinfo]::InvariantCulture)
    $y=$Point[1].ToString('0.####',[cultureinfo]::InvariantCulture)
    $null=Invoke-Rain @('input','mouse',"click:$x,$y")
}
function Click([string]$Control,[string]$Step) {
    $view=Observe $Step
    if (!$view.controls.$Control) {throw "$Control is hidden at $Step"}
    Tap $view.controls.$Control
}
function StepForward([string]$Action) {
    $null=Invoke-Rain @('input','keys',$Action)
}
function Collect([string]$Source,[string]$Beat) {
    $start=Observe "Before $Source $Beat"
    if ($start.labels.sourceLabel -ne $Source) {throw "Wrong source"}
    Tap $start.controls.listenBtn
    if ($Beat -eq 'B') {Start-Sleep -Milliseconds 3300}
    $preview=Observe "Audition $Source $Beat"
    $label=if ($Beat -eq 'A') {'收下蓄势'} else {'收下落点'}
    if ($preview.labels.keepBtnLabel -ne $label) {throw "Wrong beat"}
    Tap $preview.controls.keepBtn
    $null=Observe "Collected $Source $Beat"
}
function Shot([string]$Name) {
    $null=Invoke-Rain @('screenshot','--out',(Join-Path $folder "$Name.png"))
}
switch ($Stage) {
    'Tin' {
        Collect '雨棚铁皮' A
        Collect '雨棚铁皮' A
        Collect '雨棚铁皮' B
        Click cardEntryBtn 'Open two sounds'
        Click playBtn 'Play first two sounds'
        $null=Observe 'Two-sound replay'
        Click closeBtn 'Skip draft replay'
        Click closeBtn 'Return to canopy'
    }
    'Basin' {
        StepForward 'W:1600'
        $null=Observe 'Crossed the column on foot'
        Shot 'crossing'
        Collect '檐下接雨盆' A
        Collect '檐下接雨盆' B
        Click slot2 'Audition replacement for slot 2'
        Click stampBtn 'Confirm replacement'
        Click swapBtn 'Begin swapping'
        Click slot1 'Swap first'
        Click slot3 'Swap last'
        $null=Observe 'Reordered draft'
        Click closeBtn 'Put draft away'
    }
    'Desk' {
        StepForward 'W:1000'
        $view=Observe 'Arrived at desk on foot'
        if ($view.labels.sourceLabel -ne '窗边回信桌') {throw 'Desk not in range'}
        Click cardEntryBtn 'Sit at the table'
        Click stampBtn 'Stamp the three sounds'
        $null=Observe 'First sealed playback'
        Click closeBtn 'Skip to the static postcard'
        Shot 'postcard'
        Click postmarkBtn 'Replay via postmark'
        $replay=Invoke-Rain @('js','eval','--file',(Join-Path $PSScriptRoot 'read-replay.js'),'--timeout-ms','30000')
        $replay | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $folder "replay-$RuntimeId.json")
    }
    'SecondOrder' {
        if (!$ContinueFromWindow) {
            StepForward 'D:410'
            StepForward 'W:280'
            Collect '宿舍亮窗' A
            StepForward 'S:1100'
        }
        StepForward 'A:230'
        StepForward 'S:600'
        Collect '檐下接雨盆' B
        StepForward 'S:1200'
        Collect '雨棚铁皮' B
        Click cardEntryBtn 'Open a different draft'
        Click playBtn 'Replay voice, basin, then tin'
        $replay=Invoke-Rain @('js','eval','--file',(Join-Path $PSScriptRoot 'read-replay.js'),'--timeout-ms','30000')
        $replay | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $folder "second-order-$RuntimeId.json")
        Shot 'second-order'
    }
    'Replay' {
        Click slot2 'Single slot audition'
        Click soundBtn 'Open sound settings'
        Click rainBtn 'Toggle ambience'
        Click captionBtn 'Toggle captions'
        Click quieterBtn 'Lower volume'
        $null=Observe 'Applied settings'
        Click closeBtn 'Close settings'
        Click stampBtn 'Start a fresh card'
        $null=Observe 'Fresh card'
    }
}
