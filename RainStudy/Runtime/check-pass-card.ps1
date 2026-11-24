param([Parameter(Mandatory)][string]$InstanceId, [Parameter(Mandatory)][string]$RuntimeId,
      [ValidateSet('FirstHand','Table','Guest','Seal','NextPair','PersonalCard')][string]$Stage)
$ErrorActionPreference = 'Stop'
$evidence = Join-Path $PSScriptRoot '../Evidence'
function Run([string[]]$Commands) {
    $raw = & douyin-world --instance $InstanceId runtime @Commands --runtime-id $RuntimeId
    if ($LASTEXITCODE) { throw ($raw -join ' ') }
    $response = $raw | ConvertFrom-Json
    if ($response.ok -eq $false) { throw ($raw -join ' ') }
    $response
}
function Read-Screen([string]$Step) {
    $state = (Run @('js','eval','--file',(Join-Path $PSScriptRoot 'observe.js'))).result
    [pscustomobject]@{step=$Step;runtime=$RuntimeId;state=$state} | ConvertTo-Json -Compress -Depth 9 |
        Add-Content -LiteralPath (Join-Path $evidence "pass-card-$RuntimeId.jsonl")
    $state
}
function Click([string]$Control, [string]$Expected='') {
    $view = Read-Screen "点 $Control $Expected"
    $point = $view.controls.$Control
    if (!$point) { throw "Missing $Control; $($view.labels | ConvertTo-Json -Compress)" }
    $caption = $view.labels.("${Control}Label")
    if ($Expected -and $caption -ne $Expected) { throw "Expected $Expected, saw $caption" }
    $coords = ($point | ForEach-Object { $_.ToString('0.####',[cultureinfo]::InvariantCulture) }) -join ','
    $null = Run @('input','mouse',"click:$coords")
}
function Walk([string]$Movement) { $null = Run @('input','keys',$Movement) }
function Require-Label([string]$Label, [string]$Value) {
    $v = Read-Screen "核对 $Value"
    if ($v.labels.$Label -ne $Value) { throw "Expected $Value; $($v.labels | ConvertTo-Json -Compress)" }
}
function Collect([string]$Beat) {
    Click listenBtn
    if ($Beat -eq 'B') { Start-Sleep -Milliseconds 3200 }
    Click keepBtn $(if ($Beat -eq 'A') {'收下蓄势'} else {'收下落点'})
}
switch ($Stage) {
    FirstHand {
        Walk 'W:400'
        Require-Label sourceLabel '雨棚铁皮'
        Collect A
        Collect B
        Walk 'W:2250'
    }
    Table {
        Require-Label sourceLabel '窗边回信桌'
        Click listenBtn '合写一封'
        Click slot2
        Click closeBtn
        Require-Label slot1Title '棚上碎雨'
        Require-Label slot2Title '铁皮重滴'
        Click closeBtn
        Click listenBtn '合写一封'
        Click slot2
        Click stampBtn '选好，递给乙'
        Require-Label cardEntryBtnLabel '乙的声音 · 0/3'
    }
    Guest {
        Walk 'S:1000'
        Require-Label sourceLabel '檐下接雨盆'
        Collect A
        Walk 'W:1000'
        Require-Label sourceLabel '窗边回信桌'
        Click cardEntryBtn '乙的声音 · 1/3'
        Require-Label slot1Title '盆中双响'
        Click slot1
        Click stampBtn '放入第二格'
        Click swapBtn '换甲来提议'
        Click slot1
        Click stampBtn '提议这拍'
        Require-Label postmarkLabel '等乙按章'
    }
    Seal {
        Click swapBtn '按章合寄'
        # Repeat the exact physical input at the shuttered stamp position.
        $v = Get-Content -LiteralPath (Join-Path $evidence "pass-card-$RuntimeId.jsonl") -Tail 1 | ConvertFrom-Json
        $coords = $v.state.controls.swapBtn -join ','
        $null = Run @('input','mouse',"click:$coords")
        Start-Sleep -Seconds 10
        Require-Label mailHeading '我们合寄的一封信'
        $null = Run @('screenshot','--out',(Join-Path $evidence 'pass-card.png'))
        Click postmarkBtn
        $frames = (Run @('js','eval','--file',(Join-Path $PSScriptRoot 'read-replay.js'),'--timeout-ms','30000')).result
        $frames | ConvertTo-Json -Depth 9 | Set-Content (Join-Path $evidence "pass-replay-$RuntimeId.json")
        $assets = (Run @('lua','eval','return {S01B=S01B:GetInstanceID(), S02A=S02A:GetInstanceID(), S01A=S01A:GetInstanceID()}','--script','RainHost.lua')).result
        $clips = @($frames | Where-Object { $null -ne $_.clip } | Select-Object -ExpandProperty clip -Unique)
        $expected = @($assets.S01B,$assets.S02A,$assets.S01A)
        if (($clips -join ',') -ne ($expected -join ',')) { throw "Audio order mismatch: $clips / $expected" }
    }
    PersonalCard {
        Click closeBtn
        Require-Label sourceLabel '檐下接雨盆'
        Collect B
        Walk 'W:1000'
        Click cardEntryBtn '坐到回信桌'
        Click stampBtn '盖章寄出'
        Click closeBtn
        Require-Label mailHeading '给家里的一封信'
        Click slot2
        Click closeBtn
        Click listenBtn '合写一封'
        Click slot1
        Click stampBtn '选好，递给乙'
        Walk 'S:1000'
        Collect A
        Click cardEntryBtn '乙的声音 · 1/3'
        Click closeBtn
        Require-Label mailHeading '给家里的一封信'
        Require-Label slot3Title '迟来一滴'
    }
    NextPair {
        Click slot2
        Click stampBtn '回到个人草稿'
        Require-Label slot1Title '棚上碎雨'
        Require-Label slot2Title '铁皮重滴'
        Require-Label slot3Title '待收一声'
        Click closeBtn
        Click keepBtn '上封合写'
        Require-Label slot2Title '○ 盆中双响'
        Click closeBtn
        Click closeBtn
        Click listenBtn '合写一封'
        Click slot1
        Click stampBtn '选好，递给乙'
        Require-Label cardEntryBtnLabel '乙的声音 · 0/3'
        Click cardEntryBtn
        Require-Label slot1Title '待收一声'
        Click closeBtn
        Require-Label slot2Title '铁皮重滴'
        Click closeBtn
        Click listenBtn '合写一封'
        Click slot1
        Walk 'S:1000'
        Require-Label feedbackLine '已离开回信桌，个人明信片已取回。'
        Require-Label slot2Title '铁皮重滴'
    }
}
Write-Output "$Stage passed"
