<#
.Synopsis
Activate a Python virtual environment for PowerShell.
#>
function global:deactivate ([switch]$NonDestructive) {
    if (Test-Path variable:_OLD_VIRTUAL_PATH) {
        $env:PATH = $variable:_OLD_VIRTUAL_PATH
        Remove-Variable "_OLD_VIRTUAL_PATH" -Scope global
    }
    if (Test-Path function:_old_virtual_prompt) {
        $function:prompt = $function:_old_virtual_prompt
        Remove-Item function:_old_virtual_prompt
    }
    if ($env:VIRTUAL_ENV) {
        Remove-Item env:VIRTUAL_ENV -ErrorAction SilentlyContinue
    }
    if (-not $NonDestructive) {
        Remove-Item function:deactivate
    }
}

deactivate -nondestructive

$VIRTUAL_ENV = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$env:VIRTUAL_ENV = $VIRTUAL_ENV

$global:_OLD_VIRTUAL_PATH = $env:PATH
$env:PATH = "$VIRTUAL_ENV\Scripts;" + $env:PATH

if (!$env:VIRTUAL_ENV_DISABLE_PROMPT) {
    function global:_old_virtual_prompt {
        ""
    }
    $function:_old_virtual_prompt = $function:prompt
    function global:prompt {
        Write-Host -NoNewline "(venv) "
        & $function:_old_virtual_prompt
    }
}

