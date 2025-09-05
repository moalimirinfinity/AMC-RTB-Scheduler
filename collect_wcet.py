import subprocess
import json
import os
import re

# --- Constants ---
SELECTED_BENCHMARKS = {
    "basicmath": ("automotive/basicmath", "basicmath"),
    "qsort": ("automotive/qsort", "qsort_small"),
    "crc": ("telecomm/crc32", "crc"),
}
ITERATIONS = 50
OUTPUT_FILE = "wcet_data.json"

def compile_benchmark(path: str):
    """Compiles a specific benchmark within the MiBench directory."""
    print(f"  Compiling benchmark in '{path}'...")
    try:
        cpu_count = os.cpu_count() or 1
        subprocess.run(
            ["make", f"-j{cpu_count}"],
            cwd=os.path.join("MiBench", path),
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Compilation failed for {path}:\n{e.stderr}")
        raise

def run_and_measure(exec_path: str) -> int:
    """Runs an executable with perf stat and measures the cycle count."""
    print(f"  Running '{exec_path}' for {ITERATIONS} iterations...")
    cycles_data = []
    cycle_pattern = re.compile(r"^\s*([\d,]+)\s+cycles")

    for _ in range(ITERATIONS):
        cmd = ["taskset", "-c", "0", "perf", "stat", "-e", "cycles", exec_path]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        match = cycle_pattern.search(result.stderr)
        if match:
            cycles_str = match.group(1).replace(",", "")
            cycles_data.append(int(cycles_str))

    if not cycles_data:
        print("  ⚠️ No valid cycle data found. Measurement may have failed.")
        return 0

    wcet_cycles = max(cycles_data)
    print(f"  📈 Max cycles (C_LO) found: {wcet_cycles}")
    return wcet_cycles

def main():
    """Main function to orchestrate the WCET data collection."""
    if not os.path.exists("MiBench"):
        print("❌ MiBench directory not found. Please run 'make setup' first.")
        return

    wcet_results = {}
    for name, (path, executable) in SELECTED_BENCHMARKS.items():
        print(f"\nProcessing benchmark: {name}")
        exec_full_path = os.path.join("MiBench", path, executable)
        
        try:
            if not os.path.exists(exec_full_path):
                compile_benchmark(path)
            wcet = run_and_measure(exec_full_path)
            wcet_results[name] = wcet
        except Exception as e:
            print(f"  ❌ Failed to process benchmark {name}: {e}")
            wcet_results[name] = 0

    with open(OUTPUT_FILE, "w") as f:
        json.dump(wcet_results, f, indent=4)
    
    print(f"\n✅ WCET data collection complete. Results saved to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()