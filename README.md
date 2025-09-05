# AMC-RTB Scheduler — Analysis & Simulation
**Author:** Elite  
**Project:** Embedded Systems — AMC-RTB Scheduler Analysis and Simulation  
**Format:** End-to-end pipeline (data collection → analysis → simulation)

---

## Overview

This repository implements a complete workflow for the AMC-RTB (Adaptive Mixed-Criticality — Response Time Bound) scheduler assignment in an embedded systems course.  
It is designed to be reproducible and automated: starting from execution-time measurement (MiBench), producing WCET statistics, synthesising a mixed-criticality periodic task set, carrying out theoretical response-time analysis, and running discrete-event simulations for LO and HI modes.

The README below documents the project layout, the `make` targets, data formats, and implementation notes necessary to reproduce the results on a Ubuntu 20.04+ environment.

---

## Table of contents

- [Prerequisites](#prerequisites)  
- [Quick start](#quick-start)  
- [Make targets (pipeline)](#make-targets-pipeline)  
- [Manual steps (detailed)](#manual-steps-detailed)  
  - [1. Setup environment](#1-setup-environment)  
  - [2. Data collection & WCET](#2-data-collection--wcet)  
  - [3. Task set generation](#3-task-set-generation)  
  - [4. Analysis & simulation](#4-analysis--simulation)  
- [Input / output file formats](#input--output-file-formats)  
- [Project layout](#project-layout)  
- [Reproducibility & determinism notes](#reproducibility--determinism-notes)  
- [Validation & expected outputs](#validation--expected-outputs)  
- [Troubleshooting](#troubleshooting)  
- [License](#license)

---

## Prerequisites

- **OS:** Ubuntu 20.04 or newer  
- **Permissions:** `sudo` access for package installation  
- **System packages:** `git`, `build-essential`, `python3`, `python3-venv`, `python3-pip`, `perf` (Linux `perf` tool).  
- **Disk:** ≥ 10 GB free (MiBench and generated outputs).  
- Recommended: run on a quiescent system when measuring WCET to reduce noise.

---

## Quick start

From the project root, run:

```bash
make
