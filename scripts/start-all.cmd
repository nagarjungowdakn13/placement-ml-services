@echo off
setlocal

REM Root of the repo (folder above /scripts)
set "ROOT=%~dp0.."

REM Optional: activate shared Python venv if it exists
if exist "%ROOT%\venv\Scripts\activate.bat" (
	call "%ROOT%\venv\Scripts\activate.bat"
)

REM Start Resume NLP (8001) - force pdfminer to avoid glyph loss (e.g., missing 'u')
start "resume-nlp" cmd /k "cd /d %ROOT%\ml-service\resume-nlp && if exist ..\..\venv\Scripts\activate.bat call ..\..\venv\Scripts\activate.bat && set PDF_EXTRACTOR=pdfminer && pip install -r requirements.txt && python -m uvicorn main:app --host 0.0.0.0 --port 8001"

REM Start Collaborative Filter (8002)
start "collab-filter" cmd /k "cd /d %ROOT%\ml-service\collaborative-filter && if exist ..\..\venv\Scripts\activate.bat call ..\..\venv\Scripts\activate.bat && pip install -r requirements.txt && python -m uvicorn main:app --host 0.0.0.0 --port 8002"

REM Start Placement Predict (8003)
start "placement-predict" cmd /k "cd /d %ROOT%\ml-service\placement-predict && if exist ..\..\venv\Scripts\activate.bat call ..\..\venv\Scripts\activate.bat && pip install -r requirements.txt && python -m uvicorn main:app --host 0.0.0.0 --port 8003"

REM Start Backend (5000)
start "backend" cmd /k "cd /d %ROOT%\backend && npm install && npm run dev"

REM Start Frontend (3000)
start "frontend" cmd /k "cd /d %ROOT%\frontend && npm install && npm run dev"

echo Services are starting in separate windows.
endlocal
