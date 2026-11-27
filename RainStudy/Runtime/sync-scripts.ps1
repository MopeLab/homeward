param(
    [Parameter(Mandatory)][string]$PrefabRoot,
    [ValidateSet('Card','Host','GutterRain','BakedColors')][string]$Part
)
$ErrorActionPreference = 'Stop'
$runtimeSource = $PSScriptRoot
if ($Part -eq 'Card') {
    $fileName = 'Postcard.lua'
    $sourceFiles = @(Join-Path $runtimeSource '../Card/RainCard.lua')
} elseif ($Part -eq 'Host') {
    $fileName = 'RainHost.lua'
    $sourceFiles = @(
        (Join-Path $runtimeSource '../Audio/RainHost.lua'),
        (Join-Path $runtimeSource 'locations.lua')
    )
} else {
    $fileName = "$Part.lua"
    $sourceFiles = @(Join-Path $runtimeSource "../Scenery/$fileName")
    if ($Part -eq 'BakedColors') {
        $sourceFiles += Join-Path $runtimeSource '../ShoreRoute/River/river-display.lua'
    }
}
$target = Join-Path $PrefabRoot "scripts/$fileName"
$current = [IO.File]::ReadAllLines($target)
if ($current.Length -lt 2 -or $current[0] -notmatch '^---@id [\da-f-]+$' -or $current[1] -ne "---@referenceName $fileName") {
    throw "Unexpected SDK identity in $target"
}
$body = ($sourceFiles | ForEach-Object { [IO.File]::ReadAllText((Resolve-Path -LiteralPath $_)) }) -join "`n"
[IO.File]::WriteAllText($target, ($current[0..1] -join "`n") + "`n" + $body, [Text.UTF8Encoding]::new($false))
