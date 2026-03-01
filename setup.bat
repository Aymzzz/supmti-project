@echo off
echo =========================================================
echo       SupMTI Intelligent Chatbot - Windows Setup
echo =========================================================
echo.

:: 1. Setup Backend (Python)
echo [1/4] Setting up Python Backend...
cd backend

:: Create a virtual environment if it doesn't exist
if not exist "venv\" (
    echo [Info] Creating Python virtual environment (venv)...
    python -m venv venv
)

:: Copy .env.example to .env if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        echo [Info] Copying .env.example to .env...
        copy .env.example .env
    )
)

:: Install requirements using the venv explicitly
echo [Info] Installing backend dependencies (this might take a minute)...
venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\pip install -r requirements.txt

:: Run the database ingest script
echo [Info] Ingesting Mock Knowledge Base into ChromaDB...
venv\Scripts\python -m scripts.ingest

:: Go back to root
cd ..
echo.

:: 2. Setup Frontend (Node.js)
echo [2/4] Setting up Next.js Frontend...
cd frontend

:: Install npm packages if node_modules is missing
if not exist "node_modules\" (
    echo [Info] Installing frontend Node modules...
    call npm install
)

:: Go back to root
cd ..
echo.

:: 3. Launch Servers
echo [3/4] Launching Servers...
echo [Info] Starting FastAPI Backend on Port 8000 in a new window...
start "SupMTI Backend Server" cmd /k "cd backend && venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [Info] Starting Next.js Frontend on Port 3000 in a new window...
start "SupMTI Frontend Server" cmd /k "cd frontend && npm run dev"

:: 4. Finish
echo.
echo =========================================================
echo [4/4] Success! The SupMTI Chatbot is now running.
echo =========================================================
echo.
echo The Frontend will be available at: http://localhost:3000
echo The Backend docs are available at: http://localhost:8000/docs
echo.
echo Important: To stop the servers, just close the 2 new command windows that opened!
echo.
pause
