# AMC-RTB Scheduler — Analysis & Simulation


This repository provides a complete workflow for the analysis and simulation of the **Adaptive Mixed-Criticality with Response-Time Bound (AMC-RTB)** scheduling algorithm, in the embedded systems course. The project is designed to be fully reproducible and automated. It starts by measuring real-world execution times from the **MiBench benchmark suite**, synthesizes a mixed-criticality periodic task set, performs a formal response-time analysis based on established academic research, and finally, runs discrete-event simulations to visualize the scheduler's behavior in both LO- and HI-criticality modes.

The theoretical foundation for the analysis is based on the paper: *S.K. Baruah, A. Burns, and R.I. Davis, "Response-Time Analysis for Mixed Criticality Systems," RTSS, 2011.* [cite: 2, 3, 4, 5, 6, 7, 8]

---

## Features

* **Automated Workflow**: A `Makefile` automates the entire process from setup to simulation.
* **Empirical WCET Collection**: Uses the `perf` tool on Linux to collect realistic Worst-Case Execution Time (WCET) data from MiBench benchmarks.
* **Task Set Synthesis**: Generates a randomized, mixed-criticality sporadic task set with varying periods and priorities based on the collected WCET data.
* **Formal Schedulability Analysis**: Implements the response-time analysis for three critical scenarios:
    1.  [cite_start]**LO-Mode Schedulability** (Eq. 4 in the paper) [cite: 187]
    2.  [cite_start]**Stable HI-Mode Schedulability** (Eq. 5 in the paper) [cite: 190]
    3.  [cite_start]**LO-to-HI Transition Schedulability (AMC-rtb)** (Eq. 7 in the paper) [cite: 223, 224]
* **Discrete-Event Simulator**: A custom simulator visualizes the scheduler's runtime behavior, including job releases, preemptions, completions, and the critical mode-switch mechanism.
* **Reproducibility**: The entire environment and dependencies are managed through a setup script and a `requirements.txt` file, ensuring the project runs consistently.

---

##  How It Works

The project follows a three-stage pipeline, managed by the `Makefile`.

### 1. Setup (`make setup`)

This command prepares the environment for the project.
* Installs necessary system packages like `git`, `build-essential`, and `linux-tools` using `apt-get`.
* Clones the [mibench repository](https://github.com/embecosm/mibench) if it's not already present.
* Creates a Python virtual environment (`venv`) and installs the required `pandas` library.

### 2. Data Collection & Task Generation (`make data`)

This stage gathers empirical data and uses it to create a scheduling problem.
* **`collect_wcet.py`**: Compiles and runs selected MiBench benchmarks (`basicmath`, `qsort`, `crc`). It executes each benchmark multiple times, using `perf stat` to measure CPU cycles. The maximum observed value is saved as the task's `wcet_lo` in `wcet_data.json`.
* **`generate_taskset.py`**: Reads `wcet_data.json` and synthesizes a task set. It randomly assigns criticality levels (HI/LO), calculates periods and deadlines, and determines an additional `wcet_hi` for HI-criticality tasks. Priorities are assigned using **Deadline Monotonic Priority Ordering (DMPO)**. The final set is saved to `task_set.json`.

### 3. Analysis & Simulation (`make run`)

This is the final stage where the task set is analyzed and simulated.
* **`main.py`**: The main script orchestrates this stage.
    * **Theoretical Analysis**: It first loads `task_set.json` and calls the analysis functions in `src/analysis.py`. It verifies schedulability in LO-mode, stable HI-mode, and during the critical transition. If the task set is proven unschedulable at any point, the program stops.
    * **Simulation**: If the analysis is successful, it proceeds to simulation. The `src/simulator.py` module runs two scenarios:
        1.  **LO-Mode Scenario**: Simulates normal operation where all jobs complete within their `wcet_lo`.
        2.  **HI-Mode Scenario**: Simulates a critical situation where a HI-criticality job exceeds its `wcet_lo`. This triggers a **criticality switch**, causing the scheduler to drop all LO-criticality jobs to ensure HI-criticality jobs meet their deadlines.

---

##  Prerequisites

* A Debian-based Linux distribution (e.g., Ubuntu) for the `apt-get` commands in `setup.sh`.
* Python 3.8+
* `sudo` privileges for installing system packages.

---

##  Getting Started

To run the complete project from start to finish, follow these steps:

1.  **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd AMC-RTB-Scheduler
    ```

2.  **Run the entire pipeline with a single command:**
    ```sh
    make all
    ```
    This will execute the `setup`, `data`, and `run` targets sequentially.

### Individual Steps

You can also run each step individually:

1.  **Set up the environment:**
    ```sh
    make setup
    ```

2.  **Collect data and generate the task set:**
    ```sh
    make data
    ```

3.  **Run the analysis and simulation on the generated task set:**
    ```sh
    make run
    ```

### Cleaning Up

To remove all generated files, including the virtual environment, MiBench, and data files, run:
```sh
make clean



