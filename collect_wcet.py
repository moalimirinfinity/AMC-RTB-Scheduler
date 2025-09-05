import subprocess
import json
import os
import re
import sys

# --- Constants ---
# Corrected the path for 'crc' to 'telecomm/CRC32' (case-sensitive).
SELECTED_BENCHMARKS = {
    "basicmath": ("automotive/basicmath", "basicmath_small", None),
    "qsort": ("automotive/qsort", "qsort_small", "input_small.dat"),
    "crc": ("telecomm/CRC32", "crc", "small.pcm"),  # Verified correct case-sensitive path
}
ITERATIONS = 50
OUTPUT_FILE = "wcet_data.json"

def compile_benchmark(path: str):
    """Compiles a specific benchmark within the mibench directory."""
    full_path = os.path.join("mibench", path)
    if not os.path.isdir(full_path):
        raise FileNotFoundError(f"Directory does not exist: {full_path}")
    
    print(f"  Compiling benchmark in '{path}'...")
    try:
        subprocess.run(
            ["make"],
            cwd=full_path,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        if e.returncode != 0:
            print(f"  ❌ Compilation failed for {path}:\n{e.stderr}")
            raise

def run_and_measure(exec_path: str, input_file: str | None) -> int:
    """Runs an executable with perf stat and measures the cycle count."""
    print(f"  Running '{os.path.basename(exec_path)}' for {ITERATIONS} iterations...")
    cycles_data = []
    cycle_pattern = re.compile(r"^\s*([\d,]+)\s+cycles", re.MULTILINE)

    for i in range(ITERATIONS):
        cmd = ["sudo", "taskset", "-c", "0", "perf", "stat", "-e", "cycles", exec_path]
        
        if input_file:
            input_file_path = os.path.join(os.path.dirname(exec_path), input_file)
            if not os.path.exists(input_file_path):
                raise FileNotFoundError(f"Input file not found: {input_file_path}")
            cmd.append(input_file_path)

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            match = cycle_pattern.search(result.stderr)
            if match:
                cycles_str = match.group(1).replace(",", "")
                cycles_data.append(int(cycles_str))
        except subprocess.CalledProcessError as e:
            print(f"\n  ❌ ERROR: perf command failed on iteration {i+1} for {exec_path}.")
            print(f"  You may need to install perf: 'sudo apt-get install linux-tools-$(uname -r)'")
            print(f"  Stderr: {e.stderr}")
            raise

    if not cycles_data:
        print(f"  ⚠️ No valid cycle data found for '{os.path.basename(exec_path)}'. This can happen if the benchmark runs too quickly.")
        return 0

    wcet_cycles = max(cycles_data)
    print(f"  📈 Max cycles (C_LO) found: {wcet_cycles}")
    return wcet_cycles

def main():
    """Main function to orchestrate the WCET data collection."""
    if not os.path.exists("mibench"):
        print("❌ mibench directory not found. Please run 'make setup' first.")
        return

    wcet_results = {}
    try:
        for name, (path, executable, input_file) in SELECTED_BENCHMARKS.items():
            print(f"\nProcessing benchmark: {name}")
            exec_full_path = os.path.join("mibench", path, executable)
            
            compile_benchmark(path)

            if not os.path.exists(exec_full_path):
                raise FileNotFoundError(f"Executable for benchmark '{name}' not found at '{exec_full_path}' after compiling.")

            wcet = run_and_measure(exec_full_path, input_file)
            wcet_results[name] = wcet

    except (subprocess.CalledProcessError, FileNotFoundError, KeyboardInterrupt) as e:
        print(f"\n❌ A critical error occurred: {e}")
        print("   Aborting WCET data collection. No output file will be generated.")
        sys.exit(1)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(wcet_results, f, indent=4)
    
    print(f"\n✅ WCET data collection complete. Results saved to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()