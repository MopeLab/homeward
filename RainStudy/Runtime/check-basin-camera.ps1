param([Parameter(Mandatory)][string]$InstanceId,[Parameter(Mandatory)][string]$RuntimeId,[Parameter(Mandatory)][string]$Evidence)
$ErrorActionPreference = 'Stop'
function Run([string[]]$ArgsForCLI) {
    $raw = & douyin-world --instance $InstanceId runtime @ArgsForCLI --runtime-id $RuntimeId
    if ($LASTEXITCODE -ne 0) { throw "Failed: $ArgsForCLI" }
    $data = $raw | ConvertFrom-Json
    if ($data.ok -eq $false) { throw ($data | ConvertTo-Json -Depth 5) }
    return $data
}
function Observe { return (Run @('js','eval','--file',(Join-Path $PSScriptRoot 'observe.js'))).result }
function Tap([double[]]$Point) {
    if ($Point.Count -ne 2) { throw 'Control is not visible' }
    $null = Run @('input','mouse',('click:{0},{1}' -f $Point[0],$Point[1]))
}
$view=Observe
if ($view.labels.sourceLabel -ne '檐下接雨盆') { throw 'Begin in basin range' }
Tap $view.controls.listenBtn
$view=Observe
Tap $view.controls.keepBtn
Tap $view.controls.listenBtn
Start-Sleep -Seconds 3.2
Tap $view.controls.keepBtn
$records=@()
for ($cycle=1;$cycle -le 4;$cycle++) {
    $view=Observe
    Tap $view.controls.listenBtn
    $listening=Observe
    Tap $listening.controls.keepBtn
    Tap $view.controls.cardEntryBtn
    $panel=Observe
    Tap $panel.controls.slot1
    Tap $panel.controls.closeBtn
    $state=(Run @('js','eval','--file',(Join-Path $PSScriptRoot 'camera-state.js'))).result
    $records += [pscustomobject]@{cycle=$cycle;slots=@($panel.labels.slot1Title,$panel.labels.slot2Title);state=$state}
}
$records | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $Evidence
$records | ForEach-Object { "cycle $($_.cycle): $($_.slots -join '/') | camera $($_.state.camera -join ',') | visible $($_.state.visible.Count)" }
