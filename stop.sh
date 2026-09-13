#!/bin/bash
# LUXORA Platform - stop the supervisor and server
cd "$(dirname "$0")"
if [ -f .luxora.pid ]; then
  SUP=$(cat .luxora.pid)
  pkill -P "$SUP" -f "node server.js" 2>/dev/null
  kill "$SUP" 2>/dev/null
  rm -f .luxora.pid
  echo "✓ LUXORA stopped"
else
  pkill -f "node server.js" && echo "✓ stopped loose server processes" || echo "nothing running"
fi
