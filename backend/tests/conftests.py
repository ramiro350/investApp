import pytest
import os
import sys
from pathlib import Path

# Add the root directory to Python path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Set environment variables for testing
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment"""
    yield