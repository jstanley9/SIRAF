from pathlib import Path
import sys

print(f"Current path {Path.cwd()}")
srcPath = f"{Path.cwd()}/../src"
sys.path.append(srcPath)
import sample

def test_answer():
    assert sample.funcx(3) == 4

def test_from_zero():
    assert sample.funcx(0) == 1

def test_from_negative():
    assert sample.funcx(-2) == -1