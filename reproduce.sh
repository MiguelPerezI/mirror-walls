#!/usr/bin/env bash
# Regenerate every number, table and figure of main.tex, in the order of the article (Sections 3-7).
# Each script's stdout goes to results/<script>.txt (several invocations of one script are appended, each
# after a "# <command>" line); figures are rewritten in figures/; per-step times go to results/reproduce_times.txt.
# All runs use fixed seeds, so the results and figures are deterministic (only the GPU timings vary).
#
#   ./reproduce.sh                      full run (about 10 min on a 2026 laptop: 7 min of CPU on one core, 3 min of GPU)
#   QUICK=1 ./reproduce.sh              skip the five longest CPU runs (rule54_exact.py, scan2d.py, strata_seeds.py x3,
#                                       about 1 min each here, longer on slower machines); their results/ files are kept
#   PYTHON=python3.12 PYTHON_GPU=.venv/bin/python ./reproduce.sh
#
# The GPU part (Table 3, strata_gpu.py, and the contca_gpu.py self-test) runs only if CuPy imports in $PYTHON_GPU.
# At the end code/check_results.py compares every number quoted in main.tex with the results and prints PASS/FAIL.
set -euo pipefail
PYTHON=${PYTHON:-python3}
PYTHON_GPU=${PYTHON_GPU:-python3}
QUICK=${QUICK:-0}
# a relative interpreter path (e.g. .venv/bin/python) is taken from the current directory, before cd code/
abs() { case "$1" in */*) (cd "$(dirname "$1")" 2>/dev/null && echo "$(pwd)/$(basename "$1")") || echo "$1" ;; *) echo "$1" ;; esac; }
PYTHON=$(abs "$PYTHON"); PYTHON_GPU=$(abs "$PYTHON_GPU")
ROOT=$(cd "$(dirname "$0")" && pwd)
RES="$ROOT/results"
mkdir -p "$RES"
cd "$ROOT/code"
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 LC_ALL=C
TIMES="$RES/reproduce_times.txt"
now() { "$PYTHON" -c "import time; print(time.time())"; }
T_ALL=$(now)
SEEN=" "
{
  echo "# reproduce.sh started $(date '+%Y-%m-%d %H:%M:%S %z'), QUICK=$QUICK"
  echo "# $("$PYTHON" -c 'import sys, platform, numpy; print("PYTHON:", platform.python_implementation(), sys.version.split()[0], "numpy", numpy.__version__)')"
} > "$TIMES"
cat "$TIMES"

# run <py> <long:0|1> <script.py> [args...]: stdout -> results/<script>.txt, elapsed time printed and logged
run() {
  local py=$1 long=$2; shift 2
  local script=$1 name=${1%.py} cmd="$*"
  if [[ "$QUICK" == 1 && "$long" == 1 ]]; then
    echo "[skipped, QUICK=1] $cmd   (keeping results/$name.txt)" | tee -a "$TIMES"; return 0
  fi
  local out="$RES/$name.txt"
  if [[ "$SEEN" != *" $name "* ]]; then : > "$out"; SEEN="$SEEN$name "; fi
  echo "# $cmd" >> "$out"
  echo ">>> $cmd"
  local t0; t0=$(now)
  if ! "$py" "$@" >> "$out"; then echo "FAILED: $cmd (see results/$name.txt)"; exit 1; fi
  awk -v a="$t0" -v b="$(now)" -v c="$cmd" 'BEGIN { printf "    %8.1f s  %s\n", b - a, c }' | tee -a "$TIMES"
}

echo "== Section 3: reflection principle"
run "$PYTHON" 0 reflection_principle.py

echo "== Section 4: continuous automaton in one dimension (Figure 1)"
run "$PYTHON" 0 view1d.py 0.398 300 600
run "$PYTHON" 0 png2pdf.py ../figures/class4_1d_a0.398_periodic.png ../figures/class4_1d_a0.398_mirror.png ../figures/class4_1d_wallzoom.png
run "$PYTHON" 0 catalogue2.py
run "$PYTHON" 0 slowclass2.py
run "$PYTHON" 0 perstep.py
run "$PYTHON" 0 population.py
run "$PYTHON" 0 wall1d.py

echo "== Section 5: rule 54 (Table 1, Figures 2 and 3)"
run "$PYTHON" 1 rule54_exact.py 10          # also writes code/rule54_examples.npy for fig_rule54.py
run "$PYTHON" 0 rule54_phases.py
run "$PYTHON" 0 rule54_sparse.py            # also writes code/rule54_sparse.npz for fig_rule54.py
run "$PYTHON" 0 fig_rule54.py
run "$PYTHON" 0 rule54_charge.py

echo "== Section 6: rule 110 (Figure 4)"
run "$PYTHON" 0 rule110_ether.py
run "$PYTHON" 0 fig_rule110.py
run "$PYTHON" 0 eca_box.py

echo "== Section 7: two and three dimensions (Table 2, Figures 5 and 6)"
run "$PYTHON" 1 scan2d.py
run "$PYTHON" 0 cuts2d.py
run "$PYTHON" 0 png2pdf.py ../figures/cuts2d_spacetime.png
run "$PYTHON" 0 filmstrip2d.py 0.33
run "$PYTHON" 0 filmstrip2d.py 0.49
run "$PYTHON" 0 png2pdf.py ../figures/filmstrip2d_a0.33.png ../figures/filmstrip2d_a0.49.png
for a in 0.398 0.49 0.33; do
  run "$PYTHON" 1 strata_seeds.py "$a" 128 1500 32 800 8
done

echo "== Section 7, GPU: Table 3 and the larger boxes quoted in the text"
if "$PYTHON_GPU" -c "import cupy; assert cupy.cuda.runtime.getDeviceCount() > 0" >/dev/null 2>&1; then
  echo "# $("$PYTHON_GPU" -c 'import sys, platform, numpy, cupy; print("PYTHON_GPU:", platform.python_implementation(), sys.version.split()[0], "numpy", numpy.__version__, "cupy", cupy.__version__, cupy.cuda.runtime.getDeviceProperties(0)["name"].decode())')" | tee -a "$TIMES"
  run "$PYTHON_GPU" 0 contca_gpu.py                                   # self-test: bit-identical to contca.py
  for a in 0.398 0.49 0.33; do
    run "$PYTHON_GPU" 0 strata_gpu.py "$a" 1024 3000 128 1500 16     # Table 3
  done
  run "$PYTHON_GPU" 0 strata_gpu.py 0.33 256 3000 64 1500 16          # a = 0.33: codim 0 on 256^2, 3-D rule on 64^3
  run "$PYTHON_GPU" 0 strata_gpu.py 0.33 512 3000 96 1500 16          # a = 0.33: codim 0 on 512^2, 3-D rule on 96^3
  run "$PYTHON_GPU" 0 strata_gpu.py 0.33 1024 3000 0 0 16 40          # a = 0.33: profile to distance 39 on 1024^2
else
  echo "CuPy does not import in PYTHON_GPU=$PYTHON_GPU (or no GPU): GPU part skipped (results/strata_gpu.txt, results/contca_gpu.txt kept)" | tee -a "$TIMES"
fi

awk -v a="$T_ALL" -v b="$(now)" 'BEGIN { printf "total %.1f s\n", b - a }' | tee -a "$TIMES"
echo "== check: every number quoted in main.tex against results/"
"$PYTHON" check_results.py
