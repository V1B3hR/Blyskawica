#!/usr/bin/env python3
"""
Run the adaptive labyrinth simulation for the AiMedRes System
This script runs the multi-agent adaptive simulation
"""

import logging
import sys

from main import run_simulation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    print("=== AiMedRes System - Labyrinth Simulation ===")
    success = run_simulation()
    if success:
        print("✅ Simulation completed successfully!")
        sys.exit(0)
    else:
        print("❌ Simulation failed!")
        sys.exit(1)
