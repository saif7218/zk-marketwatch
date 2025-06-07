"""
PyTest configuration and shared fixtures.
"""

import os
import pytest
from typing import Generator
from pathlib import Path

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def data_dir(project_root: Path) -> Path:
    """Get data directory, create if not exists."""
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir

@pytest.fixture(scope="session")
def raw_data_dir(data_dir: Path) -> Path:
    """Get raw data directory, create if not exists."""
    raw_dir = data_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    return raw_dir

@pytest.fixture(scope="function")
def clean_data_dir(raw_data_dir: Path) -> Generator[Path, None, None]:
    """Provide clean data directory and cleanup after test."""
    # Remove any existing files
    for f in raw_data_dir.glob("*"):
        if f.is_file():
            f.unlink()
            
    yield raw_data_dir
    
    # Cleanup after test
    for f in raw_data_dir.glob("*"):
        if f.is_file():
            f.unlink()
