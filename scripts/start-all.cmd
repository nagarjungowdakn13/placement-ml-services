@echo off
setlocal

REM Start Resume NLP (8001)
start "resume-nlp" cmd /k "cd /d %~dp0..\ml-service\resume-nlp && pip install -r requirements.txt && python -m uvicorn main:app --host 0.0.0.0 --port 8001"

REM Start Collaborative Filter (8002)
start "collab-filter" cmd /k "cd /d %~dp0..\ml-service\collaborative-filter && pip install -r requirements.txt && python -m uvicorn main:app --host 0.0.0.0 --port 8002"

REM Start Placement Predict (8003)
start "placement-predict" cmd /k "cd /d %~dp0..\ml-service\placement-predict && pip install -r requirements.txt && python -m uvicorn main:app --host 0.0.0.0 --port 8003"

REM Start Backend (5000)
start "backend" cmd /k "cd /d %~dp0..\backend && npm install && npm run dev"

REM Start Frontend (3000)
start "frontend" cmd /k "cd /d %~dp0..\frontend && npm install && npm run dev"

echo Services are starting in separate windows.
endlocal