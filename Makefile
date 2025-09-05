# Define the Python interpreter from the virtual environment
VENV_PYTHON = venv/bin/python

.PHONY: all setup data run clean

# Default target: runs the full project pipeline from start to finish
all: setup data run

# Target to set up the environment
setup: venv
	@echo "✅ Setup complete. Virtual environment is ready."
	@echo "   You can now run 'make data' to collect performance metrics."

# Target to collect data and generate the task set
data: venv wcet_data.json
	@echo "--------------------------------------------------"
	@echo "⚙️  Generating task set from WCET data..."
	$(VENV_PYTHON) generate_taskset.py
	@echo "✅ Task set generated and saved to task_set.json."
	@echo "   You can now run 'make run' to perform the analysis."

# Target to run the main analysis and simulation
run: venv task_set.json
	@echo "--------------------------------------------------"
	@echo "🚀 Running AMC-RTB analysis and simulation..."
	$(VENV_PYTHON) main.py
	@echo "✅ Analysis and simulation complete."

# Helper target to create the virtual environment and install dependencies
venv: requirements.txt setup.sh
	@if [ ! -d "venv" ]; then \
		echo "⚙️  Running initial system setup (may require sudo password)..."; \
		bash setup.sh; \
		echo "🐍 Creating Python virtual environment..."; \
		python3 -m venv venv; \
		echo "🐍 Installing Python dependencies..."; \
		venv/bin/pip install -r requirements.txt; \
	fi

# Helper target to collect WCET data from MiBench
wcet_data.json: collect_wcet.py venv MiBench/
	@echo "--------------------------------------------------"
	@echo "📊 Collecting WCET data from MiBench benchmarks..."
	@echo "   This may take a few minutes."
	$(VENV_PYTHON) collect_wcet.py

# Target to clean up all generated files
clean:
	@echo "🧹 Cleaning up generated files..."
	rm -rf venv MiBench/ perf_raw.csv wcet_data.json task_set.json
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "✅ Cleanup complete."

# Dependency for venv target to ensure MiBench is cloned
MiBench/:
	git clone https://github.com/vanhauser-thc/MiBench.git

