#!/bin/bash
# run_app.sh — Kill ports and start FastAPI + Vite
# Run with: bash run_app.sh  (requires Git Bash on Windows)

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "🔪 Killing processes on ports 8000 and 5173..."
cmd.exe /c "for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %a" 2>/dev/null
cmd.exe /c "for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :5173') do taskkill /F /PID %a" 2>/dev/null
echo "✅ Ports cleared"

# Load .env
if [ -f "$ROOT/.env" ]; then
  export $(grep -v '^#' "$ROOT/.env" | xargs)
  echo "✅ Loaded .env"
fi

echo ""
echo "🚀 Starting FastAPI backend on http://127.0.0.1:8000 ..."
cd "$ROOT"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

echo "🚀 Starting Vite frontend on http://localhost:5173 ..."
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers are running!"
echo "   Frontend → http://localhost:5173"
echo "   Backend  → http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop both servers."

# Wait and clean up on Ctrl+C
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
wait
