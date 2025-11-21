import sys
import os

# Add the project's root directory to the Python path.
# This allows the tests to import the 'app' module correctly.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
