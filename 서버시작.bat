@echo off
cd /d %~dp0

start "Ollama" cmd /k "ollama serve"
timeout /t 3 /nobreak > nul

start "FastAPI" cmd /k "llm_env\Scripts\activate.bat && cd Chatbot && python src/server.py"
timeout /t 3 /nobreak > nul

start "ngrok" cmd /k "ngrok http --domain=bullring-reactive-ensure.ngrok-free.dev 8000"

echo Done: https://bullring-reactive-ensure.ngrok-free.dev
pause
