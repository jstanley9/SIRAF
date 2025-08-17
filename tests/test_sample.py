from pathlib import Path
import sys

print(f"Current path {Path.cwd()}")
srcPath = f"{Path.cwd()}/../src"
sys.path.append(srcPath)
from sample import funcx

def test_answer():
    assert funcx(3) == 4

def test_from_zero():
    assert funcx(0) == 1

def test_from_negative():
    assert funcx(-2) == -1