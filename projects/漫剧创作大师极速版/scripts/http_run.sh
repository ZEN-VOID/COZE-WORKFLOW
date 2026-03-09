#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${COZE_WORKSPACE_PATH:-$(dirname "$SCRIPT_DIR")}"
PORT=8000

usage() {
  echo "用法: $0 -p <端口>"
}

while getopts "p:h" opt; do
  case "$opt" in
    p)
      PORT="$OPTARG"
      ;;
    h)
      usage
      exit 0
      ;;
    \?)
      echo "无效选项: -$OPTARG"
      usage
      exit 1
      ;;
  esac
done

if [ -f "${SCRIPT_DIR}/load_env.sh" ]; then
  echo "Loading environment variables..."
  source "${SCRIPT_DIR}/load_env.sh"
fi

python "${SCRIPT_DIR}/validate_config.py" --quiet
python ${WORK_DIR}/src/main.py -m http -p $PORT
