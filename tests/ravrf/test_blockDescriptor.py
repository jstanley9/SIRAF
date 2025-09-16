from pathlib import Path
import pytest
import struct
import sys

srcPath = f"{Path.cwd()}/../../src/ravrf"
sys.path.append(srcPath)
print(f"Path = {srcPath}")
import blockDescriptor

def test_getHeadStorageSize():
    assert blockDescriptor.HeadBlock.getStorageSize() == 15

def test_emptyHeadBlock():
    head = blockDescriptor.HeadBlock.initAvailable(0, 0, 0, 65)
    assert head.encode() == bytearray(b'\x41\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x41')

def test_avail_1byte_new():
    head = blockDescriptor.HeadBlock.initAvailable(1, 0, 0, 66)
    assert head.encode() == bytearray(b'\x41\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x42')

def test_avail_1byte_linked():
    head = blockDescriptor.HeadBlock.initAvailable(1, 170, 255, 491)
    assert head.encode() == bytearray(b'\x41\x00\x00\x00\x01\x00\x00\x00\xaa\x00\x00\x00\xff\x01\xeb')

def test_avail_1byte_decode():
    head = blockDescriptor.HeadBlock.initAvailable(1, 170, 255, 491)
    data = head.encode()
    newHead = blockDescriptor.HeadBlock.decode(data)
    assert newHead.encode() == data

def test_invalid_block_type():
    with pytest.raises(ValueError) as excinfo:
        head = blockDescriptor.HeadBlock(blockDescriptor.BlockType(99), 1, 0, 0, 0)
    assert str(excinfo.value) == "99 is not a valid BlockType"    

# def test_avail_2byte():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_02_BYTE, 2, 0)
#     assert head.encode() == bytearray(b'\x02\x02')

# def test_avail_2byte_available():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 2, 0)
#     assert head.encode() == bytearray(b'\x02\x02')    

# def test_avail_2byte_decode():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_02_BYTE, 2, 0)
#     data = head.encode()
#     newHead = blockDescriptor.HeadBlock.decode(data)
#     assert newHead.encode() == data

# def test_avail_3byte():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_03_BYTE, 3, 0)
#     print(f"HeadBlock: {head}")
#     assert head.encode() == bytearray(b'\x03\x03\x03')

# def test_avail_3byte_available():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 3, 0)
#     print(f"HeadBlock: {head}")
#     assert head.encode() == bytearray(b'\x03\x03\x03')    

# def test_avail_3byte_decode():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_03_BYTE, 3, 0)
#     data = head.encode()
#     newHead = blockDescriptor.HeadBlock.decode(data)
#     assert newHead.encode() == data

# def test_avail_6byte():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_06_BYTE, 6, 0)
#     print(f"HeadBlock: {head}")
#     assert head.encode() == bytearray(b'\x06\x06\x06\x06\x06\x06')

# def test_avail_6byte_available():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 6, 0)
#     print(f"HeadBlock: {head}")
#     assert head.encode() == bytearray(b'\x06\x06\x06\x06\x06\x06')

# def test_avail_6byte_decode():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_06_BYTE, 6, 0)
#     data = head.encode()
#     newHead = blockDescriptor.HeadBlock.decode(data)
#     assert newHead.encode() == data

# def test_avail_7byte():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_07_BYTE, 7, 0)
#     print(f"HeadBlock: {head}")
#     assert head.encode() == bytearray(b'\x07\x07\x07\x07\x07\x07\x07')

# def test_avail_7byte_available():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 7, 0)
#     print(f"HeadBlock: {head}")
#     assert head.encode() == bytearray(b'\x07\x07\x07\x07\x07\x07\x07')

# def test_avail_7byte_decode():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_07_BYTE, 7, 0)
#     data = head.encode()
#     newHead = blockDescriptor.HeadBlock.decode(data)
#     assert newHead.encode() == data

# def test_avail_8byte():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_08_BYTE, 8, 0)
#     assert head.encode() == bytearray(b'\x08\x08\x08\x08\x08\x08\x08\x08')

# def test_avail_8byte_available():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 8, 0)
#     assert head.encode() == bytearray(b'\x08\x08\x08\x08\x08\x08\x08\x08')

# def test_avail_8byte_decode():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_08_BYTE, 8, 0)
#     data = head.encode()
#     newHead = blockDescriptor.HeadBlock.decode(data)
#     assert newHead.encode() == data

# def test_avail_12byte():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_12_BYTE, 12, 0)
#     print(f"HeadBlock: {head}")
#     assert head.encode() == bytearray(b'\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c')

# def test_avail_12byte_available():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 12, 0)
#     print(f"HeadBlock: {head}")
#     assert head.encode() == bytearray(b'\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c')

