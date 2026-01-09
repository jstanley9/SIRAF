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

    def __init__(self, block_type: BlockType, record_size: int, prev_or_data: int, 
                 next_or_padding: int, checksum: int):
        self.block_type = block_type
        self.record_size = record_size
        self.__next_or_open_size = next_or_padding
        self.__prev_or_data_size = prev_or_data

        if checksum != 0:
            calc_checksum = self.__getChecksum()
            if checksum != calc_checksum:
               raise ValueError(f"HeadBlock checksum ({checksum}) does not match calculated checksum ({calc_checksum})")

    
    @classmethod
    def initAvailable(cls, record_size: int, prev_available: int, next_avail: int, checksum: int):
        return cls(BlockType.AVAILABLE, record_size, prev_available, next_avail, checksum)
    

    @classmethod
    def initMeta(cls, record_size: int, data_size: int, open_size: int, checksum: int):
        return cls(BlockType.META_BLOCK, record_size, data_size, open_size, checksum)
    

    @classmethod
    def initData(cls, record_size: int, data_size: int, open_size: int, checksum: int):
        return cls(BlockType.DATA_BLOCK, record_size, data_size, open_size, checksum)
    

    @property
    def next_available(self):
        return self.__next_or_open_size
    

    @property
    def prev_available(self):
        return self.__prev_or_data_size
    

    @next_available.setter
    def next_available(self, next_available):
        self.__next_or_open_size = next_available


    @prev_available.setter
    def prev_available(self, prev_available):
        self.__prev_or_data_size = prev_available


    @property
    def data_size(self):
        return self.__prev_or_data_size


    @property
    def open_size(self):
        return self.__next_or_open_size


    @data_size.setter
    def data_size(self, data_size):
        self.__prev_or_data_size = data_size


    @open_size.setter
    def open_size(self, open_size):
        self.__prev_or_data_size = open_size


    def isAvailable(self):
        return self.block_type == BlockType.AVAILABLE

    
    def __calcRecordSize(self, data_length: int, record_size: int = 0):
        minRequiredLength = CalcMinBlockSize() + data_length
        if record_size < minRequiredLength:
            record_size = minRequiredLength
        
        return record_size, record_size - minRequiredLength
    

    def __getChecksum(self):
        return calc_16bit_checksum([self.block_type.value, self.record_size, 
                                    self.__prev_or_data_size, self.__next_or_open_size])


    def encode(self) -> bytes:
        # Format: B I I I H (1 byte, 4 bytes, 4 bytes, 4 bytes, 2 bytes)
        return bytes(struct.pack(self.__STRUCT_MASK,    
                                     self.block_type, self.record_size, 
                                     self.__prev_or_data_size, self.__next_or_open_size, 
                                     self.__getChecksum()))

    @classmethod
    def decode(cls, data: bytes):
        block_type = BlockType(data[0])
        _, record_size, prev_available, next_available, checksum = struct.unpack(cls.__STRUCT_MASK, data)
        return cls(block_type, record_size, prev_available, next_available, checksum)


    @classmethod
    def getStorageSize(cls):
        return struct.calcsize(cls.__STRUCT_MASK)
    
class EndBlock:
    # An EndBlock is always present at the end of a block. It contains only a checksum of the HeadBlock
    __STRUCT_MASK = ">IB"

    def __init__(self, record_size: int, block_type: BlockType):
        self.record_size = record_size
        self.block_type = block_type

    def encode(self) -> bytes:
        return bytes(struct.pack(self.__STRUCT_MASK, self.record_size, self.block_type.value))

    @classmethod
    def decode(cls, data: bytes):
        block_type = BlockType(data[-1])
        record_size, _ = struct.unpack(cls.__STRUCT_MASK, data)
        return cls(record_size, block_type)
    
    @classmethod
    def getStorageSize(cls):
        return struct.calcsize(cls.__STRUCT_MASK)    
    

def CalcMinBlockSize() -> int:
    return HeadBlock.getStorageSize() + EndBlock.getStorageSize()
