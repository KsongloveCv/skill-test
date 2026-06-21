#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
PORT="${PORT:-8080}"
URL="http://127.0.0.1:${PORT}"

echo "月夜狼人杀 → ${URL}"
echo "按 Ctrl+C 停止服务"

if command -v open >/dev/null 2>&1; then
  (sleep 0.5 && open "${URL}") &
fi

python3 -m http.server "${PORT}"
