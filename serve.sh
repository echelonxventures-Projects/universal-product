#!/bin/bash
# LUXORA Platform - persistent launcher (auto-restarts the server if it ever exits)
cd "$(dirname "$0")"
PORT="${PORT:-8787}"
if [ -f .luxora.pid ] && kill -0 "$(cat .luxora.pid)" 2>/dev/null; then
  echo "✓ LUXORA already running (supervisor pid $(cat .luxora.pid)) on http://localhost:${PORT}"
  exit 0
fi
export PORT
nohup bash -c 'while true; do node server.js; echo "[luxora] server exited — restarting in 2s"; sleep 2; done' >> /tmp/luxora.log 2>&1 &
echo $! > .luxora.pid
sleep 2
if curl -s -m 3 "http://localhost:${PORT}/healthz" > /dev/null; then
  echo "✓ LUXORA Platform live (supervisor pid $(cat .luxora.pid), auto-restart on)"
else
  echo "✗ not answering yet — check /tmp/luxora.log"
fi
