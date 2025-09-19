from pathlib import Path
import pytest
import sys

srcPath = f"{Path.cwd()}/../../src/ravrf"
sys.path.append(srcPath)
print(f"Path = {srcPath}")
import raFile

