from pathlib import Path
import struct
import sys

srcPath = f"{Path.cwd()}/../../src/ravrf"
sys.path.append(srcPath)
import checksum
import config

def test_zer0ocalc_16bit_checksum():
    assert checksum.calc_16bit_checksum([0, 0, 0]) == 13

def test_001_calc_16bit_checksum():
    assert checksum.calc_16bit_checksum([0, 0, 1]) == 1

def test_010_calc_16bit_checksum():
    assert checksum.calc_16bit_checksum([0, 1, 0]) == 1

def test_100_calc_16bit_checksum():
    assert checksum.calc_16bit_checksum([1, 0, 0]) == 1

def test_111_calc_16bit_checksum():
    assert checksum.calc_16bit_checksum([1, 1, 1]) == 3

def test_size_calc_16bit_checksum():
    assert checksum.calc_16bit_checksum([129, 185600, 67000]) == 534    