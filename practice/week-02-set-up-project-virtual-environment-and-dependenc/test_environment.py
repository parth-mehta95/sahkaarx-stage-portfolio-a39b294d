"""
Test script to verify environment setup and dependencies.
"""
import sys

def test_imports():
    import pandas as pd
    import sqlalchemy
    import pytest

    assert pd.__version__ is not None
    assert sqlalchemy.__version__ is not None
    assert pytest.__version__ is not None
    print(f"Python: {sys.version}")
    print(f"pandas: {pd.__version__}")
    print(f"sqlalchemy: {sqlalchemy.__version__}")
    print(f"pytest: {pytest.__version__}")
    print("All core dependencies successfully imported!")

if __name__ == "__main__":
    test_imports()

