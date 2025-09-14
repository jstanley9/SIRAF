import struct
from typing import Tuple
from checksum import calc_16bit_checksum
from enum import IntEnum

class BlockType(IntEnum):      ## limited to 1 byte (0 - 128) value is an ascii letter
    AVAILABLE = 65             ## 0X41 ascii A
    DATA_BLOCK = 68            ## 0X44 ascii D
    META_BLOCK = 77            ## 0X4D ascii M

class HeadBlock:
    # A normal block layout is:
    #   1 byte - block_type: See Block_Type enumeration above
    #   4 bytes - record_size: Total number of bytes required by the data, heading, ending, and any padding
    #   4 bytes - data_length: actual length of the data
    #                          alias: next_avail for AVAILABLE
    #   4 bytes - padding: Number of extra bytes at the end. 
    #                      Allows for some growth and eliminates AVAILABLE blocks that are smaller than MinBlockSize
    #                      alias: prev_avail for AVAILABLE
    #   2 bytes - checksum:
    #
    # When reading blocks we always know what type is being read. Checks are made to ensure that the expected type
    # is at the location being read
    __STRUCT_MASK = ">BIIIH"

    def __init__(self, block_type: BlockType, data_length: int, record_size: int, padding: int, checksum: int):
        self.block_type = block_type
        self.record_size = record_size
        if self.isAvailable():
            self.next_available = data_length
            self.prev_available = padding
        else:
            self.data_length = data_length
            self.padding = padding

        if checksum != 0:
            calc_checksum = self.__getChecksum()
            if checksum != calc_checksum:
               raise ValueError(f"HeadBlock checksum ({checksum}) does not match calculated checksum ({calc_checksum})")

    @property
    def next_available(self):
        return self.data_length
    
    @property
    def prev_available(self):
        return self.padding
    
    @next_available.setter
    def next_available(self, next_available):
        self.data_length = next_available

    @prev_available.setter
    def prev_available(self, prev_available):
        self.padding = prev_available

    def isAvailable(self):
        return self.block_type == BlockType.AVAILABLE

    def __calcRecordSize(self, data_length: int, record_size: int = 0):
        minRequiredLength = CalcMinBlockSize() + data_length
        if record_size < minRequiredLength:
            record_size = minRequiredLength
        
        return record_size, record_size - minRequiredLength
    

    def __getChecksum(self):
        return calc_16bit_checksum([self.block_type.value, self.data_length, self.record_size, self.padding])


    def encode(self) -> bytearray:
        match self.block_type:
            case BlockType.AVAILABLE:
                # Format: B I I I H (1 byte, 4 bytes, 4 bytes, 4 bytes, 2 bytes)
                return bytearray(struct.pack(self.__STRUCT_MASK,    
                                            self.block_type, self.record_size, self.next_avail, self.prev_avail, 
                                            self.__getChecksum()))
            case BlockType.META_BLOCK | BlockType.DATA_BLOCK:                 
                # Format: B I I I H (1 byte, 4 bytes, 4 bytes, 4 bytes, 2 bytes)
                return bytearray(struct.pack(self.__STRUCT_MASK,    
                                            self.block_type, self.record_size, self.data_length, self.padding, 
                                            self.__getChecksum()))
            case _:
                raise ValueError(f"Invalid block type: {self.block_type}:{self.block_type.value}")

    @classmethod
    def decode(cls, data: bytearray):
        block_type = BlockType(data[0])
        match block_type:
            case BlockType.AVAILABLE:
                _, record_size, next_available, prev_available, checksum = struct.unpack(cls.__STRUCT_MASK, data)
                return cls(block_type, next_available, record_size, prev_available, checksum)
            case BlockType.META_BLOCK | BlockType.DATA_BLOCK:
                _, record_size, data_length, padding, checksum = struct.unpack(cls.__STRUCT_MASK, data)
                return cls(block_type, data_length, record_size, padding, checksum)
            case _:
                raise ValueError(f"Invalid block type: {block_type}:{block_type.value}")

    @classmethod
    def getStorageSize(cls):
        return struct.calcsize(cls.__STRUCT_MASK)
    
class EndBlock:
    # An EndBlock is always present at the end of a block. It contains only a checksum of the HeadBlock
    __STRUCT_MASK = ">IB"

    def __init__(self, record_size: int, block_type: BlockType):
        self.record_size = record_size
        self.block_type = block_type

    def encode(self) -> bytearray:
        return bytearray(struct.pack(self.__STRUCT_MASK, self.record_size, self.block_type.value))

    @classmethod
    def decode(cls, data: bytearray):
        block_type = BlockType(data[len(data) - 1])
        record_size, _ = struct.unpack(cls.__STRUCT_MASK, data)
        return cls(record_size, block_type)
    
    @classmethod
    def getStorageSize(cls):
        return struct.calcsize(cls.__STRUCT_MASK)    
    

def CalcMinBlockSize() -> int:
    return HeadBlock.getStorageSize() + EndBlock.getStorageSize()    