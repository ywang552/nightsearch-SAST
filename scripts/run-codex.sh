#!/usr/bin/env bash

set -euo pipefail

log() {
  printf '[run-codex] %s\n' "$*"
}

fail() {
  log "ERROR: $*"
  exit 1
}

workspace_dir="${CODEX_WORKSPACE_DIR:-/workspace}"
dry_run="${CODEX_DRY_RUN:-0}"
task="${CODEX_TASK:-}"
task_file="${CODEX_TASK_FILE:-}"
model="${CODEX_MODEL:-codex-mini-latest}"

if [[ -n "$task_file" ]]; then
  [[ -f "$task_file" ]] || fail "CODEX_TASK_FILE does not exist: $task_file"
  task="$(<"$task_file")"
fi

[[ -n "$task" ]] || fail "Set CODEX_TASK or CODEX_TASK_FILE before starting the container."
[[ -d "$workspace_dir" ]] || fail "CODEX_WORKSPACE_DIR does not exist: $workspace_dir"

cd "$workspace_dir"

default_command='python -m pip install -r requirements.txt && codex exec "$CODEX_TASK"'
command_template="${CODEX_COMMAND:-$default_command}"

if [[ "$dry_run" == "1" || "$dry_run" == "true" ]]; then
  log "Dry run enabled."
  log "Workspace: $workspace_dir"
  log "Model: $model"
  log "Command: $command_template"
  log "Task preview: ${task:0:200}"
  exit 0
fi

[[ -n "${OPENAI_API_KEY:-}" ]] || fail "OPENAI_API_KEY must be set for non-dry-run execution."
[[ -f "requirements.txt" ]] || fail "requirements.txt was not found in $workspace_dir."
command -v codex >/dev/null 2>&1 || fail "The codex CLI is not installed in the container."
command -v python >/dev/null 2>&1 || fail "Python is not installed in the container."

export CODEX_TASK="$task"
export CODEX_MODEL="$model"
export PYTHONPATH="${workspace_dir}/src${PYTHONPATH:+:$PYTHONPATH}"

log "Starting Codex in $workspace_dir"
log "Model: $model"

exec bash -lc "$command_template"
