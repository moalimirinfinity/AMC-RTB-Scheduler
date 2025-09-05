#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Updating package lists..."
sudo apt-get update -y

echo "Installing required system packages..."
sudo apt-get install -y git build-essential python3-venv python3-pip linux-tools-common linux-tools-$(uname -r)

# Check if mibench directory already exists
if [ ! -d "mibench" ]; then
  echo "Cloning mibench repository..."
  git clone https://github.com/embecosm/mibench.git
else
  echo "mibench repository already exists. Skipping clone."
fi

echo "System setup is complete."

