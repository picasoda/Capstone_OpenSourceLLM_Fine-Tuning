@echo off
cd /d %~dp0

echo [1/3] Ollama 서버 시작...
start "Ollama" cmd /k "ollama serve"
timeout /t 3 /nobreak > nul

echo [2/3] FastAPI 서버 시작...
start "FastAPI" cmd /k "llm_env\Scripts\activate.bat && cd Chatbot && python src/server.py"
timeout /t 3 /nobreak > nul

echo [3/3] ngrok 시작...
start "ngrok" cmd /k "ngrok http --domain=bullring-reactive-ensure.ngrok-free.dev 8000"

echo.
echo 완료: https://bullring-reactive-ensure.ngrok-free.dev
pause
