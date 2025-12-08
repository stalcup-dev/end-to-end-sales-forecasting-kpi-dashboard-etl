"""
Pytest configuration for test suite.

This file adds the project root to the Python path so that tests can import
modules from the project.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
