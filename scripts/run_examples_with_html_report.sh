#!/usr/bin/env bash
# Run the pipeline for each of the 4 checked-in examples, then generate the
# unified --html-report for each resulting taxonomy. Useful as a network
# smoke test for in-graph changes (e.g. the evaluate_taxonomy wiring on
# feat/taxonomy-evaluation-feedback-integration) since it exercises a full
# real run end to end, not just the graph-compile check.
#
# Usage:
#   scripts/run_examples_with_html_report.sh [example-name ...]
#
# With no arguments, runs all 4 examples. Pass one or more of:
#   campus-bike cursor-git-at-scale das-p1-2023 pharmacy-food
# to run a subset.
#
# Requires the `taxonomy` conda environment and provider API keys already
# configured (same requirements as running main.py directly).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! python -c "import taxonomy_generator" >/dev/null 2>&1; then
  echo "error: 'taxonomy_generator' is not importable in the current Python environment." >&2
  echo "       Activate the project environment first, e.g.: conda activate taxonomy" >&2
  exit 1
fi

# name:corpus:config
EXAMPLES=(
  "campus-bike:examples/campus-bike/campus_bike_architecture_decisions.json:examples/campus-bike/campus_bike_config.yaml"
  "cursor-git-at-scale:examples/cursor-git-at-scale/cursor_git_at_scale_documents.json:examples/cursor-git-at-scale/git_at_scale_config.yaml"
  "das-p1-2023:examples/das-p1-2023/das-p1-2023_architecture_decisions.json:examples/das-p1-2023/das-p1-2023_config.yaml"
  "pharmacy-food:examples/pharmacy-food/pharmacy_food_architecture_decisions.json:examples/pharmacy-food/pharmacy_food_config.yaml"
)

REQUESTED=("$@")

run_one() {
  local name="$1" corpus="$2" config="$3"
  local out_dir="examples/${name}"
  local log_file="${out_dir}/${name}_run_$(date +%Y%m%d_%H%M%S).log"

  echo "=== ${name}: running pipeline ==="
  echo "    corpus: ${corpus}"
  echo "    config: ${config}"
  echo "    log:    ${log_file}"

  python main.py \
    --corpus "${corpus}" \
    --config "${config}" \
    --output "${out_dir}/" \
    2>&1 | tee "${log_file}"

  local taxonomy_path
  taxonomy_path="$(grep -o 'Taxonomy saved to: .*' "${log_file}" | tail -1 | sed 's/^Taxonomy saved to: //')"

  if [ -z "${taxonomy_path}" ]; then
    echo "!!! ${name}: could not find a saved taxonomy path in ${log_file} — skipping html-report" >&2
    return 1
  fi

  echo "=== ${name}: generating extended HTML report ==="
  echo "    taxonomy: ${taxonomy_path}"

  python main.py --html-report "${taxonomy_path}" --output "${out_dir}/"

  echo "=== ${name}: done ==="
  echo
}

FAILED=()

if [ "${#REQUESTED[@]}" -eq 0 ]; then
  TO_RUN=("${EXAMPLES[@]}")
else
  TO_RUN=()
  for wanted in "${REQUESTED[@]}"; do
    found=""
    for entry in "${EXAMPLES[@]}"; do
      if [ "${entry%%:*}" = "$wanted" ]; then
        found="$entry"
        break
      fi
    done
    if [ -z "$found" ]; then
      echo "Unknown example: ${wanted}" >&2
      exit 1
    fi
    TO_RUN+=("$found")
  done
fi

for entry in "${TO_RUN[@]}"; do
  IFS=":" read -r name corpus config <<< "$entry"
  if ! run_one "$name" "$corpus" "$config"; then
    FAILED+=("$name")
  fi
done

echo "======================================"
if [ "${#FAILED[@]}" -eq 0 ]; then
  echo "All examples completed successfully."
else
  echo "Completed with failures: ${FAILED[*]}" >&2
  exit 1
fi
