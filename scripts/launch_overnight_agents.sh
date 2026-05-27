#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/thom/Desktop/IA colombia/secop-risk-alerts-co"
PROMPT="$ROOT/docs/agent_handoffs/overnight_repo_finish_prompt.md"
RUN_DIR="/tmp/secop-risk-alerts-co-agent-runs/$(date +%Y%m%d-%H%M%S)"

mkdir -p "$RUN_DIR"

if [[ ! -f "$PROMPT" ]]; then
  echo "Missing prompt: $PROMPT" >&2
  exit 1
fi

cd "$ROOT"

MESSAGE="Read and execute the full overnight orchestration prompt at: $PROMPT. It begins with /goal and gives you up to 8 hours. Treat yourself as an orchestrator, use subagents/specialists when available, work against the repository at $ROOT, and leave a final report under docs/agent_handoffs/."

nohup hermes chat \
  --query "$MESSAGE" \
  --max-turns 500 \
  --worktree \
  --accept-hooks \
  --checkpoints \
  --yolo \
  --source overnight-secop \
  > "$RUN_DIR/hermes.log" 2>&1 &
echo "$!" > "$RUN_DIR/hermes.pid"

nohup openclaw agent \
  --local \
  --agent ops \
  --timeout 28800 \
  --thinking max \
  --message "$MESSAGE" \
  --json \
  > "$RUN_DIR/openclaw.log" 2>&1 &
echo "$!" > "$RUN_DIR/openclaw.pid"

cat > "$RUN_DIR/README.txt" <<EOF
Overnight agent run for secop-risk-alerts-co

Prompt: $PROMPT
Hermes log: $RUN_DIR/hermes.log
Hermes pid: $(cat "$RUN_DIR/hermes.pid")
OpenClaw log: $RUN_DIR/openclaw.log
OpenClaw pid: $(cat "$RUN_DIR/openclaw.pid")

Tail commands:
tail -f "$RUN_DIR/hermes.log"
tail -f "$RUN_DIR/openclaw.log"
EOF

echo "$RUN_DIR"