# def test_avail_12byte_decode():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAIL_12_BYTE, 12, 0)
#     data = head.encode()
#     newHead = blockDescriptor.HeadBlock.decode(data)
#     assert newHead.encode() == data

# def test_avail_13byte_available():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 13, 77)
#     print(f"HeadBlock: {head}")
#     assert head.encode() == bytearray(b'\x40\x00\x00\x00\x0d\x00\x4d')

# def test_avail_13byte_decode():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.AVAILABLE, 13, 77)
#     data = head.encode()
#     newHead = blockDescriptor.HeadBlock.decode(data)
#     assert newHead.encode() == data

# def test_meta_1byte():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.META_BLOCK, 1, 66)
#     assert head.encode() == bytearray(b'\x41\x00\x00\x00\x01\x00\x42')

# def test_meta_1byte_decode():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.META_BLOCK, 1, 66)
#     data = head.encode()
#     newHead = blockDescriptor.HeadBlock.decode(data)
#     assert newHead.encode() == data

# def test_meta_496byte():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.META_BLOCK, 496, 306)
#     assert head.encode() == bytearray(b'\x41\x00\x00\x01\xf0\x01\x32')

# def test_meta_496byte_decode():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.META_BLOCK, 496, 306)
#     data = head.encode()
#     newHead = blockDescriptor.HeadBlock.decode(data)
#     assert newHead.encode() == data

def test_data_1byte():
    head = blockDescriptor.HeadBlock.initData(1, 1, 0, 70)
    assert head.encode() == bytearray(b'\x44\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x46')

def test_data_1byte_decode():
    head = blockDescriptor.HeadBlock.initData(1, 1, 0, 0)
    data = head.encode()
    newHead = blockDescriptor.HeadBlock.decode(data)
    assert newHead.encode() == data

# def test_data_496byte():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.DATA_BLOCK, 496, 307)
#     assert head.encode() == bytearray(b'\x42\x00\x00\x01\xf0\x01\x33')

# def test_data_496byte_decode():
#     head = blockDescriptor.HeadBlock(blockDescriptor.BlockType.DATA_BLOCK, 496, 307)
#     data = head.encode()
#     newHead = blockDescriptor.HeadBlock.decode(data)
#     assert newHead.encode() == data

# def test_avail_13byte_end():
#     tail = blockDescriptor.EndBlock(13, blockDescriptor.BlockType.AVAILABLE)
#     assert tail.encode() == bytearray(b'\x00\x00\x00\x0d\x40')

# def test_avail_13byte_end_decode():
#     tail = blockDescriptor.EndBlock(13, blockDescriptor.BlockType.AVAILABLE)
#     data = tail.encode()
#     newTail = blockDescriptor.EndBlock.decode(data)
#     assert newTail.encode() == data

def test_meta_1byte_end():
    tail = blockDescriptor.EndBlock(1, blockDescriptor.BlockType.META_BLOCK)
    assert tail.encode() == bytearray(b'\x00\x00\x00\x01\x4d')

def test_meta_1byte_decode_end():
    tail = blockDescriptor.EndBlock(1, blockDescriptor.BlockType.META_BLOCK)
    data = tail.encode()
    newTail = blockDescriptor.EndBlock.decode(data)
    assert newTail.encode() == data

def test_meta_496byte_end():
    tail = blockDescriptor.EndBlock(496, blockDescriptor.BlockType.META_BLOCK)
    assert tail.encode() == bytearray(b'\x00\x00\x01\xf0\x4d')

def test_meta_496byte_decode_end():
    tail = blockDescriptor.EndBlock(496, blockDescriptor.BlockType.META_BLOCK)
    data = tail.encode()
    newTail = blockDescriptor.EndBlock.decode(data)
    assert newTail.encode() == data

def test_data_1byte_end():
    tail = blockDescriptor.EndBlock(1, blockDescriptor.BlockType.DATA_BLOCK)
    assert tail.encode() == bytearray(b'\x00\x00\x00\x01\x44')

def test_data_1byte_decode_end():
    tail = blockDescriptor.EndBlock(1, blockDescriptor.BlockType.DATA_BLOCK)
    data = tail.encode()
    newTail = blockDescriptor.EndBlock.decode(data)
    assert newTail.encode() == data

def test_data_496byte_end():
    tail = blockDescriptor.EndBlock(496, blockDescriptor.BlockType.DATA_BLOCK)
    assert tail.encode() == bytearray(b'\x00\x00\x01\xf0\x44')

def test_data_496byte_decode_end():
    tail = blockDescriptor.EndBlock(496, blockDescriptor.BlockType.DATA_BLOCK)
    data = tail.encode()
    newTail = blockDescriptor.EndBlock.decode(data)
    assert newTail.encode() == data

# def main():
#     print("Running tests for blockDescriptor")  
#     test_getHeadStorageSize()
#     test_emptyHeadBlock()

if __name__ == "__main__":
    main()        