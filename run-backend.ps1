# Start the backend using the virtual environment Python to avoid blocked uvicorn.exe
Set-Location -Path $PSScriptRoot
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
