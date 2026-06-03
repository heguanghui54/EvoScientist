#!/usr/bin/env bash
set -euo pipefail

# Sync this checkout to the Ubuntu GPU host and run a reproduction command.
#
# Examples:
#   reproduction/ssh_ubuntu_run.sh setup
#   reproduction/ssh_ubuntu_run.sh preflight
#   reproduction/ssh_ubuntu_run.sh query 1
#   reproduction/ssh_ubuntu_run.sh query-bg 1
#   reproduction/ssh_ubuntu_run.sh batch-bg 30
#   reproduction/ssh_ubuntu_run.sh status
#   reproduction/ssh_ubuntu_run.sh fetch
#   reproduction/ssh_ubuntu_run.sh audit

HOST="${EVOSCI_SSH_HOST:-ubuntu-heshi}"
REMOTE_DIR="${EVOSCI_REMOTE_DIR:-~/research/EvoScientist-repro}"
QUERY_EXTRA_ARGS="${EVOSCI_QUERY_EXTRA_ARGS:-}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

remote() {
  ssh -o BatchMode=yes "$HOST" "$@"
}

sync_repo() {
  rsync -az --delete \
    --exclude '.git/' \
    --exclude '.venv/' \
    --exclude '__pycache__/' \
    --exclude '.pytest_cache/' \
    --exclude 'EvoScientist.egg-info/' \
    --exclude 'reproduction/artifacts/' \
    "$ROOT/" "$HOST:$REMOTE_DIR/"
}

run_remote() {
  local cmd="$1"
  remote "bash -lc 'set -euo pipefail; cd $REMOTE_DIR; source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || true; source ~/.codex/env 2>/dev/null || true; $cmd'"
}

case "${1:-}" in
  setup)
    remote "mkdir -p $REMOTE_DIR"
    sync_repo
    run_remote "bash reproduction/setup_ubuntu_gpu.sh"
    ;;
  preflight)
    sync_repo
    run_remote "conda activate \${EVOSCI_CONDA_ENV:-evoscientist-repro}; bash reproduction/run_preflight.sh --with-agent"
    ;;
  query)
    qid="${2:-1}"
    sync_repo
    run_remote "conda activate \${EVOSCI_CONDA_ENV:-evoscientist-repro}; python reproduction/run_idea_generation.py --query-id $qid --timeout \${EVOSCI_QUERY_TIMEOUT:-1800} $QUERY_EXTRA_ARGS"
    ;;
  query-bg)
    qid="${2:-1}"
    sync_repo
    run_remote "mkdir -p reproduction/artifacts/remote_jobs; conda activate \${EVOSCI_CONDA_ENV:-evoscientist-repro}; nohup python reproduction/run_idea_generation.py --query-id $qid --timeout \${EVOSCI_QUERY_TIMEOUT:-1800} $QUERY_EXTRA_ARGS > reproduction/artifacts/remote_jobs/query_${qid}.log 2>&1 & echo \$! > reproduction/artifacts/remote_jobs/query_${qid}.pid; echo started query_${qid} pid=\$(cat reproduction/artifacts/remote_jobs/query_${qid}.pid)"
    ;;
  batch-bg)
    limit="${2:-30}"
    sync_repo
    run_remote "mkdir -p reproduction/artifacts/remote_jobs; conda activate \${EVOSCI_CONDA_ENV:-evoscientist-repro}; nohup python reproduction/run_idea_generation.py --limit $limit --timeout \${EVOSCI_QUERY_TIMEOUT:-1800} $QUERY_EXTRA_ARGS > reproduction/artifacts/remote_jobs/batch_${limit}.log 2>&1 & echo \$! > reproduction/artifacts/remote_jobs/batch_${limit}.pid; echo started batch_${limit} pid=\$(cat reproduction/artifacts/remote_jobs/batch_${limit}.pid)"
    ;;
  status)
    run_remote "if [ -d reproduction/artifacts/remote_jobs ]; then for pidfile in reproduction/artifacts/remote_jobs/*.pid; do [ -f \"\$pidfile\" ] || continue; pid=\$(cat \"\$pidfile\"); name=\$(basename \"\$pidfile\" .pid); if ps -p \"\$pid\" >/dev/null 2>&1; then echo \"\$name RUNNING pid=\$pid\"; else echo \"\$name EXITED pid=\$pid\"; fi; logfile=\"reproduction/artifacts/remote_jobs/\$name.log\"; [ -f \"\$logfile\" ] && { echo \"--- remote job log: \$logfile\"; tail -20 \"\$logfile\"; }; if [[ \"\$name\" =~ ^query_([0-9]+)\$ ]]; then qid=\"\${BASH_REMATCH[1]}\"; for outdir in reproduction/artifacts/idea_outputs/EvoScientist/query_\$(printf '%02d' \"\$qid\") reproduction/artifacts/idea_generation/query_\$(printf '%02d' \"\$qid\"); do [ -d \"\$outdir\" ] || continue; for stream in stdout.txt stderr.txt; do stream_path=\"\$outdir/\$stream\"; [ -f \"\$stream_path\" ] && { echo \"--- \$stream_path\"; tail -20 \"\$stream_path\"; }; done; done; fi; done; count=\$(find reproduction/artifacts/idea_outputs/EvoScientist -maxdepth 1 -type d -name \"query_*\" 2>/dev/null | wc -l | tr -d \" \"); echo \"idea_outputs_query_dirs=\$count\"; latest=\$(find reproduction/artifacts/idea_outputs/EvoScientist -maxdepth 1 -type d -name \"query_*\" 2>/dev/null | sort | tail -1); if [ -n \"\$latest\" ]; then echo \"latest_query_dir=\$latest\"; for stream in stdout.txt stderr.txt; do stream_path=\"\$latest/\$stream\"; [ -f \"\$stream_path\" ] && { echo \"--- latest \$stream_path\"; tail -20 \"\$stream_path\"; }; done; fi; else echo no remote_jobs directory; fi"
    ;;
  fetch)
    mkdir -p "$ROOT/reproduction/artifacts/remote_fetch"
    rsync -az "$HOST:$REMOTE_DIR/reproduction/artifacts/" "$ROOT/reproduction/artifacts/remote_fetch/"
    echo "fetched to $ROOT/reproduction/artifacts/remote_fetch"
    ;;
  audit)
    sync_repo
    run_remote "conda activate \${EVOSCI_CONDA_ENV:-evoscientist-repro}; python reproduction/audit_reproduction_artifacts.py"
    ;;
  shell)
    remote -t "cd $REMOTE_DIR; exec bash -l"
    ;;
  *)
    cat <<'USAGE'
Usage:
  reproduction/ssh_ubuntu_run.sh setup
  reproduction/ssh_ubuntu_run.sh preflight
  reproduction/ssh_ubuntu_run.sh query [query_id]
  reproduction/ssh_ubuntu_run.sh query-bg [query_id]
  reproduction/ssh_ubuntu_run.sh batch-bg [limit]
  reproduction/ssh_ubuntu_run.sh status
  reproduction/ssh_ubuntu_run.sh fetch
  reproduction/ssh_ubuntu_run.sh audit
  reproduction/ssh_ubuntu_run.sh shell

Environment overrides:
  EVOSCI_SSH_HOST=ubuntu-heshi
  EVOSCI_REMOTE_DIR=~/research/EvoScientist-repro
  EVOSCI_CONDA_ENV=evoscientist-repro
  EVOSCI_QUERY_TIMEOUT=1800
  EVOSCI_QUERY_EXTRA_ARGS="--proposal-only --stream-logs"
USAGE
    exit 2
    ;;
esac
