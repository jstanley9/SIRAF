from pathlib import Path
import struct
import sys

srcPath = f"{Path.cwd()}/../../src/ravrf"
sys.path.append(srcPath)
print(f"Path = {srcPath}")
import blockDescriptor

def test_getHeadStorageSize():
    assert blockDescriptor.HeadBlock.getStorageSize() == 7

def test_emptyHeadBlock():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 0x11223344, 234)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x40\x11\x22\x33\x44\x00\xea')

def test_avail_1byte():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_01_BYTE, 1, 0)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x01')

def test_avail_1byte_available():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 1, 0)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x01')    

def test_avail_2byte():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_02_BYTE, 2, 0)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x02\x02')

def test_avail_2byte_available():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 2, 0)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x02\x02')    

def test_avail_3byte():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_03_BYTE, 3, 0)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x03\x03\x03')

def test_avail_3byte_available():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 3, 0)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x03\x03\x03')    

def test_avail_6byte():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_06_BYTE, 6, 0)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x06\x06\x06\x06\x06\x06')

def test_avail_6byte_available():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 6, 0)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x06\x06\x06\x06\x06\x06')

def test_avail_7byte():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_07_BYTE, 7, 0)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x07\x07\x07\x07\x07\x07\x07')

def test_avail_7byte_available():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 7, 0)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x07\x07\x07\x07\x07\x07\x07')

def test_avail_8byte():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_08_BYTE, 8, 0)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x08\x08\x08\x08\x08\x08\x08\x08')

def test_avail_8byte_available():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 8, 0)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x08\x08\x08\x08\x08\x08\x08\x08')

def test_avail_12byte():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_12_BYTE, 12, 0)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c')

def test_avail_12byte_available():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 12, 0)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c')

def test_avail_13byte_available():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 13, 77)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x40\x00\x00\x00\x0d\x00\x4d')

def test_meta_1byte():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.META_BLOCK, 1, 66)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x41\x00\x00\x00\x01\x00\x42')

def test_meta_496byte():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.META_BLOCK, 496, 306)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x41\x00\x00\x01\xf0\x01\x32')

def test_data_1byte():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.DATA_BLOCK, 1, 67)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x42\x00\x00\x00\x01\x00\x43')

def test_data_496byte():
    head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.DATA_BLOCK, 496, 307)
    print(f"HeadBlock: {head}")
    assert head.encode() == bytearray(b'\x42\x00\x00\x01\xf0\x01\x33')

def main():
    print("Running tests for blockDescriptor")  
    test_getHeadStorageSize()
    test_emptyHeadBlock()

if __name__ == "__main__":
    main()        