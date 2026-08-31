param(
    [Parameter(Position = 0)]
    [string]$Command = "help"
)

$ProjectRoot = "D:\engineering-data-query-system"

Set-Location $ProjectRoot

if ($Command -eq "generate") {
    python scripts\generate_data.py
}
elseif ($Command -eq "benchmark") {
    python scripts\run_benchmarks.py
}
elseif ($Command -eq "tree") {
    tree /F
}
else {
    Write-Host ""
    Write-Host "Engineering Data Query System"
    Write-Host ""
    Write-Host "Available commands:"
    Write-Host ""
    Write-Host ".\run.ps1 generate"
    Write-Host ".\run.ps1 benchmark"
    Write-Host ".\run.ps1 tree"
    Write-Host ""
}
