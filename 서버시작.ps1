$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "[1/3] Ollama 시작..."
$p1 = Start-Process ollama -ArgumentList "serve" -PassThru -WindowStyle Hidden

Start-Sleep 3

Write-Host "[2/3] FastAPI 시작..."
$python = "$root\llm_env\Scripts\python.exe"
$p2 = Start-Process $python -ArgumentList "src/server.py" -WorkingDirectory "$root\Chatbot" -PassThru -WindowStyle Hidden

Start-Sleep 3

Write-Host "[3/3] ngrok 시작..."
$p3 = Start-Process ngrok -ArgumentList "http --domain=bullring-reactive-ensure.ngrok-free.dev 8000" -PassThru -WindowStyle Hidden

Write-Host ""
Write-Host "실행 중: https://bullring-reactive-ensure.ngrok-free.dev"
Write-Host "종료하려면 Ctrl+C"

try {
    while ($true) { Start-Sleep 1 }
} finally {
    Write-Host "`n종료 중..."
    $p1, $p2, $p3 | ForEach-Object { if ($_) { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue } }
    Write-Host "완료"
}