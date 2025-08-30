import struct
from typing import Tuple
from checksum import calc_16bit_checksum
from enum import IntEnum

class BlockType(IntEnum):          # limited to 1 byte (0 - 255)
    AVAIL_01_BYTE = 1           # 1 byte is available. This will remain unavailable until the block just above is freed
    AVAIL_02_BYTE = 2           # These AVAIL_nn_BYTE types are used to indicate small blocks of available space
                                    # that cannot have full HeadBloc, EndBlock, and at lease 1 byte of data.
                                    # When an available block has this type, the entire available space is filled with this nn value
                                    # These blocks are not entered into the available list. They will be recovered when the block above or 
                                    # below them is freed, making it available.
    AVAIL_03_BYTE = 3
    AVAIL_04_BYTE = 4
    AVAIL_05_BYTE = 5
    AVAIL_06_BYTE = 6
    AVAIL_07_BYTE = 7
    AVAIL_08_BYTE = 8
    AVAIL_09_BYTE = 9
    AVAIL_10_BYTE = 10
    AVAIL_11_BYTE = 11
    AVAIL_12_BYTE = 12

    AVAIL_MIN_FULL_FENCE = 13  ## Minimum size for full fence. That includes HeadBlock, EndBlock, and at least 1 byte of data
                               ## NOTE: This may change with Version number changes. See Config.py for versioning
    AVAILABLE = 64             ## 0X40
    META_BLOCK = 65            ## 0X41
    DATA_BLOCK = 66            ## 0X42

class HeadBlock:
    # A normal block layout is 1 byte type, 4 bytes data length, 2 bytes checksum
    # An Available block may not contain AVAIL_MIN_FULL_FENCE BYTES, so a shorter block definition is needed.
    # When the available BlockType value is less than AVAIL_MIN_FULL_FENCE, the value is the size of the available block 
    __STRUCT_MASK = ">BIH"

    def __init__(self, block_type: BlockType, data_length: int, checksum: int = 0):
        self.__block_type = block_type
        self.__data_length = data_length
        calc_checksum = self.__getActualDataLength()  
        
        if calc_checksum:
            calc_checksum = self.__getChecksum()
            if checksum != calc_checksum:
               raise ValueError(f"HeadBlock checksum ({checksum}) does not match calculated checksum ({calc_checksum})")
        
    def __getActualDataLength(self) -> bool:
        match self.__block_type:
            case BlockType.AVAIL_01_BYTE | BlockType.AVAIL_02_BYTE | BlockType.AVAIL_03_BYTE | BlockType.AVAIL_04_BYTE | \
                 BlockType.AVAIL_05_BYTE | BlockType.AVAIL_06_BYTE | BlockType.AVAIL_07_BYTE | BlockType.AVAIL_08_BYTE | \
                 BlockType.AVAIL_09_BYTE | BlockType.AVAIL_10_BYTE | BlockType.AVAIL_11_BYTE | BlockType.AVAIL_12_BYTE:
                self.__data_length = self.__block_type.value
                return False
            case BlockType.AVAIL_MIN_FULL_FENCE:
                self.__block_type = BlockType.AVAILABLE
                self.__data_length = BlockType.AVAIL_MIN_FULL_FENCE.value
                return True
            case BlockType.AVAILABLE: 
                if self.__data_length < BlockType.AVAIL_MIN_FULL_FENCE.value:
                    self.__block_type = BlockType(self.__data_length)
                    return self.__getActualDataLength()
                
                return True
            case BlockType.META_BLOCK | BlockType.DATA_BLOCK:
                return True
            case _:
                raise ValueError(f"Invalid block type: {self.__block_type}")
            

    def __getChecksum(self):
        return calc_16bit_checksum([self.__block_type.value, self.__data_length])


    def encode(self) -> bytearray:
        match self.__block_type:
            case BlockType.AVAIL_01_BYTE | BlockType.AVAIL_02_BYTE | BlockType.AVAIL_03_BYTE | BlockType.AVAIL_04_BYTE | \
                 BlockType.AVAIL_05_BYTE | BlockType.AVAIL_06_BYTE | BlockType.AVAIL_07_BYTE | BlockType.AVAIL_08_BYTE | \
                 BlockType.AVAIL_09_BYTE | BlockType.AVAIL_10_BYTE | BlockType.AVAIL_11_BYTE | BlockType.AVAIL_12_BYTE:
                return bytearray([self.__block_type.value] * self.__block_type)
            case BlockType.AVAIL_MIN_FULL_FENCE:
                raise ValueError("AVAIL_MIN_FULL_FENCE is not a valid block type for encoding")
            case BlockType.AVAILABLE | BlockType.META_BLOCK | BlockType.DATA_BLOCK:                 
                # Format: B I H (1 byte, 4 bytes, 2 bytes)
                return bytearray(struct.pack(self.__STRUCT_MASK,    
                                            self.__block_type, self.__data_length, self.__getChecksum()))
            case _:
                raise ValueError(f"Invalid block type: {self.__block_type}:{self.__block_type.value}")

    @classmethod
    def decode(cls, data: bytearray):
        block_type = BlockType(data[0])
        match block_type:
            case BlockType.AVAIL_01_BYTE | BlockType.AVAIL_02_BYTE | BlockType.AVAIL_03_BYTE | BlockType.AVAIL_04_BYTE | \
                 BlockType.AVAIL_05_BYTE | BlockType.AVAIL_06_BYTE | BlockType.AVAIL_07_BYTE | BlockType.AVAIL_08_BYTE | \
                 BlockType.AVAIL_09_BYTE | BlockType.AVAIL_10_BYTE | BlockType.AVAIL_11_BYTE | BlockType.AVAIL_12_BYTE:
                data_len = block_type.value
                return cls(block_type, data_len, 0)
            case BlockType.AVAIL_MIN_FULL_FENCE:
                raise ValueError("AVAIL_MIN_FULL_FENCE is not a valid block type for decoding")
            case BlockType.AVAILABLE | BlockType.META_BLOCK | BlockType.DATA_BLOCK:
                _, data_length, checksum = struct.unpack(cls.__STRUCT_MASK, data)
                return cls(block_type, data_length, checksum)
            case _:
                raise ValueError(f"Invalid block type: {block_type}:{block_type.value}")

    @classmethod
    def getStorageSize(cls):
        return struct.calcsize(cls.__STRUCT_MASK)
    
class EndBlock:
    # An EndBlock is always present at the end of a block. It contains only a checksum of the HeadBlock
    __STRUCT_MASK = ">IB"

    def __init__(self, data_length: int, block_type: BlockType):
        self.__data_length = data_length
        self.__block_type = block_type

    def encode(self) -> bytearray:
        return bytearray(struct.pack(self.__STRUCT_MASK, self.__data_length, self.__block_type.value))

    @classmethod
    def decode(cls, data: bytearray):
        data_len, block_type = struct.unpack(cls.__STRUCT_MASK, data)
        return cls(data_len, block_type)
    
    @classmethod
    def getStorageSize(cls):
        return struct.calcsize(cls.__STRUCT_MASK)    