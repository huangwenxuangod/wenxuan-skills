param(
    [switch]$WithHooks = $true
)

$ErrorActionPreference = "Stop"

function Write-Info($message) {
    Write-Host "[zero-lost] $message"
}

function Ensure-Command($name) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "Required command not found on PATH: $name"
    }
    return $cmd
}

function Copy-SkillDirectory($sourceDir, $destDir) {
    if (-not (Test-Path $sourceDir)) {
        throw "Source skill directory not found: $sourceDir"
    }

    if (Test-Path $destDir) {
        Remove-Item -LiteralPath $destDir -Recurse -Force
    }

    New-Item -ItemType Directory -Path $destDir | Out-Null
    Copy-Item -LiteralPath (Join-Path $sourceDir "*") -Destination $destDir -Recurse -Force
}

function Invoke-ExternalCapture($filePath, $argumentList, $timeoutSeconds) {
    $arguments = @()
    if ($argumentList) {
        $arguments = $argumentList
    }

    $stdoutFile = [System.IO.Path]::GetTempFileName()
    $stderrFile = [System.IO.Path]::GetTempFileName()
    try {
        $proc = Start-Process -FilePath $filePath -ArgumentList $arguments -RedirectStandardOutput $stdoutFile -RedirectStandardError $stderrFile -NoNewWindow -PassThru
        if (-not $proc.WaitForExit($timeoutSeconds * 1000)) {
            try {
                $proc.Kill()
            } catch {
            }

            return [pscustomobject]@{
                ExitCode = -1
                Output   = "Timed out after $timeoutSeconds seconds"
            }
        }

        $stdout = (Get-Content -LiteralPath $stdoutFile -ErrorAction SilentlyContinue | Out-String).Trim()
        $stderr = (Get-Content -LiteralPath $stderrFile -ErrorAction SilentlyContinue | Out-String).Trim()
        $combined = @($stdout, $stderr) | Where-Object { $_ } | Join-String -Separator [Environment]::NewLine

        return [pscustomobject]@{
            ExitCode = $proc.ExitCode
            Output   = $combined
        }
    } finally {
        if (Test-Path $stdoutFile) {
            Remove-Item -LiteralPath $stdoutFile -Force -ErrorAction SilentlyContinue
        }
        if (Test-Path $stderrFile) {
            Remove-Item -LiteralPath $stderrFile -Force -ErrorAction SilentlyContinue
        }
    }
}

$null = Ensure-Command "agentmemory"
$null = Ensure-Command "codex"

$agentmemoryCmd = Get-Command "agentmemory" -ErrorAction Stop
$agentmemoryRoot = Split-Path -Parent $agentmemoryCmd.Source
$bundledSkillsRoot = Join-Path $agentmemoryRoot "node_modules\@agentmemory\agentmemory\plugin\skills"
$codexSkillsRoot = Join-Path $HOME ".codex\skills"

if (-not (Test-Path $bundledSkillsRoot)) {
    throw "Bundled agentmemory skills were not found at: $bundledSkillsRoot"
}

if (-not (Test-Path $codexSkillsRoot)) {
    New-Item -ItemType Directory -Path $codexSkillsRoot | Out-Null
}

$bundledSkillDirs = Get-ChildItem -LiteralPath $bundledSkillsRoot -Directory | Sort-Object Name
$installed = @()

foreach ($skillDir in $bundledSkillDirs) {
    $destination = Join-Path $codexSkillsRoot $skillDir.Name
    Copy-SkillDirectory -sourceDir $skillDir.FullName -destDir $destination
    $installed += $skillDir.Name
}

Write-Info ("Installed agentmemory skills into {0}" -f $codexSkillsRoot)
Write-Info ("Installed: {0}" -f ($installed -join ", "))

try {
    $marketplaceResult = Invoke-ExternalCapture -filePath "codex" -argumentList @("plugin", "marketplace", "add", "rohitg00/agentmemory") -timeoutSeconds 20
    if ($marketplaceResult.ExitCode -eq 0) {
        Write-Info "Added or refreshed Codex plugin marketplace: rohitg00/agentmemory"
        if ($marketplaceResult.Output) {
            Write-Host $marketplaceResult.Output
        }
    } else {
        Write-Info "Codex plugin marketplace add returned a non-zero exit code; continuing because skills were installed locally."
        if ($marketplaceResult.Output) {
            Write-Host $marketplaceResult.Output
        }
    }
} catch {
    Write-Info "Could not add Codex plugin marketplace automatically; continuing with local skill installation."
    Write-Host $_
}

if ($WithHooks) {
    try {
        $hookResult = Invoke-ExternalCapture -filePath "agentmemory" -argumentList @("connect", "codex", "--with-hooks", "--dry-run") -timeoutSeconds 20
        if ($hookResult.ExitCode -eq 0) {
            Write-Info "Refreshed agentmemory Codex hook wiring with --with-hooks."
            if ($hookResult.Output) {
                Write-Host $hookResult.Output
            }
        } else {
            Write-Info "agentmemory connect codex --with-hooks returned a non-zero exit code."
            if ($hookResult.Output) {
                Write-Host $hookResult.Output
            }
        }
    } catch {
        Write-Info "Could not refresh Codex hook wiring automatically."
        Write-Host $_
    }
}
