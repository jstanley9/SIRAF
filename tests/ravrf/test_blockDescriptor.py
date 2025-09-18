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


def test_meta_496byte():
    head = blockDescriptor.HeadBlock.initMeta(496, 400, 96, 559)
    assert head.encode() == bytearray(b'\x4d\x00\x00\x01\xf0\x00\x00\x01\x90\x00\x00\x00\x60\x02\x2f')

def test_meta_496byte_decode():
    head = blockDescriptor.HeadBlock.initMeta(496, 400, 96, 559)
    data = head.encode()
    newHead = blockDescriptor.HeadBlock.decode(data)
    assert newHead.encode() == data

def test_data_1byte():
    head = blockDescriptor.HeadBlock.initData(1, 1, 0, 70)
    assert head.encode() == bytearray(b'\x44\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x46')

def test_data_65_000bytes():
    head = blockDescriptor.HeadBlock.initData(65000, 65000, 0, 1038)
    assert head.encode() == bytearray(b'\x44\x00\x00\xfd\xe8\x00\x00\xfd\xe8\x00\x00\x00\x00\x04\x0e')    

def test_data_65Kbyte_decode():
    head = blockDescriptor.HeadBlock.initData(65000, 65000, 0, 0)
    data = head.encode()
    newHead = blockDescriptor.HeadBlock.decode(data)
    assert newHead.encode() == data

def test_data_65_000byte_padd():
    head = blockDescriptor.HeadBlock.initData(65000, 0, 65000, 1038)
    assert head.encode() == bytearray(b'\x44\x00\x00\xfd\xe8\x00\x00\x00\x00\x00\x00\xfd\xe8\x04\x0e')    

def test_data_65Kbyte_pad_decode():
    head = blockDescriptor.HeadBlock.initData(65000, 0, 65000, 0)
    data = head.encode()
    newHead = blockDescriptor.HeadBlock.decode(data)
    assert newHead.encode() == data

def test_data_65_000both():
    head = blockDescriptor.HeadBlock.initData(65000, 65000, 65000, 1523)
    assert head.encode() == bytearray(b'\x44\x00\x00\xfd\xe8\x00\x00\xfd\xe8\x00\x00\xfd\xe8\x05\xf3')    

def test_data_65Kboth_decode():
    head = blockDescriptor.HeadBlock.initData(65000, 65000, 65000, 0)
    data = head.encode()
    newHead = blockDescriptor.HeadBlock.decode(data)
    assert newHead.encode() == data

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

def main():
    print("Running tests for blockDescriptor")  
    test_getHeadStorageSize()
    test_emptyHeadBlock()

if __name__ == "__main__":
    main()        